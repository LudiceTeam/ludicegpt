import aiogram
from dotenv import load_dotenv
import os
from aiogram import Bot,Dispatcher
import asyncio
from handlers import router
import sys
from config import PROJECT_ROOT


load_dotenv()

bot = Bot(os.getenv("BOT"))
dp = Dispatcher()



async def main():
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("DONE")