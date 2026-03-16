from fastapi import FastAPI,HTTPException,Depends,Request,Header,status
from pydantic import BaseModel
from typing import List,Optional
#from ai.olama import OllamaAPI
import uvicorn
import hmac
import hashlib
import json
import os
import time
from dotenv import load_dotenv
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

import asyncio
import atexit
import warnings
import sys
from openai import OpenAI
import requests
import aiohttp
import asyncio
from typing import Optional
import json
from jose import jwt,JWTError
from slowapi import Limiter,_rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import timedelta
from typing import Optional
import bcrypt
import base64
from backend.database.core import create_deafault_user_data,remove_free_zapros,check_free_zapros_amount,buy_zaproses,get_amount_of_zaproses,subscribe,set_sub_bac_to_false,is_user_subbed,get_sub_date_end,subscribe_basic,unsub_basic, is_user_subbed_basic,get_last_ref_basic,refil_zap,upadate_last_ref_date,get_me,add_referal,get_user_referal_count
from backend.database.chats_database.chats_core import write_message,get_all_user_messsages,delete_all_messages
from backend.database.state_database.state_core import create_user_state,change_user_state,get_user_state
from backend.database.sale_database.sale_core import cretae_user_sale_table,change_to_sale,does_user_have_sale,give_referal_sub,does_user_have_referal_sub
from backend.database.ai_choose_database.ai_core import get_user_model_name,create_default_user_model_name,change_user_model_name
from backend.database.nano_banana.nano_core import create_default_user_data_nano,minus_one_req_nano,get_user_req_nano,refil_user_amount_nano
from backend.database.long_time_database.long_time_core import default_long_time,update_last_time
from backend.database.jwt_db.jwt_core import safe_first_refresh_token,update_refresh_token,get_user_refresh_token
from backend.auth import create_access_token,create_refresh_token
from datetime import datetime
from urllib.parse import parse_qsl

load_dotenv()


app = FastAPI()
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)
#app.add_middleware(HTTPSRedirectMiddleware)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

######## SECURITY ######## 




######## ROUTES ######## 

@app.get("/")
async def main():
    return "NEUROHUB API"




def verify_telegram_init_data(init_data: str) -> dict:
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise RuntimeError("BOT_TOKEN not set")

    parsed_data = dict(parse_qsl(init_data, strict_parsing=True))

    received_hash = parsed_data.pop("hash", None)
    if not received_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Telegram hash"
        )

    auth_date = parsed_data.get("auth_date")
    if not auth_date:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing auth_date"
        )


    if time.time() - int(auth_date) > 300:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="initData is too old"
        )

    data_check_string = "\n".join(
        f"{key}={value}"
        for key, value in sorted(parsed_data.items())
    )

    secret_key = hmac.new(
        key=b"WebAppData",
        msg=bot_token.encode(),
        digestmod=hashlib.sha256
    ).digest()

    calculated_hash = hmac.new(
        key=secret_key,
        msg=data_check_string.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(calculated_hash, received_hash) and os.getenv("DEV_MODE") != "true":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Telegram signature"
        )

    return parsed_data

class TelegrammInitData(BaseModel):
    init_data:str


#эта функция должна вызываться каждый раз когда пользователь открывает мини приложение
@limiter.limit("20/minute")
@app.post("/auth/telegram")
async def default_data_api(request:Request,req:TelegrammInitData):
    
    validated_data = verify_telegram_init_data(req.init_data)

    raw_user = validated_data.get("user")
    if not raw_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Telegram user not found"
        )

    tg_user = json.loads(raw_user)
    telegram_id = str(tg_user["id"])
    username = tg_user.get("username")
    first_name = tg_user.get("first_name")
    
    try:
        await default_long_time(telegram_id)
        await create_deafault_user_data(telegram_id)
        await create_user_state(telegram_id)
        await cretae_user_sale_table(telegram_id)
        await create_default_user_model_name(telegram_id)
        await create_default_user_data_nano(telegram_id,5)

        
        #user_date_now = str(datetime.now().date())
        
        acces_token:str = create_access_token({
            "user_id":telegram_id
        })
        
        refresh_token:str = create_refresh_token({
            "user_id":telegram_id
        })
        
        try_safe:bool = await safe_first_refresh_token(telegram_id,refresh_token)
        
        if not try_safe:
            await update_refresh_token(telegram_id,refresh_token)
        
        return {
            "access_token":acces_token,
            "refresh_token":refresh_token,
            "token_type": "bearer"
        } 
       
    except HTTPException:
        raise     
    except Exception as e:
        print(f"Error : {e}")
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,detail = "Server Error.")
    

async def get_current_user(token: str = Header(..., alias="Authorization")) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        if not token.startswith("Bearer "):
            raise credentials_exception
        
        token = token.replace("Bearer ", "")
        
        payload = jwt.decode(
            token, 
            os.getenv("SECRET_KEY"), 
            algorithms=[os.getenv("ALGORITHM")]
        )
        
        username: str = payload.get("user_id")
        if username is None:
            raise credentials_exception
            
        user_data = {"user_id":username}
        
    
            
        #user_data["username"] = username
        
        return user_data
        
    except jwt.ExpiredSignatureError:
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise credentials_exception



@limiter.limit("20/minute")
@app.post("/remove_request")
async def remove_request_api(request:Request,user_data:dict = Depends(get_current_user)):
    try:
        result:bool = await remove_free_zapros(user_data["user_id"])
        if not result:
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,detail = f"User : {user_data['user_id']} not found.")
    except HTTPException:
        raise     
    except Exception as e:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,detail = "Server Error.")
    

@limiter.limit("20/minute")
@app.post("get/amount/requests")
async def get_amount_of_requests_api(request:Request,user_data:dict = Depends(get_current_user)):
    try:
        result = await get_amount_of_zaproses(user_data["user_id"])
        
        if type(result) == bool:
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,detail = f"User : {user_data["user_id"]} not found")
        
        
        return {
            "result":result
        }
        
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,detail = "Server Error.")


if __name__ == "__main__":
    uvicorn.run(app,host = "0.0.0.0",port = 1488)
    