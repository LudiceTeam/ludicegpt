from email.mime import message
from unittest import result
from aiogram import F,Router, types
from aiogram.types import LabeledPrice, PreCheckoutQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from dotenv import load_dotenv, find_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.filters import Command
import asyncio
import os
from aiogram.client.session.aiohttp import AiohttpSession
import aiohttp
import json
import hashlib
import hmac
import time
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton,InlineKeyboardMarkup
from dotenv import load_dotenv
from common.start_text import START

load_dotenv()
BASE_URl = "http://0.0.0.0:8080"
BASE_URL_START = "http://0.0.0.0:8080/start"

# Session for Bot's Telegram API requests
bot_session = AiohttpSession()

# Global session for backend API requests (will be initialized in app.py)
backend_session: aiohttp.ClientSession = None

def get_kb_start() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Профиль 👤", callback_data="profile")
        ],
        [
            InlineKeyboardButton(text="Чат 💬", callback_data="chat")
        ]
    ]
        
    )

# Routers
start_router = Router()
profile_router = Router()
chat_router = Router()

@start_router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await message.answer(
        START,
        parse_mode="Markdown",
        reply_markup=get_kb_start()
    )
    # Prepare API request data with signature
    data = {
        "username": str(user_id),
        "timestamp": time.time()
    }
    # Generate signature
    data["signature"] = generate_signature(data)

    try:
        # Register user using the Python backend endpoint
        async with backend_session.post(
            BASE_URL_START,
            json=data,
            headers={"Content-Type": "application/json"}
        ) as response:
            if response.status == 200:
                print("User registered successfully.")
            elif response.status == 404:
                print("Start gone wrong")
            elif response.status == 409:
                print("Error")
    except Exception as e:
        await message.answer(f"Error: {e}")

# @profile_router.callback_query(F.data == "profile")
# async def profile(callback: types.CallbackQuery):
    
@chat_router.callback_query(F.data == "chat")
async def chat(callback: types.CallbackQuery):
    # Prepare API request data with signature
    data = {
    }
    # Generate signature
    data["signature"] = generate_signature(data)
    
    try: 
        # Register user using the Python backend endpoint
        async with backend_session.post(
            BASE_URL_START,
            json=data,
            headers={"Content-Type": "application/json"}
        ) as response:
            if response.status == 200:
                print("User registered successfully.")
            elif response.status == 404:
                print("Start gone wrong")
            elif response.status == 409:
                print("Error")
    except Exception as e:
        await message.answer(f"Error: {e}")