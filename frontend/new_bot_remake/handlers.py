from aiogram import Bot,Dispatcher,F,Router
from aiogram.filters import CommandStart,Command
from aiogram.types import Message,File,Video,PhotoSize,LabeledPrice,PreCheckoutQuery,ContentType
import aiogram
import keyboards as kb
#from main import bot
import sys
import os
import cv2
import tempfile
import easyocr
import numpy as np
from config import PROJECT_ROOT
from pathlib import Path
import fitz
from pdf2image import convert_from_path
import zipfile
from docx import Document
from doc_handler import extract_text_from_docx_with_images
from backend.database.chats_database.chats_core import write_message,get_all_user_messsages
from backend.api import ask_chat_gpt
from backend.database.core import create_deafault_user_data,remove_free_zapros,check_free_zapros_amount,get_amount_of_zaproses,subscribe,set_sub_bac_to_false,get_me,unsub_all_users_whos_sub_is_ending_today,is_user_subbed,buy_zaproses,get_sub_date_end
from datetime import timedelta,datetime
from typing import List

router = Router()


reader = easyocr.Reader(["en","ru"])

@router.message(CommandStart())
async def start_messsage(message:Message):
    user_name = message.from_user.username
    user_id = message.from_user.id
    await create_deafault_user_data(str(user_id))
    await message.answer("Welcome",reply_markup=kb.main_keyboard)# вставить сюда норм текст
    
async def unsub_full_func(username:str) -> bool:
    if await is_user_subbed(username):
        user_end_date:str = await get_sub_date_end(username)
        date_now = datetime.now().date()
        
        async def transform_date_to_int(date:str) -> int:
            dt:str = ""
            for tm in str(date).split('-'):
                dt += tm
            return int(dt)
        
        date_int_end:int = await transform_date_to_int(str(user_end_date))
        date_int_now:int = await transform_date_to_int(str(date_now)) 
        
        if date_int_now >= user_end_date:
            await set_sub_bac_to_false(username)  
            return True
        return False 
    return False
            
        
    

@router.message(F.text == "Profile")
async def profile_handler(message:Message):
    
    user_name = message.from_user.username
    user_id = message.from_user.id
    res_unsub:bool = await unsub_full_func(str(user_id))
    if res_unsub:
        await message.asnwer(text = "Ваша подписка закончилась.Что бы продолжить пользоваться премиум функционалом вам нужно снова ее оформить.Вы можете пользоваться ботом в пределе бесплатного тарифа.Благодарим за поддержку")
    user_data = await get_me(str(user_id))
    user_data[str(user_id)] = user_name
    user_subbed:bool = await  is_user_subbed(str(user_id))
    result = f"""
        Profile of {user_data[str(user_id)]}
        
        
        Free requests : {user_data["Free requests"]}
        
        Subscribed : {user_data["Subscribed"]}

        Date of subscribtion to end : {user_data["Date of subscribtion to end"] if user_data["Subscribed"] else None}    
    
    """
    if not user_subbed:
        await message.answer(
        result,
        reply_markup=kb.profile_key_borad        
        )
    else:
        await message.answer(
        result        
    )

@router.message(F.text == "Subscribe")
async def subscribe_handler(message:Message):
    user_id = message.from_user.id
  
    buy_sub_text = "Тестовое лицензионное соглашение" # вставить норм текст для подписки
    await message.answer(buy_sub_text,reply_markup=kb.buy_sub_keyboard)

@router.message(F.text == "Back")
async def back(message:Message):
    await message.answer(text = "Вы вернулись в главное меню",reply_markup=kb.main_keyboard)

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
        #reply_markup=kb.back_keyboard
    )

@router.pre_checkout_query()
async def check_pay(pre_check_out_qr:PreCheckoutQuery):
    pass 

@router.message(lambda message: message.content_type == ContentType.SUCCESSFUL_PAYMENT)   
async def  succes_ful_payment(message:Message):
    pass

@router.message(F.text == "Chat")
async def chat_handler(message:Message):
    user_id = message.from_user.id
    res_unsub:bool = await unsub_full_func(str(user_id))
    if res_unsub:
        await message.asnwer(text = "Ваша подписка закончилась.Что бы продолжить пользоваться премиум функционалом вам нужно снова ее оформить.Вы можете пользоваться ботом в пределе бесплатного тарифа.Благодарим за поддержку")
   
    await message.answer("Привет я твой помошник ChatGPT от LudiceTeam в Telegram") # написать норм тектс для бота  типо просто первое сообщение в чате

@router.message(F.text & ~F.command)
async def answer_messages(message:Message):
   
        user_id = message.from_user.id
        res_unsub:bool = await unsub_full_func(str(user_id))
        if res_unsub:
            await message.asnwer(text = "Ваша подписка закончилась.Что бы продолжить пользоваться премиум функционалом вам нужно снова ее оформить.Вы можете пользоваться ботом в пределе бесплатного тарифа.Благодарим за поддержку")
        await message.answer("Думаю...")
        user_messages = await get_all_user_messsages(str(user_id))
        is_user_subbed_ = await is_user_subbed(str(user_id))
        if not is_user_subbed_:
            user_free_req = await get_amount_of_zaproses(str(user_id))
            if user_free_req == 0:
                await message.answer(text = "У вас не осталось бесплатных запросов.Купить подписку вы можете перейдя в профиль")
            else:
                await remove_free_zapros(str(user_id))
                response = ask_chat_gpt(str(message.text) + f"Вот все сообщение пользователя что бы тебе было легче его понимать : {user_messages}")
                await write_message(str(user_id),str(message.text),response)
                await message.answer(text = response)
        else:
            response = ask_chat_gpt(str(message.text) + f"Вот все сообщение пользователя что бы тебе было легче его понимать : {user_messages}")
            await write_message(str(user_id),str(message.text),response)
            await message.answer(text = response)
                
            
@router.message(F.photo)
async def answer_with_photo(message:Message):
   
        user_id = message.from_user.id
        res_unsub:bool = await unsub_full_func(str(user_id))
        if res_unsub:
            await message.asnwer(text = "Ваша подписка закончилась.Что бы продолжить пользоваться премиум функционалом вам нужно снова ее оформить.Вы можете пользоваться ботом в пределе бесплатного тарифа.Благодарим за поддержку")
        await message.answer("Думаю...")
        photo = message.photo[-1]
        user_messages = await get_all_user_messsages(str(user_id))
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
            result_text = "\n".join(text_lines)
        else:
            await message.answer(text = "Текст с фотографии не извелечен")      
            return      
        
        is_user_subbed_ = await is_user_subbed(str(user_id))
        if not is_user_subbed_:
            user_free_req = await get_amount_of_zaproses(str(user_id))
            if user_free_req == 0:
                await message.answer(text = "У вас не осталось бесплатных запросов.Купить подписку вы можете перейдя в профиль")
            else:
                
                full_text:str = str(message.text) + "\n" + message.caption + "\n" + result_text
                await remove_free_zapros(str(user_id))
                response = ask_chat_gpt(str(full_text) + f"Вот все сообщение пользователя что бы тебе было легче его понимать : {user_messages}")
                await write_message(str(user_id),str(full_text),response)
                await message.answer(text = response)
        else:
            full_text:str = str(message.text) + "\n" + message.caption + "\n" + result_text
            response = ask_chat_gpt(str(full_text + f"Вот все сообщение пользователя что бы тебе было легче его понимать : {user_messages}"))
            await write_message(str(user_id),str(full_text),response)
            await message.answer(text = response)
    
async def read_text_from_image(file_path:str) -> str:
    results = reader.readtext(file_path,detail = 0,paragraph=True)
    return "\n".join(results) if results else ""

async def read_pdf(path:str) -> str:
    all_text = []
    try:
        images = convert_from_path(path)
        for i,image in enumerate(images):
            with tempfile.NamedTemporaryFile(delete = False,suffix=".jpg") as tmp_file:
                image.save(tmp_file.name,"JPEG")
                page_text = await read_text_from_image(tmp_file.name)
                if page_text:
                    all_text.append(page_text)
                os.unlink(tmp_file.name)    
        return "\n\n".join(all_text)
    except Exception as e:
        raise Exception(f"Error : {e}")            
    


@router.message(F.document)
async def answer_with_document(message:Message):
    
        user_id = message.from_user.id
        res_unsub:bool = await unsub_full_func(str(user_id))
        if res_unsub:
            await message.asnwer(text = "Ваша подписка закончилась.Что бы продолжить пользоваться премиум функционалом вам нужно снова ее оформить.Вы можете пользоваться ботом в пределе бесплатного тарифа.Благодарим за поддержку")
        await message.answer("Думаю...")
        document = message.document
        filename = document.file_name.lower()
        file = await message.bot.download_file(document.file_id)
        user_messages = await get_all_user_messsages(str(user_id))
        
        with tempfile.TemporaryFile(delete = False,suffix=Path(filename).suffix) as tmp_fi:
            await message.bot.download_file(file.file_path, tmp_fi.name)
            file_path = tmp_fi.name
        try:
            if file_path.endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif')):
                text = await read_text_from_image(file_path)
                
            elif file_path.endswith('.pdf'):
                text = await read_pdf(file_path)
                
            elif file_path.endswith(('.docx','.doc')):
                text = await extract_text_from_docx_with_images(file_path)
                
            elif file_path.endswith(('.txt','.text')):
                with open(file_path,"r",encoding='utf-8') as file:
                    text = file.read()
            else:
                await message.answer(text = "Формат файла не поддерживается")
                return
            
            if os.path.exists(file_path):
                os.unlink(file_path)
            
            if text == "" or not text or text is None:
                await message.asnwer(text = "Текст с данного файда не был извлечен")    
                
            is_user_subbed_ = await is_user_subbed(str(user_id))
            if not is_user_subbed_:
                user_req = await get_amount_of_zaproses(str(user_id))
                if user_req == 0:
                    await message.answer(text = "У вас не осталось бесплатных запросов.Купить подписку вы можете перейдя в профиль")
                else:
                    full_text:str = str(message.text) + "\n" + message.caption + "\n" + text
                    await remove_free_zapros(str(user_id))
                    response = ask_chat_gpt(str(full_text) + f"Вот все сообщение пользователя что бы тебе было легче его понимать : {user_messages}")
                    await write_message(str(user_id),str(full_text),response)
                    await message.answer(text = response)
            else:
                full_text = str(message.text) + "\n" +  str(message.caption) + "\n" + text
                response = ask_chat_gpt(str(full_text + f"Вот все сообщение пользователя что бы тебе было легче его понимать : {user_messages}"))
                await write_message(str(user_id),str(full_text),response)
                await message.answer(text = response)                
                    
        except Exception as e:
            raise Exception(f"Error : {e}") 

            
            


#переписать логику сосотаяние чата и все (сделать новую бд)     