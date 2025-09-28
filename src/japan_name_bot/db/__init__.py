from __future__ import annotations

from typing import Any, Dict

from tortoise import Tortoise

from japan_name_bot.config import settings

TORTOISE_ORM: Dict[str, Any] = {
    "connections": {"default": settings.DATABASE_URL},
    "apps": {
        "models": {
            "models": [
                "japan_name_bot.models",
                "aerich.models",
            ],
            "default_connection": "default",
        }
    },
}


async def init_db() -> None:
    await Tortoise.init(config=TORTOISE_ORM)


async def close_db() -> None:
    await Tortoise.close_connections()
