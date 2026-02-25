from sqlalchemy import text,select,and_
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from datetime import datetime,timedelta
from typing import List
from sqlalchemy.orm import sessionmaker
import asyncpg
import os
from dotenv import load_dotenv
from ai_models import metadata_obj,ai_table
import asyncio
import atexit

#backend.database.ai_choose_database.


load_dotenv()


async_engine = create_async_engine(
    f"postgresql+asyncpg://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@localhost:5432/ai_choose",
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
            stmt = select(ai_table)
            res = await conn.execute(stmt)
            return res.fetchall()
        except Exception as e:
            raise Exception(f"Error : {e}")  

async def is_user_exists(username:str)  -> bool:
    async with AsyncSession(async_engine) as conn:
        try:
            stmt = select(ai_table.c.username).where(ai_table.c.username == username)
            res = await conn.execute(stmt)
            data = res.scalar_one_or_none()
            return data is not None 
        except Exception as e:
            raise Exception(f"Error : {e}") 

async def create_default_user_model_name(username:str):
    if await is_user_exists(username):
        return 
    async with AsyncSession(async_engine) as conn:
        async with conn.begin():
            try:
                stmt = ai_table.insert().values(
                    username = username,
                    ai_name = "google/gemini-3-flash-preview"
                )
                await conn.execute(stmt)
            except Exception as e:
                raise Exception(f"Error : {e}")       


async def get_user_model_name(username:str) -> str:
    if not await is_user_exists(username):
        return ""
    async with AsyncSession(async_engine) as conn:
        try:
            stmt = select(ai_table.c.ai_name).where(ai_table.c.username == username)
            res = await conn.execute(stmt)
            data = res.scalar_one_or_none()
            return str(data) if data is not None else ""
        except Exception as e:
            raise Exception(f"Error : {e}")             



async def change_user_model_name(username:str,new_ai_name:str):
    if not await is_user_exists(username):
        return
    async with AsyncSession(async_engine) as conn:
        async with conn.begin():
            try:
                stmt = ai_table.update().where(ai_table.c.username == username).values(
                    ai_name = new_ai_name
                )
                await conn.execute(stmt)
            except Exception as e:
                raise Exception(f"Error : {e}")    
        