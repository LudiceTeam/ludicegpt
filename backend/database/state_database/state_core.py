from sqlalchemy import select,delete,update
from typing import Optional,List 
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from backend.database.state_database.state_models import metadata_obj,chats_table
#from chats_models import metadata_obj,chats_table
import asyncio


load_dotenv()


async_engine = create_async_engine(
   f"postgresql+asyncpg://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@localhost:5432/ai_girl_state", 
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

async def create_table():
    async with async_engine.begin() as conn:
        await conn.run_sync(metadata_obj.create_all)


async def get_all_data():
    async with AsyncSession(async_engine) as conn:
        try:
            stmt = select(chats_table)
            res = await conn.execute(stmt)
            return res.fetchall()
        except Exception as e:
            raise Exception(f"Error : {e}")  
