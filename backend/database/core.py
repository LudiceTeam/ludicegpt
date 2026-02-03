from sqlalchemy import text,select,and_
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from datetime import datetime,timedelta
from typing import List
from sqlalchemy.orm import sessionmaker
import asyncpg
import os
from dotenv import load_dotenv
from backend.database.models import metadata_obj,table
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

async def drop_table():
    async with async_engine.begin() as conn:
        await conn.run_sync(metadata_obj.drop_all)

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
                        date = "",
                        basic_sub = False,
                        last_ref = ""
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
                        if count != 0:
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
            stmt = select(table.c.zap).where(table.c.username == username)
            res = await conn.execute(stmt)
            data = res.scalar_one_or_none()
            if data is not None:
                return int(data)
        except Exception as e:
            raise  Exception(f"Error : {e}")  
        
# premium sub code
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


async def get_sub_date_end(username:str) -> str:
    async with AsyncSession(async_engine) as conn:
        try:
            stmt = select(table.c.date).where(table.c.username == username)
            res = await conn.execute(stmt)
            data = res.scalar_one_or_none()
            if data is not None:
                return data
        except Exception as e:
            raise Exception(f"Error {e}")
        
        
# Basic sub code
        
async def subscribe_basic(username:str):
    async with AsyncSession(async_engine) as conn:
        async with conn.begin():
            try:
                date = datetime.now().date()
                date_exp = datetime.now().date() + timedelta(day = 30)
                stmt = table.update().where(table.c.username == username).values(
                    basic_sub = True,
                    last_res = str(date),
                    zap = 50 ,
                    date = str(date_exp)
                )
                await conn.execute(stmt)
            except Exception as e:
                raise Exception(f"Error : {e}")

async def unsub_basic(username:str):
    async with AsyncSession(async_engine) as conn:
        async with conn.begin():
            try:
                stmt = table.update().whree(table.c.username == username).values(
                    basic_sub = False,
                    last_res = "",
                    date = ""
                )
                await conn.execute(stmt)
            except Exception as e:
                raise Exception(f"Error : {e}")
            
            
async def is_user_subbed_basic(username:str) -> bool:
    async with AsyncSession(async_engine) as conn:
        try:
            stmt = select(table.c.basic_sub).where(table.c.username == username)
            res = await conn.execute(stmt)
            data = res.scalar_one_or_none()
            if data is not None:
                return data
            return False
        except Exception as e:
            raise Exception(f"Error :  {e}")

async def get_last_ref_basic(username:str) -> str:
    async with AsyncSession(async_engine) as conn:
        try:
            stmt = select(table.c.last_ref).where(table.c.username == username)
            res = await conn.execute(stmt)
            data = res.scalar_one_or_none()
            if data is not None:
                return str(data)
        except Exception as e:
            raise Exception(f"Error : {e}")
        
async def refil_zap(username:str):
    if await is_user_subbed_basic(username):
        async with AsyncSession(async_engine) as conn:
            try:
                stmt = table.update().where(table.c.username == username).values(
                    zap = 50
                )
                await conn.execute(stmt)
            except Exception as e:
                raise Exception(f"Error : {e}")
    
async def upadate_last_ref_date(username:str):
    async with AsyncSession(async_engine) as conn:
        async with conn.begin():
            try:
                date_cur = datetime.now().date()
                stmt = table.update().where(table.c.username == username).values(
                    last_ref = str(date_cur)
                )
                await conn.execute(stmt)
            except Exception as e:
                raise Exception(f"Error : {e}")
        
            

async def get_me(username:str) -> dict:
    async with AsyncSession(async_engine) as conn:
        try:
            stmt = select(table).where(table.c.username == username)
            res = await conn.execute(stmt)
            data = res.first()
            
            basic_sub = await is_user_subbed_basic(username)
            if data is not None:
                user_data = data
                return {
                    "Username":user_data[0],
                    "Free requests":user_data[2],
                    "Subscribed":user_data[3],
                    "Basic_sub":basic_sub,
                    "Date of subscribtion to end":user_data[4]
                }
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
 
