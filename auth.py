from aiogram import Bot
from aiogram.enums import ChatMemberStatus

from config import ADMIN_ID, GROUP_ID


async def is_admin(bot: Bot, user_id: int) -> bool:
    """Админ бота = захардкоженный ADMIN_ID ИЛИ админ/владелец группы GROUP_ID."""
    if user_id == ADMIN_ID:
        return True
    try:
        member = await bot.get_chat_member(GROUP_ID, user_id)
    except Exception:
        return False
    return member.status in (ChatMemberStatus.CREATOR, ChatMemberStatus.ADMINISTRATOR)
