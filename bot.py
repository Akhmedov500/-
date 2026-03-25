from __future__ import annotations

import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

import config
from database.base import init_db
from utils.logger import setup_logger

from handlers.start import router as start_router
from handlers.navigation import router as navigation_router
from handlers.combat_handler import router as combat_router
from handlers.quest_handler import router as quest_router
from handlers.crafting_handler import router as crafting_router
from handlers.market_handler import router as market_router
from handlers.guild_handler import router as guild_router
from handlers.profile_handler import router as profile_router
from handlers.leaderboard import router as leaderboard_router
from handlers.admin import router as admin_router

logger = setup_logger()


async def main() -> None:
    logger.info("Starting SEA OF SHADOWS bot...")

    if not config.BOT_TOKEN:
        logger.error("BOT_TOKEN not set. Please set it in .env file.")
        return

    await init_db()
    logger.info("Database initialized.")

    bot = Bot(token=config.BOT_TOKEN, default={"parse_mode": ParseMode.HTML})
    dp = Dispatcher()

    dp.include_router(start_router)
    dp.include_router(navigation_router)
    dp.include_router(combat_router)
    dp.include_router(quest_router)
    dp.include_router(crafting_router)
    dp.include_router(market_router)
    dp.include_router(guild_router)
    dp.include_router(profile_router)
    dp.include_router(leaderboard_router)
    dp.include_router(admin_router)

    logger.info("All routers registered. Polling started.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
