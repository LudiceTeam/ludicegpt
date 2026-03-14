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