from sqlalchemy import text,select,and_
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from datetime import datetime,timedelta
from typing import List
from sqlalchemy.orm import sessionmaker
import asyncpg
import os
from dotenv import load_dotenv
from nano_models import metadata_obj,nano_table
import asyncio
import atexit
from sqlalchemy import func



load_dotenv()


async_engine = create_async_engine(
    f"postgresql+asyncpg://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@localhost:5432/nano_banano_nanotable",
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

        
async def is_user_exists(username:str) -> bool:
   async with AsyncSession(async_engine) as conn:
       stmt = select(nano_table.c.username).where(nano_table.c.username == username)
       res = await conn.execute(stmt)
       data = res.scalar_one_or_none()
       if data is not None:
           return True
       return False 

async def create_default_user_data(username:str):
    if  await is_user_exists(username):
        return
    async with AsyncSession(async_engine) as conn:
        try:
            async with conn.begin():
                stmt = nano_table.insert().values(
                    username = username,
                    req = 5
                )
                await conn.execute(stmt)
        except Exception as e:
            raise Exception(f"Error : {e}")

async def minus_one_req(username:str):
    if not await is_user_exists(username):
        return
    async with AsyncSession(async_engine) as conn:
        try:
            async with conn.begin():
                stmt = nano_table.update().where(nano_table.c.username == username).values(
                    req = nano_table.c.req - 1
                )
                await conn.execute(stmt)
        except Exception as e:
            raise Exception(f"Error : {e}")

async def get_user_req(username:str) -> int:
    pass


async def refil_user_amount(username:str,amount:int):
    pass        
        

   
   