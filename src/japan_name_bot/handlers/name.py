from __future__ import annotations

from aiogram import Bot, F, Router, types
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from japan_name_bot.config import settings
from japan_name_bot.models import NameRequest, User
from japan_name_bot.services.name_conversion import convert_name as convert_name_v2
from japan_name_bot.services.subscription import is_user_subscribed

router = Router()


@router.message(F.text, ~F.text.startswith("/"))
async def on_name(message: types.Message, bot: Bot) -> None:
    if not message.from_user or not message.text:
        return
    user_id = message.from_user.id
    input_name = message.text.strip()

    # Validate word count: allow up to 3 words (to support cases like full name)
    words = [w for w in input_name.split() if w]
    if len(words) > 3:
        await message.answer(
            "Хмм, что-то много слов 😅\n\n"
            "Отправь только имя (до 3 слов), пожалуйста 🙏"
        )
        return

    # React with a fire emoji to the valid name message
    try:
        await bot.set_message_reaction(
            chat_id=message.chat.id,
            message_id=message.message_id,
            reaction=[types.ReactionTypeEmoji(emoji="🔥")],
            is_big=True,
        )
    except TelegramBadRequest:
        pass

    katakana, romaji = convert_name_v2(input_name)

    username = message.from_user.username
    user, _ = await User.get_or_create(id=user_id, defaults={"username": username})
    await NameRequest.create(
        user=user,
        input_name=input_name,
        katakana=katakana,
        romaji=romaji,
        provider="offline",
    )

    subscribed = await is_user_subscribed(bot, None, user_id)
    if subscribed:
        await message.answer(
            f"<b>Твое имя:</b> {katakana}\n\n<b>Romaji:</b> {romaji}",
            parse_mode=ParseMode.HTML,
        )
        await message.answer(
            text="Интересно звучит, не так ли?\n\n"
            "Узнай, как по-японски будет имя твоего друга и скинь ему!",
        )
    else:
        # Построим ссылку на канал, если указан username (@channel)
        username = settings.CHANNEL_USERNAME
        url = f"https://t.me/{username.lstrip('@')}" if username else None
        if url:
            kb = InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text="Подписаться", url=url)]]
            )
            await message.answer(
                "Пожалуйста, подпишись на мой канал и я пришлю тебе "
                "результат сразу после подписки ☺️",
                reply_markup=kb,
            )
        else:
            await message.answer(
                "Пожалуйста, подпишись на мой канал и я пришлю тебе "
                "результат сразу после подписки ☺️",
            )
