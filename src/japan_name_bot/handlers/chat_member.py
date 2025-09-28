from __future__ import annotations

from aiogram import Bot, F, Router, types

from japan_name_bot.models import NameRequest

router = Router()


@router.chat_member(
    F.new_chat_member.status.in_({"member", "administrator", "creator"})
)
async def on_join(event: types.ChatMemberUpdated, bot: Bot) -> None:
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
        text=f"Ваше имя: {req.katakana}\nRomaji: {req.romaji}",
    )
    req.delivered = True
    await req.save(update_fields=["delivered"])
