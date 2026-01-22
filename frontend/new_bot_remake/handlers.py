from aiogram import Bot,Dispatcher,F,Router
from aiogram.filters import CommandStart,Command
from aiogram.types import Message,File,Video,PhotoSize,LabeledPrice
import aiogram
import keyboards as kb
from backend.database.core import create_deafault_user_data,remove_free_zapros,check_free_zapros_amount,get_amount_of_zaproses,subscribe,set_sub_bac_to_false,get_me,unsub_all_users_whos_sub_is_ending_today,is_user_subbed,buy_zaproses
#from main import bot
from backend.database.chats_database.chats_core import write_message
from backend.api import ask_chat_gpt
import sys
import os
import cv2
import tempfile
import easyocr
import numpy as np


current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir) 

sys.path.insert(0, project_root)

router = Router()

user_chat_flag:bool = False
reader = easyocr.Reader(["en","rus"])

@router.message(CommandStart())
async def start_messsage(message:Message):
    user_name = message.from_user.username
    user_chat_flag = False
    user_id = message.from_user.id
    await create_deafault_user_data(str(user_id))
    await message.answer("Welcome")# вставить сюда норм текст

@router.message(F.text == "Profile")
async def profile_handler(message:Message):
    user_chat_flag = False
    user_name = message.from_user.username
    user_id = message.from_user.id
    user_data = get_me(str(user_id))
    user_data[str(user_id)] = user_name
    user_subbed:bool = await  is_user_subbed(str(user_id))
    if not user_subbed:
        await message.answer(
        user_data,
        reply_markup=kb.profile_key_borad        
        )
    else:
        await message.answer(
        user_data        
    )

@router.message(F.text == "Subscribe")
async def subscribe_handler(message:Message):
    user_id = message.from_user.id
    user_chat_flag = False
    buy_sub_text = "" # вставить норм текст для подписки
    await message.answer(buy_sub_text,reply_markup=kb.buy_sub_keyboard)



#сделать  норм invoice
@router.message(F.text == "Buy subscribtion")
async def buy_sub_handler(message:Message):
    await message.bot.send_invoice(
        chat_id=message.chat.id,
        title="Название товара",
        description="Описание товара",
        payload="test_payload", 
        provider_token="YOUR_PROVIDER_TOKEN", 
        currency="RUB",
        prices=[
            LabeledPrice(label="Товар 1", amount=10000),  # 100.00 RUB
            LabeledPrice(label="Скидка", amount=-2000),   # -20.00 RUB
        ],
        start_parameter="test",
        need_email=True, 
        need_phone_number=False,
        is_flexible=False, 
    )

@router.message("Chat")
async def chat_handler(message:Message):
    global user_chat_flag
    user_chat_flag = True  
    await message.answer("Привет я чат бот") # написать норм тектс для бота  типо просто первое сообщение в чате

@router.message()
async def answer_messages(message:Message):
    user_id = message.from_user.id
    is_user_subbed = await is_user_subbed(str(user_id))
    if not is_user_subbed:
        user_free_req = await get_amount_of_zaproses(str(user_id))
        if user_free_req == 0:
            await message.answer(text = "У вас не осталось бесплатных запросов.Купить подписку вы можете перейдя в профиль")
        else:
            await remove_free_zapros(str(user_id))
            response = ask_chat_gpt(str(message.text))
            await write_message(str(user_id),str(message.text),response)
            await message.answer(text = response)
    else:
        response = ask_chat_gpt(str(message.text))
        await write_message(str(user_id),str(message.text),response)
        await message.answer(text = response)
                
            
@router.message(F.photo)
async def answer_with_photo(message:Message):
    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
        await message.bot.download_file(file.file_path, tmp_file.name)
        results = reader.readtext(tmp_file.name)
    os.unlink(tmp_file.name)
    
    if results:
        text_lines = []
        for (bbox,text,prob) in results:
            if prob > 0.3:
                text_lines.append(text)
        result_text = " ".join(text_lines)        
    
    user_id = message.from_user.id
    is_user_subbed = await is_user_subbed(str(user_id))
    if not is_user_subbed:
        user_free_req = await get_amount_of_zaproses(str(user_id))
        if user_free_req == 0:
            await message.answer(text = "У вас не осталось бесплатных запросов.Купить подписку вы можете перейдя в профиль")
        else:
            
            full_text:str = str(message.text) + "\n" + message.caption + "\n" + result_text
            await remove_free_zapros(str(user_id))
            response = ask_chat_gpt(str(full_text))
            await write_message(str(user_id),str(message.text),response)
            await message.answer(text = response)
    else:
        response = ask_chat_gpt(str(message.text))
        await write_message(str(user_id),str(message.text),response)
        await message.answer(text = response)
                
    
    
    
    
       