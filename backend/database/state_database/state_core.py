from sqlalchemy import select,delete,update,exc
from typing import Optional,List 
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
#from backend.database.state_database.state_models import metadata_obj,state_table
#from chats_models import metadata_obj,chats_table
import asyncio
from state_models import metadata_obj,state_table


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
            stmt = select(state_table)
            res = await conn.execute(stmt)
            return res.fetchall()
        except Exception as e:
            raise Exception(f"Error : {e}")  

async def is_user_exists(username:str) -> bool:
    async with AsyncSession(async_engine) as conn:
        try:
            stmt = select(state_table.c.username).where(state_table.c.username == username)
            res = await conn.execute(stmt)
            data = res.scalar_one_or_none()
            if data is not None:
                return True
            return False
        except exc.SQLAlchemyError:
            raise exc.SQLAlchemyError("Error while executing")        

async def create_user_state(username:str):
    if await is_user_exists(username):
        return
    async with AsyncSession(async_engine) as conn:
        async with conn.begin():
            try:
                stmt = state_table.insert().values(
                    username = username,
                    chat = False
                )
                await conn.execute(stmt)
            except exc.SQLAlchemyError:
                raise exc.SQLAlchemyError("Error while exeuting")        

async def change_user_state(username:str,state:bool):
    async with AsyncSession(async_engine) as conn:
        async with conn.begin():
            try:
                stmt = state_table.update().where(state_table.c.username == username).values(
                    chat = state
                )
                await conn.execute(stmt)
            except exc.SQLAlchemyError:
                raise exc.SQLAlchemyError("Error while executing")      

async def get_user_state(username:str) -> bool:
    async with AsyncSession(async_engine) as conn:
        try:
            stmt = await select(state_table.c.chat).where(state_table.c.username == username)
            res = await conn.execute(stmt)
            data = res.scalar_one_or_none()
            if data is not None:
                return data
            raise NameError("Not found")
        except exc.SQLAlchemyError:
            raise exc.SQLAlchemyError("Error while executing")

async def delete_user_data(username:str):
    async with AsyncSession(async_engine) as conn:
        async with conn.begin():
            try:
                stmt = state_table.delete(state_table).where(state_table.c.username == username)
                await conn.execute(stmt)
            except exc.SQLAlchemyError:
                raise exc.SQLAlchemyError("Error while executing")        
 