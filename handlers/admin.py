from datetime import datetime, timedelta
import pytz

from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

import database as db
import sheets
from config import ADMIN_ID, GROUP_ID

router = Router()

MOSCOW_TZ = pytz.timezone("Europe/Moscow")

DIFFICULTY_EMOJI = {"easy": "🟢", "medium": "🟡"}
TOPIC_EMOJI = {
    "Два указателя": "👆",
    "Матрицы": "🔢",
    "Хеш-таблицы": "🗂",
    "Префиксная сумма": "➕",
    "Битовые манипуляции": "⚙️",
    "Бинарный поиск": "🔍",
    "Сортировки": "📊",
    "Интервалы": "📏",
    "Связные списки": "🔗",
    "Деревья": "🌳",
    "Стеки и очереди": "📚",
    "Плавающие окна": "🪟",
    "Поиск с возвратом": "↩️",
    "Графы": "🕸",
    "Динамическое программирование": "💡",
}


def _is_admin(message: Message) -> bool:
    return message.from_user.id == ADMIN_ID


def _parse_deadline(arg: str) -> datetime | None:
    """Парсит '3d', '5d' или 'DD.MM.YYYY HH:MM'"""
    now = datetime.now(MOSCOW_TZ)
    if arg.endswith("d") and arg[:-1].isdigit():
        days = int(arg[:-1])
        deadline = now + timedelta(days=days)
        return deadline.replace(hour=23, minute=59, second=0, microsecond=0)
    try:
        naive = datetime.strptime(arg, "%d.%m.%Y %H:%M")
        return MOSCOW_TZ.localize(naive)
    except ValueError:
        return None


def _format_deadline(dt: datetime) -> str:
    return dt.strftime("%d %B %Y, %H:%M МСК")


def _number_emoji(n: int) -> str:
    digits = {
        "0": "0️⃣", "1": "1️⃣", "2": "2️⃣", "3": "3️⃣", "4": "4️⃣",
        "5": "5️⃣", "6": "6️⃣", "7": "7️⃣", "8": "8️⃣", "9": "9️⃣"
    }
    return "".join(digits[d] for d in str(n))


@router.message(Command("next"))
async def cmd_next(message: Message):
    if not _is_admin(message):
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply(
            "Использование:\n"
            "/next 3d — через 3 дня (23:59)\n"
            "/next 08.04.2026 23:59 — конкретная дата"
        )
        return

    active = await db.get_active_task()
    if active:
        await message.reply(
            f"Сейчас активна задача #{active['number']} — {active['title']}.\n"
            "Закрой её сначала или дождись дедлайна."
        )
        return

    deadline = _parse_deadline(args[1])
    if not deadline:
        await message.reply("Не могу распознать дату. Используй: 3d или 08.04.2026 23:59")
        return

    task = await db.get_next_pending_task()
    if not task:
        await message.reply("Все задачи из пула выполнены! 🎉")
        return

    topic_emoji = TOPIC_EMOJI.get(task["topic"], "📌")
    diff_emoji = DIFFICULTY_EMOJI.get(task["difficulty"], "")
    num_emoji = _number_emoji(task["number"])

    text = (
        f"{num_emoji}  <b>{task['title']}</b>  {diff_emoji}\n"
        f"📂 {task['topic']}\n\n"
        f"🔗 {task['url']}\n\n"
        f"⏰ Дедлайн: <b>{_format_deadline(deadline)}</b>"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Решил", callback_data=f"done:{task['id']}")
    ]])

    sent = await message.bot.send_message(
        chat_id=GROUP_ID,
        text=text,
        parse_mode="HTML",
        reply_markup=keyboard
    )

    await db.activate_task(task["id"], deadline, sent.message_id)

    try:
        sheets.add_task_row(task["number"], task["title"], _format_deadline(deadline))
    except Exception:
        pass

    await message.reply(f"✅ Задача #{task['number']} опубликована. Дедлайн: {_format_deadline(deadline)}")


@router.message(Command("strikes"))
async def cmd_strikes(message: Message):
    if not _is_admin(message):
        return

    participants = await db.get_strikes_table()
    if not participants:
        await message.reply("Участников нет.")
        return

    lines = []
    for p in participants:
        name = f"@{p['username']}" if p["username"] else p["first_name"]
        strikes = p["strikes"]
        warn = " ⚠️" if strikes >= 3 else ""
        lines.append(f"{name}: {'🔴' * min(strikes, 3)} {strikes}{warn}")

    await message.reply(
        "📋 <b>Страйки</b>\n\n" + "\n".join(lines),
        parse_mode="HTML"
    )


@router.message(Command("tasks"))
async def cmd_tasks(message: Message):
    if not _is_admin(message):
        return

    tasks = await db.get_all_tasks()
    pending = [t for t in tasks if t["status"] == "pending"]

    if not pending:
        await message.reply("Пул задач пуст 🎉")
        return

    lines = []
    for t in pending[:20]:
        diff = DIFFICULTY_EMOJI.get(t["difficulty"], "")
        lines.append(f"#{t['number']} {diff} {t['title']} ({t['topic']})")

    text = f"📋 <b>Очередь задач</b> (следующие {len(lines)} из {len(pending)}):\n\n"
    text += "\n".join(lines)

    await message.reply(text, parse_mode="HTML")


@router.message(Command("kick"))
async def cmd_kick(message: Message):
    if not _is_admin(message):
        return

    args = message.text.split()
    if len(args) < 2:
        await message.reply("Использование: /kick USER_ID или /kick @username")
        return

    target = args[1].lstrip("@")

    # Пробуем как user_id
    if target.lstrip("-").isdigit():
        user_id = int(target)
    else:
        # Ищем по username в БД
        participants = await db.get_all_participants()
        found = next((p for p in participants if p["username"] and p["username"].lower() == target.lower()), None)
        if not found:
            await message.reply(f"Не нашёл @{target} в базе. Используй числовой USER_ID.")
            return
        user_id = found["user_id"]

    try:
        await message.bot.ban_chat_member(GROUP_ID, user_id)
        await message.reply(f"✅ Кикнул {args[1]}.")
    except Exception as e:
        await message.reply(f"Не удалось кикнуть: {e}")
