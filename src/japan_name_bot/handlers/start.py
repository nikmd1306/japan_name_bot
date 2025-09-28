from __future__ import annotations

from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from japan_name_bot.models import User
from japan_name_bot.states import NameStates

router = Router()


@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext) -> None:
    if not message.from_user:
        return
    user_id = message.from_user.id
    username = message.from_user.username

    await User.get_or_create(id=user_id, defaults={"username": username})

    await message.answer("Пришлите ваше имя")
    await state.set_state(NameStates.waiting_name)
