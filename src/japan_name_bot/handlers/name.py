from __future__ import annotations

from aiogram import Bot, Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from japan_name_bot.config import settings
from japan_name_bot.models import NameRequest, User
from japan_name_bot.services.name_conversion import convert_name as convert_name_v2
from japan_name_bot.services.subscription import is_user_subscribed
from japan_name_bot.states import NameStates

router = Router()


@router.message(StateFilter(NameStates.waiting_name))
async def on_name(message: types.Message, state: FSMContext, bot: Bot) -> None:
    if not message.from_user or not message.text:
        return
    user_id = message.from_user.id
    input_name = message.text.strip()

    katakana, romaji = convert_name_v2(input_name)

    user = await User.get(id=user_id)
    await NameRequest.create(
        user=user,
        input_name=input_name,
        katakana=katakana,
        romaji=romaji,
        provider="offline",
    )

    subscribed = await is_user_subscribed(bot, None, user_id)
    if subscribed:
        await message.answer(f"Ваше имя: {katakana}\nRomaji: {romaji}")
        await state.set_state(NameStates.waiting_name)
    else:
        # Построим ссылку на канал, если указан username (@channel)
        username = settings.CHANNEL_USERNAME
        url = f"https://t.me/{username.lstrip('@')}" if username else None
        if url:
            kb = InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text="Подписаться", url=url)]]
            )
            await message.answer(
                "Пожалуйста, подпишитесь на канал. "
                "Результат придет автоматически после подписки.",
                reply_markup=kb,
            )
        else:
            await message.answer(
                "Пожалуйста, подпишитесь на канал. "
                "Результат придет автоматически после подписки.",
            )
        # оставляем запись как pending (delivered=False)
