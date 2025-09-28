from __future__ import annotations

from aiogram import Router, types
from aiogram.filters import CommandStart

from japan_name_bot.models import User

router = Router()


@router.message(CommandStart())
async def cmd_start(message: types.Message) -> None:
    if not message.from_user:
        return
    user_id = message.from_user.id
    username = message.from_user.username

    await User.get_or_create(id=user_id, defaults={"username": username})

    await message.answer("🌸напиши свое имя🌸")
