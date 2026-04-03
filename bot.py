import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from database import init_db, load_tasks_pool
from tasks_pool import TASKS_POOL
from scheduler import setup_scheduler
from handlers import admin, user
import sheets

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    os.makedirs("data", exist_ok=True)

    await init_db()
    await load_tasks_pool(TASKS_POOL)

    try:
        sheets.setup_sheet()
    except Exception as e:
        logger.warning(f"Google Sheets недоступен при старте: {e}")

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    dp.include_router(admin.router)
    dp.include_router(user.router)

    scheduler = setup_scheduler(bot)
    scheduler.start()

    logger.info("LeetRush bot started")

    try:
        await dp.start_polling(bot, allowed_updates=["message", "callback_query"])
    finally:
        scheduler.shutdown()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
