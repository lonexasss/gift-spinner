import asyncio
import logging

from aiogram import Bot, Dispatcher

from . import config, db
from .handlers import register as register_handlers

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
log = logging.getLogger("bot")


async def main() -> None:
    if not config.BOT_TOKEN:
        log.error("BOT_TOKEN не задан. Создай .env из .env.example и впиши токен от @BotFather.")
        return

    db.init_db()

    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()
    register_handlers(dp)

    log.info("Bot started. Demo mode: %s", subgram_demo_status())
    await dp.start_polling(bot)


def subgram_demo_status() -> str:
    from .subgram import demo_mode

    return "ON" if demo_mode() else "OFF"


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass