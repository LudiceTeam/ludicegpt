from sqlalchemy import select,delete,update
from typing import Optional,List 
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from backend.database.chats_database.chats_models import metadata_obj,chats_table


load_dotenv()


async_engine = create_async_engine(
   f"postgresql+psycopg://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@localhost:5432/ai_girl_messages", 
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


async def write_message(username:str,message:str,response:str):
    async with AsyncSession(async_engine) as conn:
        try:
            async with conn.begin():
                stmt = chats_table.insert().values(
                    username = username,
                    id = str(uuid.uuid4()),
                    message = message,
                    response = response
                )
                await conn.execute(stmt)
        except Exception as e:
            raise Exception(f"Error : {e}")
        


async def delete_message(message_id:str):
    async with AsyncSession(async_engine) as conn:
        try:
            async with conn.begin():
                stmt = delete(chats_table).where(chats_table.c.id == message_id)
                await conn.execute(stmt)
        except Exception as e:
            raise  Exception(f"Error : {e}") 


async def get_all_user_messsages(username:str):
    async with AsyncSession(async_engine) as conn:
        try:
            stmt = select(chats_table).where(chats_table.c.username == username)
            res = await conn.execute(stmt)
            data = res.fetchall()
            return data 
        except Exception as e:
            raise  Exception(f"Error : {e}") 
          
async def delete_all_messages(username:str):
    async with AsyncSession(async_engine) as conn:
        try:
            async with conn.begin():
                stmt = delete(chats_table).where(chats_table.c.username == username)
                await conn.execute(stmt)
        except Exception as e:
            return Exception(f"Error : {e}")                    
