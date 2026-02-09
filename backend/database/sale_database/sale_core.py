from sqlalchemy import text,select,and_
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from datetime import datetime,timedelta
from typing import List
from sqlalchemy.orm import sessionmaker
import asyncpg
import os
from dotenv import load_dotenv
from backend.database.sale_database.sale_models import metadata_obj,sale_table
import asyncio
import atexit
#backend.database.sale_database.



load_dotenv()


async_engine = create_async_engine(
    f"postgresql+asyncpg://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@localhost:5432/gpt_sale",
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
            stmt = select(sale_table)
            res = await conn.execute(stmt)
            return res.fetchall()
        except Exception as e:
            raise Exception(f"Error : {e}")  


async def is_user_exists(username:str) -> bool:
   async with AsyncSession(async_engine) as conn:
       stmt = select(sale_table.c.username).where(sale_table.c.username == username)
       res = await conn.execute(stmt)
       data = res.scalar_one_or_none()
       if data is not None:
           return True
       return False 
   
async def cretae_user_sale_table(username:str):
    if await is_user_exists(username):
        return
    async with AsyncSession(async_engine) as conn:
        async with conn.begin():
            try:
                stmt = sale_table.insert().values(
                    username = username,
                    sale = False,
                    referal_sub = False
                )
                await conn.execute(stmt)
            except Exception as e:
                raise Exception(f"Error {e}")
            
            
            
async def change_to_sale(username:str):
    async with AsyncSession(async_engine) as conn:
        async with conn.begin():
            try:
                stmt = sale_table.update().where(sale_table.c.username == username).values(
                    sale = True
                )
                await conn.execute(stmt)
            except Exception as e:
                raise Exception(f"Error : {e}")  
            
async def does_user_have_sale(username:str) -> bool :
    async with AsyncSession(async_engine) as conn:
        try:
            stmt = select(sale_table.c.sale).where(sale_table.c.username == username)
            res = await conn.execute(stmt)
            data = res.scalar_one_or_none()
            if data is not None:
                return data
            return False
        except Exception as e:
            raise Exception(f"Error : {e}") 
        
        
async def give_referal_sub(username:str):
    async with AsyncSession(async_engine) as conn:
        async with conn.begin():
            try:
                stmt = sale_table.update().where(sale_table.c.username == username).values(
                    referal_sub = True
                )
                await conn.execute(stmt)
            except Exception as e:
                raise Exception(f"Error : {e}")

async def does_user_have_referal_sub(username:str) -> bool:
     async with AsyncSession(async_engine) as conn:
        try:
            stmt = select(sale_table.c.referal_sub).where(sale_table.c.username == username)
            res = await conn.execute(stmt)
            data = res.scalar_one_or_none()
            if data is not None:
                return data
            return False
        except Exception as e:
            raise Exception(f"Error : {e}") 

