from sqlalchemy import text,select,and_
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from datetime import datetime,timedelta
from typing import List
from sqlalchemy.orm import sessionmaker
import asyncpg
import os
from dotenv import load_dotenv
from database.models import metadata_obj,table
import asyncio
import atexit


load_dotenv()


async_engine = create_async_engine(
    f"postgresql+asyncpg://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@localhost:5432/ai_girl",
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

        
async def is_user_exists(username:str) -> bool:
   async with AsyncSession(async_engine) as conn:
       stmt = select(table.c.username).where(table.c.username == username)
       res = await conn.execute(stmt)
       data = res.scalar_one_or_none()
       if data is not None:
           return True
       return False 

async def create_deafault_user_data(username:str) -> bool:
    if await is_user_exists(username):
        return False
    async with AsyncSession(async_engine) as conn:
        try:
            async with conn.begin():
                    stmt = table.insert().values(
                        username = username,
                        balance = 0,
                        zap = 20,
                        sub = False,
                        date = ""
                    )
                    await conn.execute(stmt)
                    return True
        except Exception as e:
            raise Exception(f"Error : {e}")       

async def remove_free_zapros(username:str) -> bool:
    if not await is_user_exists(username):
        return False 
    async with AsyncSession(async_engine) as conn:
            try:
                async with conn.begin():
                        stmt = select(table.c.zap).where(table.c.username == username)
                        res = await conn.execute(stmt)
                        data = res.scalar_one_or_none()
                        count = int(data) if data is not None else 0
                        if count != 10:
                            count -= 1
                        update_stmt = table.update().where(table.c.username == username).values(zap = count) 
                        await conn.execute(update_stmt)
                        return True   
            except Exception as e:
                raise Exception(f"Error : {e}")       
       
async def check_free_zapros_amount(username:str) -> bool:
    if not await is_user_exists(username):
        return False
    async with AsyncSession(async_engine) as conn:
        try:
            stmt = select(table.c.zap).where(table.c.username == username)
            res = await conn.execute(stmt)
            data = await res.scalar_one_or_none()
            data_res = int(data) if data is not None else 0
            return data_res > 0
        except Exception as e:
            raise Exception(f"Error : {e}")   

async def buy_zaproses(username:str,amount:int) -> bool:
    if not await is_user_exists(username):
        return False
    async with AsyncSession(async_engine) as conn:
        try:
            async with conn.begin():
                stmt = select(table.c.zap).where(table.c.username == username)
                res = await conn.execute(stmt)
                data = await res.scalar_one_or_none()
                data_res = int(data) if data is not None else 0
                update_stmt = table.update().where(table.c.username == username).values(zap = int(data_res) + amount)
                await conn.execute(update_stmt)
                return True
        except Exception as e:
            raise Exception(f"Error : {e}")



async def get_all_data():
    async with AsyncSession(async_engine) as conn:
        try:
            stmt = select(table)
            res = await conn.execute(stmt)
            return res.fetchall()
        except Exception as e:
            raise Exception(f"Error : {e}")  



async def get_amount_of_zaproses(username:str) -> int:
    if not await is_user_exists(username):
        return KeyError("User not found")
    async with AsyncSession(async_engine) as conn:
        try:
            stmt = select(table.c.zap).where(username == username)
            res = await conn.execute(stmt)
            data = res.scalar_one_or_none()
            if data is not None:
                return int(data[0])
        except Exception as e:
            raise  Exception(f"Error : {e}")  
        

async def subscribe(username:str):
    async with AsyncSession(async_engine) as conn:
        try:
            async with conn.begin():
                date_exp = datetime.now().date() + timedelta(days=30)
                stmt = table.update().where(table.c.username == username).values(sub = True,date = str(date_exp))
                await conn.execute(stmt)
        except Exception as e:
            raise Exception(f"Error : {e}")
        

async def set_sub_bac_to_false(username:str):
    async with AsyncSession(async_engine) as conn:
        try:
            async with conn.begin():
                stmt = table.update().where(table.c.username == username).values(sub = False,date = "")
                await conn.execute(stmt)
        except Exception as e:
            raise Exception(f"Error : {e}")
        

async def is_user_subbed(username:str) -> bool:
    if not await is_user_exists(username):
        return False
    async with AsyncSession(async_engine) as conn:
        try:
            stmt = select(table.c.sub).where(table.c.username == username)
            res = await conn.execute(stmt)
            data =  res.scalar_one_or_none()
            if data is not None:
               return bool(data)
            return False
        except Exception as e:
            raise Exception(f"Error : {e}")  


async def get_me(username:str) -> dict:
    async with AsyncSession(async_engine) as conn:
        try:
            stmt = select(table).where(table.c.username == username)
            res = await conn.execute(stmt)
            data =  res.first()
            if data is not None:
                user_data = data
                return {
                    "Username":user_data[0],
                    "Free requests":user_data[2],
                    "Subscribed":user_data[3],
                    "Date of subscribtion to end":user_data[4]
                }
        except Exception as e:
            raise  Exception(f"Error : {e}") 
        

async def unsub_all_users_whos_sub_is_ending_today():           
    async with AsyncSession(async_engine) as conn:
        try:
            stmt = select(table.c.username).where(table.c.date == str(datetime.now().date()))
            #stmt = select(table.c.username)
            res = await conn.execute(stmt)
            data = res.fetchall()
            usernames = []
            for user in data:
                usernames.append(user[0])
            for user in usernames:
                try:
                    await set_sub_bac_to_false(user)
                except Exception as e:
                    raise Exception(f"Error while unsub : {e}")
            return True    
        except Exception as e:
            raise  Exception(f"Error : {e}") 


def cleanup():
    """Очистка при завершении"""
    try:
        # Получаем текущий event loop если он есть
        loop = asyncio.get_event_loop()
        if not loop.is_closed():
            # Запускаем dispose в существующем loop
            loop.run_until_complete(async_engine.dispose())
    except:
        pass   
atexit.register(cleanup)        