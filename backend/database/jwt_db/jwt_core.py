from sqlalchemy import select,exc
from backend.database.jwt_db.jwt_models  import refresh_table,metadata_obj
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import asyncio



load_dotenv()

async_engine = create_async_engine(
    f"postgresql+asyncpg://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@localhost:5432/jwt_token_db",
    pool_size = 20,
    max_overflow = 50,
    pool_recycle=3600,     
    pool_pre_ping=True,    
    echo=False
)



AsyncSessionLocal = sessionmaker(
    async_engine,
    class_ = AsyncSession,
    expire_on_commit=False
)


async def create_table():
    async with async_engine.begin() as conn:
        await conn.run_sync(metadata_obj.create_all)

        
async def is_user_exists(username:str) -> bool:
   async with AsyncSession(async_engine) as conn:
       stmt = select(refresh_table.c.username).where(refresh_table.c.username == username)
       res = await conn.execute(stmt)
       data = res.scalar_one_or_none()
       if data is not None:
           return True
       return False 

async def safe_first_refresh_token(username:str,token:str) -> bool:
    if await is_user_exists(username):
        return False
    async with AsyncSession(async_engine) as conn:
        async with conn.begin():
            try:
                stmt = refresh_table.insert().values(
                    username = username,
                    token =  token
                )
                await conn.execute(stmt)
                
                return True
            except exc.SQLAlchemyError:
                raise exc.SQLAlchemyError("Error while executing")
            
async def update_refresh_token(username:str,token:str):
    if await is_user_exists(username):
        return
    async with AsyncSession(async_engine) as conn:
        async with conn.begin():
            try:
                stmt = refresh_table.update().where(refresh_table.c.username == username).values(
                    token = token
                )
                await conn.execute(stmt)
            except exc.SQLAlchemyError:
                raise exc.SQLAlchemyError("Error while executing")
    

async def get_user_refresh_token(username:str) -> str | bool:
    if not await is_user_exists(username):
        return False
    async with AsyncSession(async_engine) as conn:
        try:
            stmt = select(refresh_table.c.token).where(refresh_table.c.username == username)
            res = await conn.execute(stmt)
            data = res.scalar_one_or_none()
            return data if data is not None else False
        except Exception as e:
            raise Exception(f"Error : {e}")
