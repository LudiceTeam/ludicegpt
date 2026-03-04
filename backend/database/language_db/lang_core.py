from sqlalchemy import text,select,and_,exc
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from datetime import datetime,timedelta
from typing import List
from sqlalchemy.orm import sessionmaker
import asyncpg
import os
from dotenv import load_dotenv
from backend.database.language_db.lang_models import metadata_obj,language_table
import asyncio
import atexit





load_dotenv()


async_engine = create_async_engine(
    f"postgresql+asyncpg://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@localhost:5432/gpt_language",
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
            stmt = select(language_table)
            res = await conn.execute(stmt)
            return res.fetchall()
        except Exception as e:
            raise Exception(f"Error : {e}")  


async def is_user_exists(username:str) -> bool:
   async with AsyncSession(async_engine) as conn:
       stmt = select(language_table.c.username).where(language_table.c.username == username)
       res = await conn.execute(stmt)
       data = res.scalar_one_or_none()
       if data is not None:
           return True
       return False 
   
async def create_user_language(username:str):
    if await is_user_exists(username):
        return
    async with AsyncSession(async_engine) as conn:
        async with conn.begin():
            try:
                stmt = language_table.insert().values(
                    username = username,
                    lang = "ru"
                )
                await conn.execute(stmt)
            except exc.SQLAlchemyError:
                raise exc.SQLAlchemyError("Error while exeuting")        

async def change_user_language(username:str,lang:str):
    async with AsyncSession(async_engine) as conn:
        async with conn.begin():
            try:
                stmt = language_table.update().where(language_table.c.username == username).values(
                    lang = lang 
                )
                await conn.execute(stmt)
            except exc.SQLAlchemyError:
                raise exc.SQLAlchemyError("Error while executing")      

async def get_user_language(username:str) -> bool:
    async with AsyncSession(async_engine) as conn:
        try:
            stmt = select(language_table.c.lang).where(language_table.c.username == username)
            res = await conn.execute(stmt)
            data = res.scalar_one_or_none()
            if data is not None:
                return data
            raise NameError("Not found")
        except exc.SQLAlchemyError:
            raise exc.SQLAlchemyError("Error while executing")

    