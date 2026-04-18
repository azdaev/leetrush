from datetime import datetime, timedelta
import pytz
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot

import database as db
import sheets
from config import GROUP_ID, ADMIN_ID

MOSCOW_TZ = pytz.timezone("Europe/Moscow")
CHECK_INTERVAL = timedelta(minutes=5)
logger = logging.getLogger(__name__)


def _mention(user_id: int, name: str, username: str | None) -> str:
    if username:
        return f"@{username}"
    return f'<a href="tg://user?id={user_id}">{name}</a>'


async def _send_reminder_24h(bot: Bot, task) -> None:
    await bot.send_message(
        GROUP_ID,
        f"⏰ <b>Напоминание!</b>\n"
        f"До дедлайна задачи #{task['number']} — <b>{task['title']}</b> остался 1 день.\n"
        f"Кто ещё не решил — успейте!",
        parse_mode="HTML",
    )


async def _send_reminder_1h(bot: Bot, task) -> None:
    await bot.send_message(
        GROUP_ID,
        f"🔴 <b>Через час дедлайн!</b>\n"
        f"Задача #{task['number']} — <b>{task['title']}</b>\n"
        f"Последний шанс отметиться ✅",
        parse_mode="HTML",
    )


async def _close_deadline(bot: Bot, task) -> None:
    # Порядок: идемпотентные DB-шаги (страйки, close_task) → отправка сообщений.
    # Если падает send_message — задача уже закрыта и страйки проставлены,
    # теряется только пост в группу. DB-состояние консистентно.
    all_participants = await db.get_all_participants()
    done_ids = set(await db.get_completions(task["id"]))

    done_list = [p for p in all_participants if p["user_id"] in done_ids]
    non_solvers = [p for p in all_participants if p["user_id"] not in done_ids]

    strike_list = []
    three_strikes = []
    for p in non_solvers:
        strike_count = await db.add_strike(p["user_id"], task["id"])
        strike_list.append((p, strike_count))
        try:
            sheets.mark_strike(task["number"], p["sheet_col"])
        except Exception:
            pass
        if strike_count >= 3:
            three_strikes.append((p, strike_count))

    await db.close_task(task["id"])

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

    if three_strikes:
        warn_text = "⚠️ <b>3 страйка у участников:</b>\n\n"
        for p, cnt in three_strikes:
            warn_text += f"• {fmt(p)} — {cnt} страйка\n"
        warn_text += "\nКикнуть: /kick USER_ID"
        await bot.send_message(ADMIN_ID, warn_text, parse_mode="HTML")


HANDLERS = {
    "reminder_24h": _send_reminder_24h,
    "reminder_1h": _send_reminder_1h,
    "close_deadline": _close_deadline,
}


async def schedule_task_jobs(task_id: int, deadline: datetime) -> None:
    """Планирует напоминания и закрытие задачи. Джобы с fire_at в прошлом пропускаются."""
    now = datetime.now(MOSCOW_TZ)
    plan = [
        ("reminder_24h", deadline - timedelta(hours=24)),
        ("reminder_1h", deadline - timedelta(hours=1)),
        ("close_deadline", deadline),
    ]
    for kind, fire_at in plan:
        if fire_at > now:
            await db.schedule_job(task_id, kind, fire_at)


async def run_jobs(bot: Bot) -> None:
    now = datetime.now(MOSCOW_TZ)
    jobs = await db.get_due_jobs(now)
    for job in jobs:
        task = await db.get_task_by_id(job["task_id"])
        # Задача могла быть закрыта вручную — устаревшие джобы молча гасим.
        if not task or task["status"] == "closed":
            await db.mark_job_done(job["id"])
            continue

        handler = HANDLERS.get(job["kind"])
        if handler is None:
            logger.error(f"Unknown job kind: {job['kind']} (job id={job['id']})")
            await db.mark_job_failed(job["id"])
            continue

        logger.info(f"Firing {job['kind']} for task #{task['number']} (job id={job['id']})")
        try:
            await handler(bot, task)
            await db.mark_job_done(job["id"])
        except Exception:
            logger.exception(f"Job {job['id']} ({job['kind']}) failed")
            await db.mark_job_failed(job["id"])


def setup_scheduler(bot: Bot) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone=MOSCOW_TZ)
    scheduler.add_job(
        run_jobs, "interval", seconds=CHECK_INTERVAL.total_seconds(), args=[bot]
    )
    return scheduler
