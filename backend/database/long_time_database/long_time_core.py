from sqlalchemy import text,select,and_
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from datetime import datetime,timedelta
from typing import List
from sqlalchemy.orm import sessionmaker
import asyncpg
import os
from dotenv import load_dotenv
from backend.database.long_time_database.long_time_models import metadata_obj,main_table
import asyncio
import atexit

#backend.database.long_time_database.

load_dotenv()


async_engine = create_async_engine(
    f"postgresql+asyncpg://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@localhost:5432/long_time",
    pool_size=20,           # Размер пула соединений
    max_overflow=50,        # Максимальное количество соединений
    pool_recycle=3600,      # Пересоздавать соединения каждый час
    pool_pre_ping=True,     # Проверять соединение перед использованием
    echo=False
)




AsyncSessionLocal = sessionmaker(
    async_engine, 
    class_=AsyncSession,
    expire_on_commit=False
)

async def drop_table():
    async with async_engine.begin() as conn:
        await conn.run_sync(metadata_obj.drop_all)

async def create_table():
    async with async_engine.begin() as conn:
        await conn.run_sync(metadata_obj.create_all)

async def get_all_data():
    async with AsyncSession(async_engine) as conn:
        try:
            stmt = select(main_table)
            res = await conn.execute(stmt)
            return res.fetchall()
        except Exception as e:
            raise Exception(f"Error : {e}")  

async def is_user_exists(username:str)  -> bool:
    async with AsyncSession(async_engine) as conn:
        try:
            stmt = select(main_table.c.username).where(main_table.c.username == username)
            res = await conn.execute(stmt)
            data = res.scalar_one_or_none()
            if data is not None:
                return data == username
            return False
        except Exception as e:
            raise Exception(f"Error : {e}")      

async def default_long_time(username:str):
    if await is_user_exists(username):
        return
    async with AsyncSession(async_engine) as conn:
        async with conn.begin():
            date_now = datetime.now().date()
            try:
                stmt = main_table.insert().values(
                    username = username,
                    last_date = date_now
                )
                await conn.execute(stmt)
            except Exception as e:
                raise Exception(f"Error : {e}") 

async def update_last_time(username:str):
    if not await is_user_exists(username):
        await default_long_time(username)
        return
    async with AsyncSession(async_engine) as conn:
        async with conn.begin():
            try:
                date_now = datetime.now().date()
                stmt = main_table.update().where(main_table.c.username == username).values(
                    last_date = date_now
                )
                await conn.execute(stmt)
            except Exception as e:
                raise Exception(f"Error : {e}")  
            

       
async def all_users_who_needs_to_recieve_message() -> List[str]:
    async with AsyncSession(async_engine) as conn:
        try:
            date_now:int = datetime.now().date() - timedelta(days = 7)
            stmt = select(main_table.c.username).where(main_table.c.last_date < date_now)
            res = await conn.execute(stmt)
            date = res.scalars().all()
            return date
        except Exception as e:
            raise Exception(f"Error : {e}")            
                       
