import asyncio
import os
import aiohttp
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv, find_dotenv
from datetime import datetime
from aiogram.client.session.aiohttp import AiohttpSession

load_dotenv(find_dotenv())
TOKEN = os.getenv("TOKEN")

from routers.private_user import start_router, profile_router, chat_router
import routers.private_user as private_user

LOG_FILE = "bot_start_log.txt"
PID_FILE = "bot.pid"

def log_start():
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.utcnow().isoformat()} | bot started\n")


def write_pid():
    with open(PID_FILE, "w", encoding="utf-8") as f:
        f.write(str(os.getpid()))


async def main():
    # Initialize the backend API session
    private_user.backend_session = aiohttp.ClientSession()

    try:
        # Initialize bot with the custom session
        bot_session = AiohttpSession()
        bot = Bot(TOKEN, session=bot_session)

        dp.include_router(start_router)
        dp.include_router(profile_router)
        dp.include_router(chat_router)

        await bot.delete_webhook(drop_pending_updates=True)

        print("✅ Bot started! Waiting for updates...")
        await asyncio.sleep(0.5)
        print("Press Ctrl+C to stop the bot.")
        await asyncio.sleep(1)
        print("Included routers: start_router, game_router, admin_router")

        await dp.start_polling(bot)
    finally:
        # Clean up the session on shutdown
        await private_user.backend_session.close()


if __name__ == "__main__":
    asyncio.run(main())
