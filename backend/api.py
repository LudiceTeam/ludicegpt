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
from database.core import create_deafault_user_data,remove_free_zapros,check_free_zapros_amount,buy_zaproses,get_amount_of_zaproses,subscribe,set_sub_bac_to_false,is_user_subbed,get_sub_date_end,subscribe_basic,unsub_basic, is_user_subbed_basic,get_last_ref_basic,refil_zap,upadate_last_ref_date,get_me,add_referal,get_user_referal_count
from database.chats_database.chats_core import write_message,get_all_user_messsages,delete_all_messages
from database.state_database.state_core import create_user_state,change_user_state,get_user_state
from database.sale_database.sale_core import cretae_user_sale_table,change_to_sale,does_user_have_sale,give_referal_sub,does_user_have_referal_sub
from database.ai_choose_database.ai_core import get_user_model_name,create_default_user_model_name,change_user_model_name
from database.nano_banana.nano_core import create_default_user_data_nano,minus_one_req_nano,get_user_req_nano,refil_user_amount_nano
from database.long_time_database.long_time_core import default_long_time,update_last_time
from database.jwt_db.jwt_core import safe_first_refresh_token,update_refresh_token,get_user_refresh_token
from auth import create_access_token,create_refresh_token
from datetime import datetime

load_dotenv()


app = FastAPI()
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)
#app.add_middleware(HTTPSRedirectMiddleware)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

######## SECURITY ######## 


async def verify_signature(data: dict, rec_signature, x_timestamp: str) -> bool:
   
    if time.time() - int(x_timestamp) > 300:
        return False
    
   
    return await asyncio.to_thread(_sync_verify_signature, data, rec_signature)

def _sync_verify_signature(data: dict, rec_signature: str) -> bool:
   
    KEY = os.getenv("signature")
    data_to_verify = data.copy()
    data_to_verify.pop("signature", None)
    data_str = json.dumps(data_to_verify, sort_keys=True, separators=(',', ':'))
    expected = hmac.new(KEY.encode(), data_str.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(rec_signature, expected)



async def hash_psw(password: str) -> str:
    salt = await asyncio.to_thread(bcrypt.gensalt)
    
    hashed = await asyncio.to_thread(
        bcrypt.hashpw,
        password.encode("utf-8"),
        salt
    )

    return hashed.decode()

async def safe_get(req: Request):
    try:
        api = req.headers.get("X-API-KEY")
        if not api:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        if not await asyncio.to_thread(hmac.compare_digest, api, os.getenv("api")):
            raise HTTPException(status_code=401, detail="Invalid API key")
            
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid api key")

######## ROUTES ######## 

@app.get("/")
async def main():
    return "NEUROHUB API"

class OnlyUsername(BaseModel):
    user_id:str

@limiter.limit("20/minute")
@app.post("/create_default_data")
async def default_data_api(request:Request,req:OnlyUsername,x_signature:str = Header(...),x_timestamp:str = Header(...)):
    if not verify_signature(req.model_dump(),x_signature,x_timestamp):
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN,detail = "Invalid.")
    
    
    try:
        await default_long_time(str(req.user_id))
        await create_deafault_user_data(str(req.user_id))
        await create_user_state(str(req.user_id))
        await cretae_user_sale_table(str(req.user_id))
        await create_default_user_model_name(str(req.user_id))
        await create_default_user_data_nano(str(req.user_id),5)

        
        user_date_now = str(datetime.now().date())
        
        acces_token:str = create_access_token({
            "user_id":req.user_id,
            "date":user_date_now
        })
        
        refresh_token:str = create_refresh_token({
            "user_id":req.user_id
        })
        
        try_safe = await safe_first_refresh_token(req.user_id,refresh_token)
        
        if not try_safe:
            await update_refresh_token(req.user_id,refresh_token)
        
        return {
            "access_token":acces_token,
            "refresh_token":refresh_token
        }    
        
    except Exception as e:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,detail = "Server Error.")
    

@limiter.limit("20/minute")
@app.post("/remove_request")
async def remove_request_api(request:Request,req:OnlyUsername,x_signature:str = Header(...),x_timestamp:str = Header(...)):
    if not verify_signature(req.model_dump(),x_signature,x_timestamp):
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN,detail = "Invalid.")
    
    try:
        result:bool = await remove_free_zapros(req.user_id)
        if not result:
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,detail = f"User : {req.user_id} not found.")
    except Exception as e:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,detail = "Server Error.")
    

    
    