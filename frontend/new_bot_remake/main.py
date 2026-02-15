import aiogram
from dotenv import load_dotenv
import os
from aiogram import Bot,Dispatcher
import asyncio
from handlers import router
import sys
from config import PROJECT_ROOT
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from backend.database.long_time_database.long_time_core import all_users_who_needs_to_recieve_message

load_dotenv()

bot = Bot(os.getenv("BOT"))
dp = Dispatcher()
scheduler = AsyncIOScheduler()

async def long_time_havent_seen():
    long_time_text = """👋 Привет!

Ты давно не заходил. Просто решил напомнить о себе.
Хорошего дня! 🌟"""
    users = await all_users_who_needs_to_recieve_message()
    for username in users:
        await bot.send_message(chat_id=int(username),text = long_time_text)

async def main():
    dp.include_router(router)
    scheduler.add_job(
       long_time_havent_seen, 
        'cron', 
        hour=14,  
        minute=0  # ровно
    )
    scheduler.start()
    await dp.start_polling(bot)




if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("DONE")