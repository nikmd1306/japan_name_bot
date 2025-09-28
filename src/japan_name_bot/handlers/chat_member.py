from __future__ import annotations

from aiogram import Bot, F, Router, types
from aiogram.enums import ParseMode

from japan_name_bot.config import settings
from japan_name_bot.models import NameRequest

router = Router()


@router.chat_member(
    F.new_chat_member.status.in_({"member", "administrator", "creator"})
)
async def on_join(event: types.ChatMemberUpdated, bot: Bot) -> None:
    if settings.CHANNEL_ID is not None:
        if event.chat.id != settings.CHANNEL_ID:
            return
    else:
        desired_username = (settings.CHANNEL_USERNAME or "").lstrip("@").lower()
        actual_username = (event.chat.username or "").lstrip("@").lower()
        if not desired_username or actual_username != desired_username:
            return

    user_id = event.new_chat_member.user.id

    req = (
        await NameRequest.filter(user_id=user_id, delivered=False)
        .order_by("-id")
        .first()
    )
    if not req:
        return

    await bot.send_message(
        chat_id=user_id,
        text=f"<b>Твое имя:</b> {req.katakana}\n\n<b>Romaji:</b> {req.romaji}",
        parse_mode=ParseMode.HTML,
    )
    await bot.send_message(
        chat_id=user_id,
        text="Интересно звучит, не так ли?\n\n"
        "Узнай, как по-японски будет имя твоего друга и скинь ему!",
    )
    req.delivered = True
    await req.save(update_fields=["delivered"])
