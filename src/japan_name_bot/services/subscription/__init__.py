from __future__ import annotations

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest

from japan_name_bot.config import settings


def _resolve_channel() -> str | int | None:
    if settings.CHANNEL_ID is not None:
        return settings.CHANNEL_ID

    if settings.CHANNEL_USERNAME:
        return settings.CHANNEL_USERNAME

    return None


async def is_user_subscribed(bot: Bot, channel: str | int | None, user_id: int) -> bool:
    target = channel if channel is not None else _resolve_channel()
    if target is None:
        return False

    try:
        member = await bot.get_chat_member(chat_id=target, user_id=user_id)
    except TelegramBadRequest:
        return False
    status = getattr(member, "status", None)
    return status in {"member", "administrator", "creator"}
