import asyncio

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from japan_name_bot.config import settings
from japan_name_bot.db import close_db, init_db
from japan_name_bot.handlers import chat_member as chat_member_handlers
from japan_name_bot.handlers import name as name_handlers
from japan_name_bot.handlers import start as start_handlers
from japan_name_bot.utils.logging import setup_logging


async def main() -> None:
    setup_logging()
    bot = Bot(token=settings.BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()

    await init_db()

    dp.include_router(start_handlers.router)
    dp.include_router(name_handlers.router)
    dp.include_router(chat_member_handlers.router)

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(main())
