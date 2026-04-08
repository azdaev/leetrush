from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

import database as db
import sheets

router = Router()


def _mention(user_id: int, name: str, username: str | None) -> str:
    if username:
        return f"@{username}"
    return f'<a href="tg://user?id={user_id}">{name}</a>'


async def _ensure_registered(user_id: int, username: str | None, first_name: str) -> dict:
    """Регистрирует если нет, возвращает participant. Колонку берёт из таблицы."""
    participant = await db.get_participant(user_id)
    if participant:
        return participant

    # Ищем существующую колонку по имени в таблице
    try:
        existing_col = sheets.find_col_by_name(first_name)
    except Exception:
        existing_col = None

    if existing_col is not None:
        sheet_col = existing_col
        create_col = False
    else:
        sheet_col = sheets.get_next_col_index()
        create_col = True

    await db.register_participant(user_id, username, first_name, sheet_col)
    participant = await db.get_participant(user_id)

    if create_col:
        try:
            sheets.add_participant_column(first_name, sheet_col)
        except Exception:
            pass

    return participant


async def _status_text(task: dict) -> str:
    all_participants = await db.get_all_participants()
    done_ids = set(await db.get_completions(task["id"]))

    done = [p for p in all_participants if p["user_id"] in done_ids]
    not_done = [p for p in all_participants if p["user_id"] not in done_ids]

    def fmt(p):
        return p["username"] if p["username"] else p["first_name"]

    text = f"📊 <b>Задача #{task['number']} — {task['title']}</b>\n\n"
    text += f"✅ Решили ({len(done)}/{len(all_participants)}):\n"
    text += ", ".join(fmt(p) for p in done) if done else "—"
    text += f"\n\n❌ Не решили ({len(not_done)}):\n"
    text += ", ".join(fmt(p) for p in not_done) if not_done else "—"
    return text


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.reply(
        "📖 <b>Команды LeetRush</b>\n\n"
        "/start — зарегистрироваться\n"
        "/done &lt;номер&gt; — отметить задачу выполненной\n"
        "/undone &lt;номер&gt; — отменить отметку\n"
        "/status — кто решил текущую задачу\n"
        "/help — это сообщение",
        parse_mode="HTML"
    )


@router.message(Command("start"))
async def cmd_start(message: Message):
    user = message.from_user
    existing = await db.get_participant(user.id)

    if existing:
        await db.register_participant(user.id, user.username, user.first_name, existing["sheet_col"])
        await message.answer("Ты уже зарегистрирован 👍")
        return

    participant = await _ensure_registered(user.id, user.username, user.first_name)
    await message.answer(
        f"✅ Добро пожаловать, {user.first_name}!\n"
        "Ты зарегистрирован в LeetRush.\n\n"
        "Когда решишь задачу — нажми кнопку <b>✅ Решил</b> под постом или напиши /done <номер>.",
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("done:"))
async def callback_done(callback: CallbackQuery):
    task_id = int(callback.data.split(":")[1])
    user = callback.from_user

    task = await db.get_active_task()
    if not task or task["id"] != task_id:
        await callback.answer("Эта задача уже закрыта.", show_alert=True)
        return

    already = await db.has_done(task_id, user.id)
    if already:
        await callback.answer("Ты уже отметился ✅", show_alert=True)
        return

    participant = await _ensure_registered(user.id, user.username, user.first_name)

    await db.mark_done(task_id, user.id)

    try:
        sheets.mark_cell(task["number"], participant["sheet_col"], done=True)
    except Exception:
        pass

    await callback.answer("✅ Отмечено! Молодец!")
    status = await _status_text(task)
    await callback.message.reply(status, parse_mode="HTML")


@router.message(Command("done"))
async def cmd_done(message: Message):
    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        await message.reply("Использование: /done <номер задачи>")
        return

    task_number = int(args[1])
    task = await db.get_task_by_number(task_number)
    if not task:
        await message.reply(f"Задача #{task_number} не найдена.")
        return
    if task["status"] == "pending":
        await message.reply(f"Задача #{task_number} ещё не опубликована.")
        return
    if task["status"] == "closed":
        await message.reply(f"Задача #{task_number} уже закрыта, дедлайн прошёл.")
        return

    user = message.from_user
    already = await db.has_done(task["id"], user.id)
    if already:
        await message.reply(f"Задача #{task_number} уже отмечена ✅")
        return

    participant = await _ensure_registered(user.id, user.username, user.first_name)

    await db.mark_done(task["id"], user.id)
    try:
        sheets.mark_cell(task["number"], participant["sheet_col"], done=True)
    except Exception:
        pass

    task = await db.get_task_by_number(task_number)
    status = await _status_text(task)
    await message.reply(f"✅ Задача #{task_number} отмечена как выполненная!\n\n{status}", parse_mode="HTML")


@router.message(Command("status"))
async def cmd_status(message: Message):
    task = await db.get_active_task()
    if not task:
        await message.reply("Нет активной задачи.")
        return

    await message.reply(await _status_text(task), parse_mode="HTML")


@router.message(Command("undone"))
async def cmd_undone(message: Message):
    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        await message.reply("Использование: /undone <номер задачи>")
        return

    task_number = int(args[1])
    task = await db.get_task_by_number(task_number)
    if not task:
        await message.reply(f"Задача #{task_number} не найдена.")
        return

    user = message.from_user
    participant = await db.get_participant(user.id)
    if not participant:
        await message.reply("Ты не зарегистрирован. Напиши /start.")
        return

    removed = await db.unmark_done(task["id"], user.id)
    if not removed:
        await message.reply(f"Задача #{task_number} не была отмечена.")
        return

    try:
        sheets.mark_cell(task["number"], participant["sheet_col"], done=False)
    except Exception:
        pass

    await message.reply(f"↩️ Отметка по задаче #{task_number} отменена.")
