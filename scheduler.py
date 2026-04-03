from datetime import datetime
import pytz
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot

import database as db
import sheets
from config import GROUP_ID, ADMIN_ID

MOSCOW_TZ = pytz.timezone("Europe/Moscow")
logger = logging.getLogger(__name__)


def _mention(user_id: int, name: str, username: str | None) -> str:
    if username:
        return f"@{username}"
    return f'<a href="tg://user?id={user_id}">{name}</a>'


async def check_reminders(bot: Bot):
    """Проверяет дедлайн и шлёт напоминания за 24ч и 1ч."""
    task = await db.get_active_task()
    if not task or not task["deadline"]:
        return

    deadline = datetime.fromisoformat(task["deadline"])
    if deadline.tzinfo is None:
        deadline = MOSCOW_TZ.localize(deadline)

    now = datetime.now(MOSCOW_TZ)
    delta = deadline - now
    hours_left = delta.total_seconds() / 3600

    if 23.5 <= hours_left <= 24.5:
        await bot.send_message(
            GROUP_ID,
            f"⏰ <b>Напоминание!</b>\n"
            f"До дедлайна задачи #{task['number']} — <b>{task['title']}</b> остался 1 день.\n"
            f"Кто ещё не решил — успейте!",
            parse_mode="HTML"
        )
    elif 0.9 <= hours_left <= 1.1:
        await bot.send_message(
            GROUP_ID,
            f"🔴 <b>Через час дедлайн!</b>\n"
            f"Задача #{task['number']} — <b>{task['title']}</b>\n"
            f"Последний шанс отметиться ✅",
            parse_mode="HTML"
        )


async def process_deadline(bot: Bot):
    """Закрывает задачу после дедлайна: выдаёт страйки, обновляет Sheets, постит итог."""
    task = await db.get_active_task()
    if not task or not task["deadline"]:
        return

    deadline = datetime.fromisoformat(task["deadline"])
    if deadline.tzinfo is None:
        deadline = MOSCOW_TZ.localize(deadline)

    now = datetime.now(MOSCOW_TZ)
    if now < deadline:
        return

    logger.info(f"Closing task #{task['number']}")

    all_participants = await db.get_all_participants()
    done_ids = set(await db.get_completions(task["id"]))

    done_list = []
    strike_list = []
    three_strikes = []

    for p in all_participants:
        user_id = p["user_id"]
        if user_id in done_ids:
            done_list.append(p)
        else:
            strike_count = await db.add_strike(user_id, task["id"])
            strike_list.append((p, strike_count))
            try:
                sheets.mark_strike(task["number"], p["sheet_col"])
            except Exception:
                pass
            if strike_count >= 3:
                three_strikes.append((p, strike_count))

    await db.close_task(task["id"])

    # Итоговый пост в группу
    def fmt(p):
        return _mention(p["user_id"], p["first_name"], p["username"])

    text = f"🏁 <b>Задача #{task['number']} закрыта — {task['title']}</b>\n\n"

    if done_list:
        text += f"✅ Решили ({len(done_list)}):\n"
        text += ", ".join(fmt(p) for p in done_list)
    else:
        text += "✅ Никто не решил 😬"

    if strike_list:
        text += f"\n\n❌ Страйк ({len(strike_list)}):\n"
        text += ", ".join(f"{fmt(p)} ({cnt}🔴)" for p, cnt in strike_list)

    await bot.send_message(GROUP_ID, text, parse_mode="HTML")

    # Уведомление админу о тех у кого 3 страйка
    if three_strikes:
        warn_text = "⚠️ <b>3 страйка у участников:</b>\n\n"
        for p, cnt in three_strikes:
            warn_text += f"• {fmt(p)} — {cnt} страйка\n"
        warn_text += "\nКикнуть: /kick USER_ID"
        await bot.send_message(ADMIN_ID, warn_text, parse_mode="HTML")


def setup_scheduler(bot: Bot) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone=MOSCOW_TZ)

    # Каждый час проверяем напоминания
    scheduler.add_job(check_reminders, "interval", hours=1, args=[bot])

    # Каждые 5 минут проверяем не истёк ли дедлайн
    scheduler.add_job(process_deadline, "interval", minutes=5, args=[bot])

    return scheduler
