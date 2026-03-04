from aiogram import Bot,Dispatcher,F,Router
from aiogram.filters import CommandStart,Command,CommandObject
from aiogram.types import Message,File,Video,PhotoSize,LabeledPrice,PreCheckoutQuery,ContentType,CallbackQuery,InlineKeyboardMarkup,InlineKeyboardButton,BufferedInputFile 
import aiogram
import keyboards as kb
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
from backend.database.chats_database.chats_core import write_message,get_all_user_messsages,delete_all_messages
#from backend.api import ask_chat_gpt
from backend.database.core import create_deafault_user_data,remove_free_zapros,check_free_zapros_amount,get_amount_of_zaproses,subscribe,set_sub_bac_to_false,get_me,is_user_subbed,buy_zaproses,get_sub_date_end,subscribe_basic,unsub_basic,is_user_subbed_basic,get_last_ref_basic,refil_zap,upadate_last_ref_date,is_user_exists,get_user_referal_count,add_referal,count_all_users,get_all_usernames
from datetime import timedelta,datetime
from typing import List
from backend.database.state_database.state_core import create_user_state,change_user_state,get_user_state
from backend.database.sale_database.sale_core import cretae_user_sale_table,change_to_sale,does_user_have_sale,give_referal_sub,does_user_have_referal_sub
import time
from io import BytesIO 
import aiohttp
from openai import AsyncOpenAI
import asyncio
from asyncio import Queue
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from concurrent.futures import ThreadPoolExecutor
import re
import pytesseract
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
import io
from backend.database.long_time_database.long_time_core import default_long_time,update_last_time
from backend.database.ai_choose_database.ai_core import get_user_model_name,create_default_user_model_name,change_user_model_name
from aiogram.utils.keyboard import InlineKeyboardBuilder
from backend.database.nano_banana.nano_core import create_default_user_data_nano,minus_one_req_nano,get_user_req_nano,refil_user_amount_nano
import base64


router = Router()
gpt_queue = Queue(maxsize=100)


#reader = easyocr.Reader(["en","ru"],gpu = False) # будут норм сервера поставить True
os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'

@router.message(CommandStart())
async def start_messsage(message:Message):
    welcome_text = """Добро пожаловать в NEUROHUB от LudiceTeam!

Наш бот помогает быстро и удобно получать ответы на любые вопросы. Вы можете задавать текстовые запросы — и бот предоставит понятные и точные ответы.

Но что ещё удобнее — не обязательно вручную вводить текст! Просто отправьте картинку с нужным текстом или задачей, а наш бот самостоятельно её «прочитает», распознает и решит за вас.

Используйте нашего бота для учебы, работы и повседневных задач — он сэкономит ваше время и сделает процесс проще!"""
    user_name = message.from_user.username
    user_id = message.from_user.id
    args = message.text.split()
    if not await is_user_exists(str(user_id)):
        if len(args) > 1:
            referal_id = args[1]
            if referal_id != str(user_id):
                await buy_zaproses(str(referal_id),5)
                await add_referal(str(referal_id))
                await message.answer(text = f"🎉 Вы зашли по ссылке друга!")
                
        await message.answer(text = welcome_text)# вставить сюда норм текст            
                
    else:
        await message.answer(text = welcome_text)# вставить сюда норм текст            
    await default_long_time(str(user_id))
    await create_deafault_user_data(str(user_id))
    await create_user_state(str(user_id))
    await cretae_user_sale_table(str(user_id))
    await create_default_user_model_name(str(user_id))
    await create_default_user_data_nano(str(user_id),5)

async def time_to_give_free_referal_sub(username:str) -> bool:
    user_friends_invited:int = await get_user_referal_count(username)
    if user_friends_invited >= 5 and not await is_user_subbed(username) and not await is_user_subbed_basic(username):
        recieved_sub = await does_user_have_referal_sub(username)
        if recieved_sub:
            return False
        else:
            await give_referal_sub(username)
            await subscribe_basic(username)
            return True
    else:
        return False    
    
async def transform_date_to_int(date:str) -> int:
        dt:str = ""
        for tm in str(date).split('-'):
            dt += tm
        return int(dt)

async def refil_requests_basic_sub(username:str):
    is_user_subbed_basic_flag = await is_user_subbed_basic(username)
    user_premium_sub_flag = await is_user_subbed(str(username))
    
    
    
    if is_user_subbed_basic_flag or user_premium_sub_flag:
        date_now = datetime.now().date()
        user_last_refil_date = await get_last_ref_basic(username)
            
            
        dt_int = await transform_date_to_int(str(date_now))
        last_ref_int = await transform_date_to_int(str(user_last_refil_date))
            
        if dt_int > last_ref_int:
            if user_premium_sub_flag:
                await refil_user_amount_nano(str(username),15)  
            
            if is_user_subbed_basic_flag:
                    await refil_zap(username)
                    await upadate_last_ref_date(username)
                    await refil_user_amount_nano(str(username),10)
                
        else:
            return
       
        

async def unsub_full_func(username:str) -> bool:
    if await is_user_subbed(username):
        user_end_date:str = await get_sub_date_end(username)
        date_now = datetime.now().date()
        
        date_int_end:int = await transform_date_to_int(str(user_end_date))
        date_int_now:int = await transform_date_to_int(str(date_now)) 
        
        if date_int_now >= date_int_end:
            await set_sub_bac_to_false(username)  
            return True
        return False 
    
    elif await is_user_subbed_basic(username):
        user_end_sub:str = await get_sub_date_end(username)
        date_now_basic = datetime.now().date()
        date_int_end:int = await transform_date_to_int(str(user_end_sub))
        date_int_now:int = await transform_date_to_int(str(date_now_basic)) 
        
        if date_int_now >= date_int_end:
            await unsub_basic(username)  
            return True
        return False 
    else:
        return False
            

#Функция создает данные в таблице Nano для пользователей которые зарегались в боте до обновление 1.1
async def create_user_data_in_nano_database(username:str):
    user_premium_sub = await is_user_subbed(username)
    user_basic_sub = await is_user_subbed_basic(username)
    if user_premium_sub:
        await create_default_user_data_nano(username,15)
    elif user_basic_sub:
        await create_default_user_data_nano(username,10)
    else:
        await create_default_user_data_nano(username,5)

@router.startup()
async def start_up():
    await start_worker(5) 
    

@router.message(Command("profile"))
async def profile_handler(message:Message):
    user_name = message.from_user.username
    user_id = message.from_user.id
    await create_user_data_in_nano_database(str(user_id))
    await refil_requests_basic_sub(str(user_id))
    await change_user_state(str(user_id),False)
    await update_last_time(str(user_id))
    res_unsub:bool = await unsub_full_func(str(user_id))
    if res_unsub:
        await message.answer( text="📅 Ваша подписка закончилась.\n\n"
         "🔓 Чтобы продолжить пользоваться платным функционалом, вам нужно оформить её снова.\n\n"
         "🆓 Вы можете пользоваться ботом в пределах бесплатного тарифа.\n\n"
         "Благодарим за поддержку!")
    
    free_ref_sub = await  time_to_give_free_referal_sub(str(user_id))
    if free_ref_sub:
        ref_text = """✅ Basic подписка получена!
✅ Награда за 5 приглашённых друзей
✅ Активна 30 дней"""
        await message.answer(text = ref_text)    
        
        
        
    user_data = await get_me(str(user_id))
    user_data[str(user_id)] = user_name
    
    user_subbed:bool = await  is_user_subbed(str(user_id))
    user_basic_sub:bool = await is_user_subbed_basic(str(user_id))
    
   
    async def get_request_text() -> str:
        
        if user_subbed:
            return "∞ (безлимит)"
        elif user_basic_sub:
            user_zaps = await get_amount_of_zaproses(str(user_id))
            return f"{user_zaps}/25"
        else:
            user_zaps = await get_amount_of_zaproses(str(user_id))
            return f"{user_zaps}/20"
    
    async def get_user_subscribtion_type() -> str:
       
        
        if user_subbed:
            return "Premium (Безлимитная)"
        elif user_basic_sub:
            return "Basic (25 запросов в день)"
        else:
            return "Не активирована"
    
    async def get_sub_end_text() -> str:
        if user_subbed:
            return user_data["Date of subscribtion to end"]  
        elif user_basic_sub:
            return user_data["Date of subscribtion to end"]
        else:
            return "Подписка не активирована" 
    
    async def get_nano_banana_text() -> str:
        req_amount_nano:int = await get_user_req_nano(str(user_id))
        if user_subbed:
            return f"{req_amount_nano}/15"
        elif user_basic_sub:
            return f"{req_amount_nano}/10"
        else:
            return f"{req_amount_nano}/5"    
            
    
    new_profile_desc = f"""
        Профиль @{user_data[str(user_id)]}:
        
Запросов осталось: {await get_request_text()}

Запросы к Nano Banana: {await get_nano_banana_text()}

Статус подписки: {await get_user_subscribtion_type()}


Срок истечения подписки: {await get_sub_end_text()}

    """
    if not user_subbed and not await is_user_subbed_basic(str(user_id)):
        await message.answer(
         new_profile_desc   
        )
    else:
        await message.answer(
         new_profile_desc     
    )


@router.message(Command("gsp"))
async def gsp_handler(message:Message,command:CommandObject):
    user_id = str(message.from_user.id)
    if user_id == "6184036112":
        args = command.args
        if not args:
            await message.answer("Укажите ID! Пример: /gsp 12345")
            return
        args_list = args.split()
        user_id_sub = str(args_list[0])
        if await is_user_exists(user_id_sub):
            await subscribe(user_id_sub)
            await message.answer(text = "✅ Подписка выдана")
            return
        else:
            await message.answer(text = "Пользователь не найден")
    else:
        return

@router.message(Command("rms"))
async def remove_sub_from_user(message:Message,command:CommandObject):
    user_id = str(message.from_user.id)
    if user_id == "6184036112":
        args = command.args
        if not args:
            await message.answer("Укажите ID! Пример: /rms 12345")
            return
        args_list = args.split()
        user_id_sub = str(args_list[0])
        if await is_user_exists(user_id_sub):
            await set_sub_bac_to_false(user_id_sub)
            await message.answer(text = "✅ Подписка отобрана")
            return
        else:
            await message.answer(text = "Пользователь не найден")
    else:
        return



@router.message(Command("count"))
async def count_all_users_handler(message:Message):
    user_id = str(message.from_user.id)
    if user_id  == "6184036112":
        amount = await count_all_users()
        await message.answer(text = str(amount))
    else:
        return    
        

  

@router.message(Command("referal"))
async def referal_prog(message:Message):
    user_id = str(message.from_user.id)
    await create_user_data_in_nano_database(str(user_id))
    user_referal_count = await get_user_referal_count(user_id)
    await update_last_time(str(user_id))
    referal_text = f"""📢 **РЕФЕРАЛЬНАЯ ПРОГРАММА**

🎁 Приглашайте друзей и получайте бонусы!

🔗 **Ваша реферальная ссылка:**
https://t.me/character_ai_ludice_team_bot?start={user_id}

👥 **Приглашено друзей:** {user_referal_count}

🏆 **Ваши бонусы за приглашения:**

✅ **За каждого друга:** +5 запросов к нейросети
✅ **Первые 5 друзей:** Подписка Basic на 1 месяц!

💡 **Как это работает:**
1. Отправьте другу вашу реферальную ссылку
2. Друг переходит и начинает пользоваться ботом
3. Вы автоматически получаете бонусы!


🚀 **Начните приглашать прямо сейчас!**"""
    await message.answer(text = referal_text)
    free_ref_sub = await  time_to_give_free_referal_sub(str(user_id))
    if free_ref_sub:
        ref_text = """✅ Basic подписка получена!
✅ Награда за 5 приглашённых друзей
✅ Активна 30 дней"""
        await message.answer(text = ref_text) 
    res_unsub: bool = await unsub_full_func(str(user_id))
    if res_unsub:
        await message.answer( text="📅 Ваша подписка закончилась.\n\n"
        "🔓 Чтобы продолжить пользоваться платным функционалом, вам нужно оформить её снова.\n\n"
        "🆓 Вы можете пользоваться ботом в пределах бесплатного тарифа.\n\n"
        "Благодарим за поддержку!")  
    
     

@router.message(Command("pay"))
async def subscribe_hander(message:Message):
    user_id = str(message.from_user.id)
    await create_user_data_in_nano_database(str(user_id))
    sub_text = """Возможности подписок: 

Basic:
Gemini 3 Flash, 
Gemini 2.5 Flash, 
Deepseek, 
Mistral Large, 
Claude Opus 4.6, 
Claude Sonnet 4.6, 
GPT-4, 
GPT-4 Turbo - 25 запросов/день

Nano Banana - 5 запросов/день

Premium: безлимитный доступ к любой нейросети, кроме Nano Banana (15 запросов/день)"""
    await message.answer(text = sub_text,reply_markup=kb.subcribtion_key_board)


async def count_sale(price:int) -> int:
    sale:int = int(price * 0.1)
    return price - sale

@router.callback_query(F.data == "subscribe_premium")
async def premium_handler(callback:CallbackQuery):
    price = 499
    user_has_sale = await does_user_have_sale(str(callback.from_user.id))
    if user_has_sale:
        price = await count_sale(price)
        
    buy_sub_text = f"1) Стоимость: {price} звезд / 30 дней. \n\n Бонус: любая следующая покупка в боте будет со скидкой 10%"
    prices = [LabeledPrice(label=f"{price} ⭐", amount=price)]
    
    inline_pay = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text = f"Заплатить {price} ⭐",pay = True)]
    ])
    
    
    await callback.bot.send_invoice(
        chat_id=callback.from_user.id,
        title="Premium",
        description=buy_sub_text,
        payload="subscribtion",
        provider_token="410694247:TEST:48b50af2-4c6d-4c87-8d3f-6912d0d8c38a",
        prices=prices,
        currency="XTR",    
        reply_markup=inline_pay
    )
    
    
@router.callback_query(F.data == "subscribe_basic")
async def basic_sub_handler(callback:CallbackQuery):
    price = 199
    user_has_sale = await does_user_have_sale(str(callback.from_user.id))
    if user_has_sale:
        price = await count_sale(price)
        
    inline_pay = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text = f"Заплатить {price} ⭐",pay = True)]
    ])
    
    buy_sub_text = f"1) Стоимость: {price} звезд / 30 дней"
    prices = [LabeledPrice(label=f"{price} ⭐", amount=price)]
    await callback.bot.send_invoice(
    chat_id=callback.from_user.id,
    title="Basic",
    description=buy_sub_text,
    payload="basic",
    provider_token="410694247:TEST:48b50af2-4c6d-4c87-8d3f-6912d0d8c38a",
    prices=prices,
    currency="XTR",    
    reply_markup=inline_pay
)
    
    

requests_buy_text = "Данная покупка предоставляет только фиксированное количество запросов без каких-либо дополнительных привилегий, гарантий приоритета или влияния на обработку запросов."        

   
@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)

@router.message(F.successful_payment)
async def succesful_payment_handler(message:Message):
    
    payment = message.successful_payment
    user_id = str(message.from_user.id)
    invoice = payment.invoice_payload.split("_")
    
    
    #if "ludice_team" in payment.invoice_payload:
        #await buy_zaproses(user_id,int(invoice[-1]))
       # await message.answer(text = f"✅ Вы купили {invoice[-1]} запросов. Спасибо за покупку. Приятного пользования.")
    if "subscribtion" in payment.invoice_payload:
        await subscribe(user_id)
        await change_to_sale(user_id)
        await message.answer("✅ Вы успешно подписались на Premium подписку. Спасибо за покупку. Приятного пользования.")
    elif "basic" in payment.invoice_payload:
        await subscribe_basic(user_id)
        await message.answer("✅ Вы успешно подписались на Basic. Спасибо за покупку. Приятного пользования.")
            
    else:
        await message.answer("Что то пошло не так. Попробуйте снова.")
    
     

#@router.message(F.text == "Назад")
#async def back(message:Message):
 #   await message.answer(text = "Вы вернулись в главное меню",reply_markup=kb.main_keyboard)


    
@router.message(Command("reset"))
async def reset(message:Message):
    user_id = str(message.from_user.id)
    await create_user_data_in_nano_database(str(user_id))
    await refil_requests_basic_sub(str(user_id))
    await delete_all_messages(user_id)
    await update_last_time(str(user_id))
    await message.answer(text = "✅ История отчищена.")

@router.message(Command("help"))
async def help(message:Message):
    help_text = """🎯Основные разделы (главное меню):

Чат — начать общение со мной. Здесь я помогаю с текстами презентаций, переводом, разбором параграфов и любыми вашими вопросами.

Профиль — информация о вашем аккаунте. Здесь можно посмотреть оставшееся количество запросов на день.

Сбросить контекст — очистить историю нашего диалога.

Помощь — это сообщение с описанием возможностей бота (данное сообщение).

Поддержка — связь с разработчиком, если что-то работает не так.

👤Профиль:
В этом разделе вы можете контролировать свою активность:

Узнать свой статус.

Проверить лимит доступных запросов.

💡Советы:

Старайтесь формулировать запрос четко и как можно подробнее — так результат будет точнее."""
    user_id:str = str(message.from_user.id)
    await update_last_time(str(user_id))
    await message.answer(text = help_text)



@router.message(Command("support"))
async def support_handler(message:Message):
    user_id = str(message.from_user.id)
    await create_user_data_in_nano_database(str(user_id))
    await update_last_time(str(user_id))
    await message.answer(text =  "Отправьте ваш вопрос вот этому пользователю : @kksndid_support")
        

async def worker():
    while True:
        user_id,request,future = await gpt_queue.get()
        
        try:
            response = await ask_chat_gpt(request,user_id)
            future.set_result(response)
            
        except Exception as e:
            future.set_exception(e)
            print(f"Error : {e}")
        finally:
            gpt_queue.task_done()

async def start_worker(count = 5):
    for i in range(count):
        asyncio.create_task(worker(),name = f"worker_{i}")
    print(f"✅ Запущено {count} воркеров")

async def add_to_queue(user_id:str,request:str) -> str | bytes:
    future = asyncio.Future()
    try:
        await asyncio.wait_for(
            gpt_queue.put((user_id, request[:4000], future)), 
            timeout=5.0
        )
    except asyncio.TimeoutError:
        return "🔄 Очередь переполнена"
    try:
        result = await asyncio.wait_for(future,timeout=200)
        return result
    except asyncio.TimeoutError:
        future.cancel()
        return "⏱️ Превышено время ожидания"

async def get_user_models_keyboard(user_id:str):
    builder = InlineKeyboardBuilder()
    models = [
        ("google/gemini-3-flash-preview", "Gemini 3 Flash"),
        ("google/gemini-2.5-flash", "Gemini 2.5 Flash"),
        ("openai/gpt-4", "GPT-4"),
        ("openai/gpt-4-turbo", " GPT-4 Turbo"),
        ("anthropic/claude-opus-4.6", "Claude Opus"),
        ("anthropic/claude-sonnet-4.6", "Cloude Sonnet"),
        ("mistralai/mistral-large", "Mistral Large"),
        ("deepseek/deepseek-chat", "DeepSeek Chat"),
        ("google/gemini-3-pro-image-preview","Nano Banana")
    ]
    user_model = await get_user_model_name(user_id)
    for data,model_button_text in models:
        if user_model == data:
            button_new_text = f"✅ {model_button_text}"
        else:
            button_new_text = model_button_text
        builder.button(text=button_new_text, callback_data=data)
    builder.adjust(2, 2, 2, 2, 2, 2)
    
    return builder.as_markup()

       
            
@router.message(Command("ai_mode"))
async def choose_model_handler(message:Message):
    user_id = str(message.from_user.id)
    await create_user_data_in_nano_database(str(user_id))
    text = (
        "🤖 **Выберите AI модель**\n\n"
        
        "**Google: Gemini 3 Flash**\n"
        "⚡ Быстрая модель от Google\n\n"
        
        "**Google: Gemini 2.5 Flash**\n"
        "⚡ Сбалансированная модель от Google\n\n"
        
        "**OpenAI: GPT-4**\n"
        "🤖 Мощная модель от OpenAI\n\n"
        
        "**OpenAI: GPT-4 Turbo**\n"
        "🤖 Ускоренная версия GPT-4\n\n"
        
        "**Anthropic: Claude Opus 4.6**\n"
        "👑 Флагманская модель Claude\n\n"
        
        "**Anthropic: Claude Sonnet 4.6**\n"
        "📝 Стандартная модель Claude\n\n"
        
        "**Mistral: Mistral Large**\n"
        "🌀 Европейская языковая модель\n\n"
        
        "**DeepSeek: DeepSeek Chat**\n"
        "🧠 Китайская языковая модель\n\n"
        
        "**Nano Banana: Banana Gen**\n"
        "🍌 Генерация реалистичных изображений\n\n"
        
    )
    user_keyborad = await get_user_models_keyboard(user_id)
    await message.answer(
        text = text,
        reply_markup=user_keyborad,
        parse_mode="Markdown"
        )


@router.callback_query(F.data.startswith(("google/", "openai/", "anthropic/", "deepseek/","mistralai/")))
async def ai_change_handler(callback:CallbackQuery):
    user_id = str(callback.from_user.id)
    await change_user_model_name(user_id,callback.data)
    
    user_keyboard = await get_user_models_keyboard(user_id)
    
    await callback.message.edit_reply_markup(
        reply_markup=user_keyboard
    )


from frontend.new_bot_remake.keys import OPEN_AI_KEY

client = AsyncOpenAI(
    api_key=OPEN_AI_KEY,
    base_url="https://openrouter.ai/api/v1",
    timeout=60.0,
    max_retries=2
)

async def ask_chat_gpt(request: str,user_id:str) -> str | bytes:
    try:
        request = request[:10000]
        
        user_model = await get_user_model_name(user_id)
        
        if user_model == "google/gemini-3-pro-image-preview":
            response = await client.chat.completions.create(
            model=user_model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": request
                        }
                    ]
                }
            ],
            extra_body={
                "modalities": ["image", "text"],  # КЛЮЧЕВОЙ ПАРАМЕТР!
            }
        )
            message = response.choices[0].message
            if hasattr(message, 'images') and message.images:
                img_dict = message.images[0]
                if 'image_url' in img_dict:
                    img_data = img_dict['image_url']  # <-- ВОТ ТАК ПРАВИЛЬНО!
                    
                    true_img_data = img_data["url"]
                   
                    if ',' in true_img_data:
                        base64_str = true_img_data.split(',')[1]
                    else:
                        base64_str = true_img_data
                    
                    
                    image_bytes = base64.b64decode(base64_str)
                    return image_bytes
            return f"🤔 Нет изображения в ответе."
            
        response = await client.chat.completions.create(  # <-- ВАЖНО: используем chat.completions
            model=user_model,  # <-- ПРАВИЛЬНОЕ имя модели
            messages=[
                {"role": "user", "content": request}
            ]
        )
        
        result = response.choices[0].message.content.strip()
        if not result:
            return "🤔 Gemini вернул пустой ответ."
        
        return result
        
    except Exception as e:
        print(f"OpenAI SDK error: {e}")
        return f"❌ Ошибка: {str(e)[:100]}"



@router.message(F.text & ~F.command)
async def answer_messages(message:Message):
        #user_state = await get_user_state(str(message.from_user.id))
        await refil_requests_basic_sub(str(message.from_user.id))
        user_id = message.from_user.id
        await update_last_time(str(user_id))
        await create_user_data_in_nano_database(str(user_id))
        res_unsub:bool = await unsub_full_func(str(user_id))
        if res_unsub:
            await message.answer(text="📅 Ваша подписка закончилась.\n\n"
            "🔓 Чтобы продолжить пользоваться платным функционалом, вам нужно оформить её снова.\n\n"
            "🆓 Вы можете пользоваться ботом в пределах бесплатного тарифа.\n\n"
            "Благодарим за поддержку!")
            
        free_ref_sub = await  time_to_give_free_referal_sub(str(user_id))
        if free_ref_sub:
            ref_text = """✅ Basic подписка получена!
    ✅ Награда за 5 приглашённых друзей
    ✅ Активна 30 дней"""
            await message.answer(text = ref_text)    
                
        
        think_message = await message.answer("Думаю...")
        user_messages = await get_all_user_messsages(str(user_id))
        is_user_subbed_ = await is_user_subbed(str(user_id))
        
        promt = f"""Ты — ассистент, который помогает пользователю, учитывая контекст переписки.

История сообщений пользователя (для понимания стиля и контекста):
{user_messages}

Текущее сообщение пользователя (на которое нужно ответить):
{str(message.text)}

Задача: Ответь на текущее сообщение пользователя, опираясь на историю переписки. Сохраняй релевантность и последовательность диалога.
Забудь про Markdown, JSON и любой другой синтаксис. Отвечай обычным человеческим текстом, как в переписке. Без звездочек, решеток, кавычек, блоков кода и форматирования. Если нужно записать уравнение или пример — пиши его в строчку обычными символами, например: x2 + 2x - 3 = 0 или 3 * 4 = 12. Главное правило: никаких спецсимволов для оформления, только текст."""
        
        user_model = await get_user_model_name(str(user_id))
        if user_model == "google/gemini-3-pro-image-preview":
            user_nano_req = await get_user_req_nano(str(user_id))
            #user_subbed = await is_user_subbed(str(user_id))
            if user_nano_req == 0:
                await message.answer(text = "У вас не осталось запросов к Nano Banana.")
                return
            
            response = await add_to_queue(str(user_id),str(message.text))
            #await think_message.delete()
            if type(response) == str:
                await message.answer(text = response)
            elif type(response) == bytes:
                await message.answer_photo(
                    photo=BufferedInputFile(
                        file=response,
                        filename="image.png"
                    ),
                    caption=f"Промт: {str(message.text)}"
                )
            await minus_one_req_nano(str(user_id))    
            return
                
            
        if not is_user_subbed_:
            user_free_req = await get_amount_of_zaproses(str(user_id))
            user_basic_sub = await is_user_subbed_basic(str(user_id))
            if user_free_req == 0:
                if user_basic_sub:
                    await think_message.delete()
                    await message.answer(text = "У вас на сегодня закончились запросы.Попробуйте  завтра")
                else:
                    await think_message.delete()
                    await message.answer(text = "У вас не осталось бесплатных запросов.Купить подписку вы можете по команде /pay")
            else:
                
                response = await add_to_queue(str(user_id),promt)
                await remove_free_zapros(str(user_id))
                try:
                    await think_message.delete()
                except Exception as e:
                    raise Exception(f"Error : {e}")
                #await asyncio.sleep(0.5)
                
                
                if len(response) > 4096:
                    for i in range(0,len(response),4096):
                        part = response[i:i + 4096]
                        await message.answer(text = part)
                else:
                    await message.answer(text = response)        
                await write_message(str(user_id),str(message.text),response)
        else:
            response = await add_to_queue(str(user_id),promt)
            try:
                await think_message.delete()
            except Exception as e:
                raise Exception(f"Error : {e}")
           # await asyncio.sleep(0.5)
            
            
            if len(response) > 4096:
                for i in range(0,len(response),4096):
                    part = response[i:i + 4096]
                    await message.answer(text = part)
            else:
                await message.answer(text = response)        
            await write_message(str(user_id),str(message.text),response)
        
                    

class TesseractOCR:
    """Tesseract для бота с прямым доступом к файлам"""
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=2)
        
    async def extract_text_from_path(self, image_path: str) -> str:
        """Распознавание через прямой путь к файлу (ЛУЧШЕЕ КАЧЕСТВО)"""
        loop = asyncio.get_event_loop()
        try:
            text = await loop.run_in_executor(
                self.executor,
                self._process_image,
                image_path
            )
            return text
        except Exception as e:
            print(f"Tesseract error: {e}")
            return ""
    
    def _process_image(self, image_path: str) -> str:
        """Обработка изображения"""
        
        # 1. Открываем изображение напрямую (максимальное качество)
        img = Image.open(image_path)
        
        # 2. Увеличиваем если маленькое
        if max(img.size) < 1000:
            scale = 1500 / max(img.size)
            new_size = (int(img.size[0] * scale), int(img.size[1] * scale))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        # 3. Конвертируем в оттенки серого
        img = img.convert('L')
        
        # 4. Пробуем разные режимы Tesseract
        texts = []
        
        # Режим 6 - обычный текст
        config1 = r'--oem 3 --psm 6 -l rus'
        text1 = pytesseract.image_to_string(img, config=config1)
        texts.append(text1)
        
        # Режим 4 - переменный размер текста
        config2 = r'--oem 3 --psm 4 -l rus'
        text2 = pytesseract.image_to_string(img, config=config2)
        texts.append(text2)
        
        # Режим 12 - вертикальный текст
        config3 = r'--oem 3 --psm 12 -l rus'
        text3 = pytesseract.image_to_string(img, config=config3)
        texts.append(text3)
        
        # 5. Выбираем лучший результат
        best_text = max(texts, key=lambda x: len(x.strip()))
        
        # 6. Чистим текст
        best_text = self._clean_text(best_text)
        
        return best_text.strip()
    
    def _clean_text(self, text: str) -> str:
        """Чистка текста"""
        # Убираем лишние пробелы
        text = re.sub(r'\s+', ' ', text)
        
        # Исправляем типичные ошибки
        fixes = {
            ' 4 ': ' А ',
            ' B ': ' В ',
            ' 0 ': ' О ',
            'кмч': 'км/ч',
            'км/ч': 'км/ч',
            'межд': 'между',
            'котОрыын': 'которыми',
            'расстоянне': 'расстояние',
            'велосппеднстя': 'велосипедиста',
        }
        
        for wrong, correct in fixes.items():
            text = text.replace(wrong, correct)
        
        return text

ocr = TesseractOCR()    

async def is_user_has_free_req(username:str) -> bool:
    is_user_subbed_flag:bool = await is_user_subbed(username)
    if not is_user_subbed_flag:
        #basic_sub = await is_user_subbed_basic(username)
        user_free_req = await get_amount_of_zaproses(username)
        if user_free_req == 0:
            return True
        return False
    return False

    

            
@router.message(F.photo)
async def answer_with_photo(message: Message):
    #user_state = await get_user_state(str(message.from_user.id))
    await refil_requests_basic_sub(str(message.from_user.id))
    user_id = message.from_user.id
    await update_last_time(str(user_id))
    await create_user_data_in_nano_database(str(user_id))
    res_unsub: bool = await unsub_full_func(str(user_id))
    user_model = await get_user_model_name(str(user_id))
    if user_model == "google/gemini-3-pro-image-preview":
        await message.answer("Ваш запрос не подходит для данной модели. Измените запрос или выберите другую модель.")
        return
    think_message = await message.answer("Думаю...")
    
    has_req:bool = await is_user_has_free_req(str(user_id))
    if has_req:
        basic_sub = await is_user_subbed_basic(str(user_id))
        if basic_sub:
            await think_message.delete()
            await message.answer(text = "У вас на сегодня закончились запросы. Попробуйте  завтра")
            return
        else:
            await think_message.delete()
            await message.answer(text = "У вас не осталось бесплатных запросов.Купить подписку вы можете по команде /pay")
            return
    
    free_ref_sub = await  time_to_give_free_referal_sub(str(user_id))
    if free_ref_sub:
        ref_text = """✅ Basic подписка получена!
✅ Награда за 5 приглашённых друзей
✅ Активна 30 дней"""
        await message.answer(text = ref_text)    
        
                
            
                
        
    
    if res_unsub:
        await message.answer( text="📅 Ваша подписка закончилась.\n\n"
        "🔓 Чтобы продолжить пользоваться платным функционалом, вам нужно оформить её снова.\n\n"
        "🆓 Вы можете пользоваться ботом в пределах бесплатного тарифа.\n\n"
        "Благодарим за поддержку!")
    
    
    user_messages = await get_all_user_messsages(str(user_id))
    
    photo = message.photo[-1]
    file_info = await message.bot.get_file(photo.file_id)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
        await message.bot.download_file(file_info.file_path, tmp_file.name)
        image_path = tmp_file.name
    
    
    
    result_text = await ocr.extract_text_from_path(image_path)

    os.unlink(image_path) 
        
    #await message.answer(text = f"Вот текст с картинки  : {result_text}")
    
    if not result_text or result_text == "":
        await message.answer(text="Текст с фотографии не извлечен")
        await think_message.delete()
        return
    full_text: str = str(message.text) + "\n" + (str(message.caption) or "") + "\n" + result_text
    
    promt = f"""Ты — ассистент, который помогает пользователю, учитывая контекст переписки.

История сообщений пользователя (для понимания стиля и контекста):
{user_messages}

Текущее сообщение пользователя (на которое нужно ответить):
{full_text}

Задача: Ответь на текущее сообщение пользователя, опираясь на историю переписки. Сохраняй релевантность и последовательность диалога.
Забудь про Markdown, JSON и любой другой синтаксис. Отвечай обычным человеческим текстом, как в переписке. Без звездочек, решеток, кавычек, блоков кода и форматирования. Если нужно записать уравнение или пример — пиши его в строчку обычными символами, например: x2 + 2x - 3 = 0 или 3 * 4 = 12. Главное правило: никаких спецсимволов для оформления, только текст."""
    
    is_user_subbed_ = await is_user_subbed(str(user_id))
    
    if not is_user_subbed_:  
        response = await add_to_queue(str(user_id),promt)
        await remove_free_zapros(str(user_id))
        try:
            await think_message.delete()
        except Exception as e:
            raise Exception(f"Error: {e}")
        #await asyncio.sleep(0.5)
        
        
        if len(response) > 4096:
            for i in range(0,len(response),4096):
                part = response[i:i + 4096]
                await message.answer(text = part)
        else:
            await message.answer(text = response)        
        await write_message(str(user_id), str(full_text), response)
            
    else:
        #full_text: str = str(message.text) + "\n" + (message.caption or "") + "\n" + result_text
        response = await add_to_queue(str(user_id),promt)
        try:
            await think_message.delete()
        except Exception as e:
            raise Exception(f"Error: {e}")
        #await asyncio.sleep(0.5)
        
        if len(response) > 4096:
                for i in range(0,len(response),4096):
                    part = response[i:i + 4096]
                    await message.answer(text = part)
        else:
            await message.answer(text = response)
        await write_message(str(user_id), str(full_text), response)
   
            


async def read_pdf(path:str) -> str:
    all_text = []
    try:
        images = convert_from_path(path)
        for i,image in enumerate(images):
            with tempfile.NamedTemporaryFile(delete = False,suffix=".jpg") as tmp_file:
                image.save(tmp_file.name,"JPEG")
                page_text = await ocr.extract_text_from_path(tmp_file.name)
                if page_text:
                    all_text.append(page_text)
                os.unlink(tmp_file.name)    
        return "\n\n".join(all_text)
    except Exception as e:
        raise Exception(f"Error : {e}")            
    


@router.message(F.document)
async def answer_with_document(message: Message):
    #user_state = await get_user_state(str(message.from_user.id))
    await refil_requests_basic_sub(str(message.from_user.id))
    user_id = message.from_user.id
    await update_last_time(str(user_id))
    await create_user_data_in_nano_database(str(user_id))
    res_unsub: bool = await unsub_full_func(str(user_id))
    if res_unsub:
        await message.answer( text="📅 Ваша подписка закончилась.\n\n"
        "🔓 Чтобы продолжить пользоваться платным функционалом, вам нужно оформить её снова.\n\n"
        "🆓 Вы можете пользоваться ботом в пределах бесплатного тарифа.\n\n"
        "Благодарим за поддержку!")
    
    user_model = await get_user_model_name(str(user_id))
    if user_model == "google/gemini-3-pro-image-preview":
        await message.answer("Ваш запрос не подходит для данной модели. Измените запрос или выберите другую модель.")
        return
    
    think_message = await message.answer("Думаю...")
    
    has_req:bool = await is_user_has_free_req(str(user_id))
    if has_req:
        basic_sub = await is_user_subbed_basic(str(user_id))
        if basic_sub:
            await think_message.delete()
            await message.answer(text = "У вас на сегодня закончились запросы.Попробуйте снова завтра")
            return
        else:
            await think_message.delete()
            await message.answer(text = "У вас не осталось бесплатных запросов.Купить подписку вы можете по команде /pay")
            return
        
    free_ref_sub = await  time_to_give_free_referal_sub(str(user_id))
    if free_ref_sub:
        ref_text = """✅ Basic подписка получена!
✅ Награда за 5 приглашённых друзей
✅ Активна 30 дней"""
        await message.answer(text = ref_text)    
        
    
    document = message.document
    MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB

    if document.file_size > MAX_FILE_SIZE:
        await message.answer(
            f"❌ Файл слишком большой!\n"
            f"📁 Размер: {document.file_size / 1024 / 1024:.1f}MB\n"
            f"⚠️ Максимум: 20MB\n"
            f"💡 Попробуй сжать файл или отправь часть"
        )
        return
    
    filename = document.file_name.lower()
    
    #file_bytes = await message.bot.download_file(document.file_id)
    
    file_info = await message.bot.get_file(document.file_id)
    
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename).suffix) as tmp_fi:
        await message.bot.download_file(file_info.file_path,tmp_fi.name)
        file_path = tmp_fi.name
        
    try:
            
        if file_path.endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif')):
            text = await ocr.extract_text_from_path(file_path)
                
        elif file_path.endswith('.pdf'):
            text = await read_pdf(file_path)
            
        elif file_path.endswith(('.docx','.doc')):
            text = await extract_text_from_docx_with_images(file_path)
            
        elif file_path.endswith(('.txt','.text')):
            with open(file_path,"r",encoding='utf-8') as file:
                text = file.read()
        else:
            await message.answer(text="Формат файла не поддерживается")
            return
        
        if os.path.exists(file_path):
            os.unlink(file_path)
        
        if text == "" or not text or text is None:
            await message.answer(text="Текст с файла не был извлечен")   
            return 
    except Exception as e:
        print(f"Error : {e}")

    
    user_messages = await get_all_user_messsages(str(message.from_user.id))
    full_text: str = str(message.text) + "\n" + str(message.caption) + "\n" + text
    
    promt = f"""Ты — ассистент, который помогает пользователю, учитывая контекст переписки.

История сообщений пользователя (для понимания стиля и контекста):
{user_messages}

Текущее сообщение пользователя (на которое нужно ответить):
{full_text}

Задача: Ответь на текущее сообщение пользователя, опираясь на историю переписки. Сохраняй релевантность и последовательность диалога.
Забудь про Markdown, JSON и любой другой синтаксис. Отвечай обычным человеческим текстом, как в переписке. Без звездочек, решеток, кавычек, блоков кода и форматирования. Если нужно записать уравнение или пример — пиши его в строчку обычными символами, например: x2 + 2x - 3 = 0 или 3 * 4 = 12. Главное правило: никаких спецсимволов для оформления, только текст."""
    
    

    
    try:
            
        is_user_subbed_ = await is_user_subbed(str(user_id))
        if not is_user_subbed_:
            
            response = await add_to_queue(str(user_id),promt)
            await remove_free_zapros(str(user_id))
            try:
                await think_message.delete()
            except Exception as e:
                raise Exception(f"Error : {e}")
            
            #await asyncio.sleep(0.5)
            if len(response) > 4096:
                for i in range(0,len(response),4096):
                    part = response[i:i + 4096]
                    await message.answer(text = part)
            else:
                await message.answer(text = response)
            await write_message(str(user_id), str(full_text), response)
        else:
            #full_text = str(message.text) + "\n" + str(message.caption) + "\n" + text
            response = await add_to_queue(str(user_id),promt)
            try:
                await think_message.delete()
            except Exception as e:
                raise Exception(f"Error : {e}")
            
            #await asyncio.sleep(0.5)
            if len(response) > 4096:
                for i in range(0,len(response),4096):
                    part = response[i:i + 4096]
                    await message.answer(text = part)
            else:
                await message.answer(text = response)      
            await write_message(str(user_id), str(full_text), response)
                
    except Exception as e:
        raise Exception(f"Error : {e}")
  