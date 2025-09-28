from __future__ import annotations

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest


async def is_user_subscribed(bot: Bot, channel_id: str | int, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
    except TelegramBadRequest:
        return False
    status = getattr(member, "status", None)
    return status in {"member", "administrator", "creator"}
