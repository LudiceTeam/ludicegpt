from aiogram import Bot,Dispatcher,F,Router
from aiogram.filters import CommandStart,Command
from aiogram.types import Message,File,Video,PhotoSize,LabeledPrice,PreCheckoutQuery,ContentType,CallbackQuery,InlineKeyboardMarkup,InlineKeyboardButton
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
from backend.database.chats_database.chats_core import write_message,get_all_user_messsages,delete_all_messages
#from backend.api import ask_chat_gpt
from backend.database.core import create_deafault_user_data,remove_free_zapros,check_free_zapros_amount,get_amount_of_zaproses,subscribe,set_sub_bac_to_false,get_me,is_user_subbed,buy_zaproses,get_sub_date_end,subscribe_basic,unsub_basic,is_user_subbed_basic,get_last_ref_basic,refil_zap,upadate_last_ref_date,is_user_exists,get_user_referal_count,add_referal
from datetime import timedelta,datetime
from typing import List
from backend.database.state_database.state_core import create_user_state,change_user_state,get_user_state
from backend.database.sale_database.sale_core import cretae_user_sale_table,change_to_sale,does_user_have_sale,give_referal_sub,does_user_have_referal_sub
import time
from io import BytesIO 
import aiohttp
from openai import AsyncOpenAI

router = Router()


reader = easyocr.Reader(["en","ru"],gpu = False) # будут норм сервера поставить True
os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'

@router.message(CommandStart())
async def start_messsage(message:Message):
    welcome_text = """Добро пожаловать в ChatGPT от LudiceTeam!

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
                await message.answer(text = welcome_text,reply_markup=kb.main_keyboard)# вставить сюда норм текст            
                
    else:
        await message.answer(text = welcome_text,reply_markup=kb.main_keyboard)# вставить сюда норм текст            
    
    await create_deafault_user_data(str(user_id))
    await create_user_state(str(user_id))
    await cretae_user_sale_table(str(user_id))
    

async def time_to_give_free_referal_sub(username:str) -> bool:
    user_friends_invited:int = await get_user_referal_count(username)
    if user_friends_invited >= 5:
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
    if is_user_subbed_basic_flag:
        date_now = datetime.now().date()
        user_last_refil_date = await get_last_ref_basic(username)
        
       
        dt_int = await transform_date_to_int(str(date_now))
        last_ref_int = await transform_date_to_int(str(user_last_refil_date))
        
        if dt_int > last_ref_int:
            await refil_zap(username)
            await upadate_last_ref_date(username)
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
            
        
    

@router.message(F.text == "Профиль")
async def profile_handler(message:Message):
    user_name = message.from_user.username
    user_id = message.from_user.id
    await refil_requests_basic_sub(str(user_id))
    await change_user_state(str(user_id),False)
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
            
    
    new_profile_desc = f"""
        Профиль @{user_data[str(user_id)]}:
        
Запросов осталось: {await get_request_text()}

Статус подписки: {await get_user_subscribtion_type()}


Срок истечения подписки: {await get_sub_end_text()}

    """
    if not user_subbed and not await is_user_subbed_basic(str(user_id)):
        await message.answer(
         new_profile_desc,
        reply_markup=kb.profile_key_borad        
        )
    else:
        await message.answer(
         new_profile_desc     
    )

@router.message(F.text == "Реферальная прог")
async def referal_prog(message:Message):
    user_id = str(message.from_user.id)
    user_referal_count = await get_user_referal_count(user_id)
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
        
        

@router.message(F.text == "Подписаться")
async def subscribe_hander(message:Message):
    await message.answer(text = "Выберете тип подписки",reply_markup=kb.subscrition_keyborad)


async def count_sale(price:int) -> int:
    sale:int = int(price * 0.1)
    return price - sale

@router.message(F.text == "Premium")
async def premium_handler(message:Message):
    price = 499
    user_has_sale = await does_user_have_sale(str(message.from_user.id))
    if user_has_sale:
        price = await count_sale(price)
        
    buy_sub_text = f"1) Стоимость: {price} звезд / 30 дней. 2) Лимит: безлимитные запросы 3) Бонус: любая следующая покупка в боте будет со скидкой 10%"
    prices = [LabeledPrice(label=f"{price} ⭐", amount=price)]
    
    inline_pay = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text = f"Заплатить {price} ⭐",pay = True)]
    ])
    
    
    await message.bot.send_invoice(
        chat_id=message.from_user.id,
        title="Premium",
        description=buy_sub_text,
        payload="subscribtion",
        provider_token="410694247:TEST:48b50af2-4c6d-4c87-8d3f-6912d0d8c38a",
        prices=prices,
        currency="XTR",    
        reply_markup=inline_pay
    )
    
@router.message(F.text == "Basic")
async def basic_sub_handler(message:Message):
    price = 199
    user_has_sale = await does_user_have_sale(str(message.from_user.id))
    if user_has_sale:
        price = await count_sale(price)
        
    inline_pay = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text = f"Заплатить {price} ⭐",pay = True)]
    ])
    
    buy_sub_text = f"1) Стоимость: {price} звезд / 30 дней 2) Лимит: 25 запросов в день"
    prices = [LabeledPrice(label=f"{price} ⭐", amount=price)]
    await message.bot.send_invoice(
    chat_id=message.from_user.id,
    title="Basic",
    description=buy_sub_text,
    payload="basic",
    provider_token="410694247:TEST:48b50af2-4c6d-4c87-8d3f-6912d0d8c38a",
    prices=prices,
    currency="XTR",    
    reply_markup=inline_pay
)
    
    
    
requests_buy_text = "Данная покупка предоставляет только фиксированное количество запросов без каких-либо дополнительных привилегий, гарантий приоритета или влияния на обработку запросов."        

@router.message(F.text == "Купить Запросы")
async def buy_req_handler(message:Message):
    await message.answer(text = "Выберете то количество запросов, которое хотите купить.",reply_markup=kb.buy_req_keyboard)

@router.message(F.text == "5 Запросов")
async def buy_5_req_handler(message:Message):
    price = 10
    user_has_sale = await does_user_have_sale(str(message.from_user.id))
    if user_has_sale:
        price = await count_sale(price)
        
    inline_pay = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text = f"Заплатить {price} ⭐",pay = True)]
    ])
    
    prices = [LabeledPrice(label=f"{price} ⭐", amount=price)]
    await message.bot.send_invoice(
    chat_id=message.from_user.id,
    title="5 Запросов",
    description=requests_buy_text,
    payload="ludice_team_5",
    provider_token="410694247:TEST:48b50af2-4c6d-4c87-8d3f-6912d0d8c38a",
    prices=prices,
    currency="XTR",    
    reply_markup=inline_pay
    )
    
@router.message(F.text == "10 Запросов")
async def buy_10_req_handler(message:Message):
    price = 19
    user_has_sale = await does_user_have_sale(str(message.from_user.id))
    if user_has_sale:
        price = await count_sale(price)
        
    inline_pay = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text = f"Заплатить {price} ⭐",pay = True)]
    ])
    
    prices = [LabeledPrice(label=f"{price} ⭐", amount=price)]
    await message.bot.send_invoice(
    chat_id=message.from_user.id,
    title="10 Запросов",
    description=requests_buy_text,
    payload="ludice_team_10",
    provider_token="410694247:TEST:48b50af2-4c6d-4c87-8d3f-6912d0d8c38a",
    prices=prices,
    currency="XTR",    
    reply_markup=inline_pay
    )

@router.message(F.text == "20 Запросов")
async def buy_20_req_handler(message:Message):
    price = 37
    user_has_sale = await does_user_have_sale(str(message.from_user.id))
    if user_has_sale:
        price = await count_sale(price)
        
    inline_pay = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text = f"Заплатить {price} ⭐",pay = True)]
    ])
    
    prices = [LabeledPrice(label=f"{price} ⭐", amount=price)]
    await message.bot.send_invoice(
    chat_id=message.from_user.id,
    title="20 Запросов",
    description=requests_buy_text,
    payload="ludice_team_20",
    provider_token="410694247:TEST:48b50af2-4c6d-4c87-8d3f-6912d0d8c38a",
    prices=prices,
    currency="XTR",    
    reply_markup=inline_pay
    )


    
   
@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)

@router.message(F.successful_payment)
async def succesful_payment_handler(message:Message):
    
    payment = message.successful_payment
    user_id = str(message.from_user.id)
    invoice = payment.invoice_payload.split("_")
    
    
    if "ludice_team" in payment.invoice_payload:
        await buy_zaproses(user_id,int(invoice[-1]))
        await message.answer(text = f"✅ Вы купили {invoice[-1]} запросов. Спасибо за покупку. Приятного пользования.")
    elif "subscribtion" in payment.invoice_payload:
        await subscribe(user_id)
        await change_to_sale(user_id)
        await message.answer("✅ Вы успешно подписались на Premium подписку. Спасибо за покупку. Приятного пользования.")
    elif "basic" in payment.invoice_payload:
        await subscribe_basic(user_id)
        await message.answer("✅ Вы успешно подписались на Basic. Спасибо за покупку. Приятного пользования.")
            
    else:
        await message.answer("Что то пошло не так. Попробуйте снова.")
    
     

@router.message(F.text == "Назад")
async def back(message:Message):
    await message.answer(text = "Вы вернулись в главное меню",reply_markup=kb.main_keyboard)


    
@router.message(F.text == "Сбросить Контекст")
async def reset(message:Message):
    user_id = str(message.from_user.id)
    await refil_requests_basic_sub(str(user_id))
    await delete_all_messages(user_id)
    await message.answer(text = "✅ История отчищена.")

@router.message(F.text == "Помощь")
async def help(message:Message):
    help_text = """🎯 Основные разделы (главное меню):

    Чат — начать общение со мной. Вы можете задавать вопросы, обсуждать идеи, получать консультации.

    Профиль — управление вашим аккаунтом: подписка, покупка запросов, статистика.

    Сбросить контекст — очистить историю нашего диалога. Используйте, если хотите начать новый разговор «с чистого листа».

    Помощь — это сообщение.

    Поддержка — связаться с техподдержкой по вопросам работы бота.

👤 Профиль:
В разделе Профиль вы можете:

    Подписаться — выбрать тариф (Basic или Premium) для расширения возможностей.

    Купить Запросы — приобрести пакеты запросов, если у вас их не хватает.

💎 Тарифы и запросы:

    Basic — базовая подписка с увеличенным лимитом.

    Premium — полный доступ с максимальными возможностями.

    Запросы — можно купить отдельно пакетами по 5, 10 или 20 штук.

💡 Советы:

    Используйте кнопку «Назад», чтобы вернуться в предыдущее меню.

    Чтобы оплатить подписку или запросы, нажмите на соответствующую кнопку в меню и следуйте инструкциям.

    Если что-то пошло не так, попробуйте «Сбросить контекст» или обратитесь в «Поддержку».

❓ Остались вопросы?
Нажмите кнопку «Поддержка» в главном меню — наша команда поможет вам!

Для навигации используйте кнопки меню 👇
"""
    await message.answer(text = help_text)



@router.message(F.text == "Поддержка")
async def support_handler(message:Message):
    
    await message.answer(text =  "Отправьте ваш вопрос вот этому пользователю : @kksndid_support")
        


    

@router.message(F.text == "Чат")
async def chat_handler(message:Message):
    user_id = message.from_user.id
    await change_user_state(str(user_id),True)
    await refil_requests_basic_sub(str(user_id))
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
        
   
    await message.answer("Привет, я твой помощник ChatGPT от LudiceTeam в Telegram") # написать норм тектс для бота  типо просто первое сообщение в чате

from frontend.new_bot_remake.keys import OPEN_AI_KEY

client = AsyncOpenAI(
    api_key=OPEN_AI_KEY,
    base_url="https://openrouter.ai/api/v1",
    timeout=30.0,
    max_retries=2
)

async def ask_chat_gpt(request: str) -> str:
    """Асинхронная версия через официальный SDK"""
    try:
        # Ограничиваем длину запроса
        request = request[:3000]
        
        response = await client.responses.create(
            model="gpt-5-nano", 
            input=request
        )
        
        result = response.output_text.strip()
        if not result:
            return "🤔 GPT вернул пустой ответ."
        
        return result[:4000]
        
    except Exception as e:
        print(f"OpenAI SDK error: {e}")
        return f"❌ Ошибка: {str(e)[:100]}"



@router.message(F.text & ~F.command)
async def answer_messages(message:Message):
        user_state = await get_user_state(str(message.from_user.id))
        await refil_requests_basic_sub(str(message.from_user.id))
        if user_state:
            user_id = message.from_user.id
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
                    
            
            think_message = await message.answer("Думаю...")
            user_messages = await get_all_user_messsages(str(user_id))
            is_user_subbed_ = await is_user_subbed(str(user_id))
            
            if not is_user_subbed_:
                user_free_req = await get_amount_of_zaproses(str(user_id))
                user_basic_sub = await is_user_subbed_basic(str(user_id))
                if user_free_req == 0:
                    if user_basic_sub:
                        await think_message.delete()
                        await message.answer(text = "У вас на сегодня закончились запросы.Попробуйте снова завтра")
                    else:
                        await think_message.delete()
                        await message.answer(text = "У вас не осталось бесплатных запросов.Купить подписку вы можете перейдя в профиль")
                else:
                    await remove_free_zapros(str(user_id))
                    response = await ask_chat_gpt(f"Вот все сообщение пользователя что бы тебе было легче его понимать : {user_messages},это его история сообщений что бы ты его понимал.Ты отвечаешь кратко и по делу. А вот его текущие сообщение : {str(message.text)}")
                    try:
                        await think_message.delete()
                    except Exception as e:
                        raise Exception(f"Error : {e}")
                    time.sleep(0.5)
                    
                    
                    if len(response) > 4096:
                        for i in range(0,len(response),4096):
                            part = response[i:i + 4096]
                            await message.answer(text = part)
                    else:
                        await message.answer(text = response)        
                    await write_message(str(user_id),str(message.text),response)
            else:
                response = ask_chat_gpt(f"Вот все сообщение пользователя что бы тебе было легче его понимать : {user_messages},это его история сообщений что бы ты его понимал.Ты отвечаешь кратко и по делу. А вот его текущие сообщение : {str(message.text)}")
                try:
                    await think_message.delete()
                except Exception as e:
                    raise Exception(f"Error : {e}")
                time.sleep(0.5)
                
                
                if len(response) > 4096:
                    for i in range(0,len(response),4096):
                        part = response[i:i + 4096]
                        await message.answer(text = part)
                else:
                    await message.answer(text = response)        
                await write_message(str(user_id),str(message.text),response)
        else:
            await message.answer(text="❌ Команда не распознана. Чтобы включить режим чата, нажмите кнопку «Чат».")
                    
 

async def extract_text_from_image_new(image_bytes: bytes) -> str:
   
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        return ""
    
   
    height, width = img.shape[:2]
    if max(height, width) > 800:
        scale = 800 / max(height, width)
        img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    
   
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    
   
    texts = []
    

    result1 = reader.readtext(enhanced, paragraph=True, detail=0)
    if result1:
        texts.append("\n".join(result1))
    
   
    result2 = reader.readtext(enhanced, paragraph=False, detail=0)
    if result2:
        texts.append("\n".join(result2))
    
 
    result3 = reader.readtext(img, paragraph=True, detail=0)
    if result3:
        texts.append("\n".join(result3))
    
   
    if texts:
        best_text = max(texts, key=len)
        return best_text.strip()
    
    return ""

def four_point_transform(image, pts):
    """Выравнивает перспективу по 4 точкам"""
    rect = order_points(pts)
    (tl, tr, br, bl) = rect
    
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))
    
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))
    
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")
    
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    return warped

def order_points(pts):
  
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

async def is_user_has_free_req(username:str) -> bool:
    is_user_subbed_flag:bool = is_user_subbed(username)
    if not is_user_subbed_flag:
        #basic_sub = await is_user_subbed_basic(username)
        user_free_req = await get_amount_of_zaproses(username)
        if user_free_req == 0:
            return True
        return False
    return False
    
            
@router.message(F.photo)
async def answer_with_photo(message: Message):
    user_state = await get_user_state(str(message.from_user.id))
    await refil_requests_basic_sub(str(message.from_user.id))
    if user_state:
        user_id = message.from_user.id
        res_unsub: bool = await unsub_full_func(str(user_id))
        
        has_req:bool = await is_user_has_free_req(str(user_id))
        if has_req:
            basic_sub = await is_user_subbed_basic(str(user_id))
            if basic_sub:
                await think_message.delete()
                await message.answer(text = "У вас на сегодня закончились запросы.Попробуйте снова завтра")
                return
            else:
                await think_message.delete()
                await message.answer(text = "У вас не осталось бесплатных запросов.Купить подписку вы можете перейдя в профиль")
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
        
        think_message = await message.answer("Думаю...")
        photo = message.photo[-1]
        user_messages = await get_all_user_messsages(str(user_id))
        file = await message.bot.get_file(photo.file_id)
        
       
        file_bytes_io = BytesIO()
        await message.bot.download_file(file.file_path, file_bytes_io)
        file_bytes_io.seek(0)
        image_bytes = file_bytes_io.read()
        
       
      
        result_text = await extract_text_from_image_new(image_bytes)
        
       # await message.answer(text = f"Вот текст с картинки  : {result_text}")
        
        if not result_text:
            await message.answer(text="Текст с фотографии не извлечен")
            await think_message.delete()
            return
        
      
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                await message.bot.download_file(file.file_path, tmp_file.name)
                results = reader.readtext(tmp_file.name)
            os.unlink(tmp_file.name)
            
            
            if results:
                text_lines = []
                for (bbox, text, prob) in results:
                    if prob > 0.3:
                        text_lines.append(text)
                old_method_text = "\n".join(text_lines)
                
               
                if len(old_method_text) > len(result_text):
                    result_text = old_method_text
        except:
            pass 
        
        is_user_subbed_ = await is_user_subbed(str(user_id))
        
        if not is_user_subbed_:
            user_free_req = await get_amount_of_zaproses(str(user_id))
            user_basic_sub = await is_user_subbed_basic(str(user_id))
            if user_free_req == 0:
                if user_basic_sub:
                    await think_message.delete()
                    await message.answer(text = "У вас на сегодня закончились запросы.Попробуйте снова завтра")
                else:
                    await think_message.delete()
                    await message.answer(text = "У вас не осталось бесплатных запросов.Купить подписку вы можете перейдя в профиль")
            else:
                full_text: str = str(message.text) + "\n" + (message.caption or "") + "\n" + result_text
                await remove_free_zapros(str(user_id))
                response = ask_chat_gpt(f"Вот все сообщение пользователя что бы тебе было легче его понимать : {user_messages},это его история сообщений что бы ты его понимал.Ты отвечаешь кратко и по делу. А вот его текущие сообщение : {full_text}")
                try:
                    await think_message.delete()
                except Exception as e:
                    raise Exception(f"Error: {e}")
                time.sleep(0.5)
                
                
                if len(response) > 4096:
                    for i in range(0,len(response),4096):
                        part = response[i:i + 4096]
                        await message.answer(text = part)
                else:
                    await message.answer(text = response)        
                await write_message(str(user_id), str(full_text), response)
               
        else:
            full_text: str = str(message.text) + "\n" + (message.caption or "") + "\n" + result_text
            response = ask_chat_gpt(f"Вот все сообщение пользователя что бы тебе было легче его понимать : {user_messages},это его история сообщений что бы ты его понимал.Ты отвечаешь кратко и по делу. А вот его текущие сообщение : {full_text}")
            try:
                await think_message.delete()
            except Exception as e:
                raise Exception(f"Error: {e}")
            time.sleep(0.5)
            
            if len(response) > 4096:
                    for i in range(0,len(response),4096):
                        part = response[i:i + 4096]
                        await message.answer(text = part)
            else:
                await message.answer(text = response)
            await write_message(str(user_id), str(full_text), response)
    else:
        await message.answer(text="❌ Команда не распознана. Чтобы включить режим чата, нажмите кнопку «Чат».")        
            
            
            
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
async def answer_with_document(message: Message):
    user_state = await get_user_state(str(message.from_user.id))
    await refil_requests_basic_sub(str(message.from_user.id))
    if user_state:
        user_id = message.from_user.id
        res_unsub: bool = await unsub_full_func(str(user_id))
        if res_unsub:
            await message.answer( text="📅 Ваша подписка закончилась.\n\n"
         "🔓 Чтобы продолжить пользоваться платным функционалом, вам нужно оформить её снова.\n\n"
         "🆓 Вы можете пользоваться ботом в пределах бесплатного тарифа.\n\n"
         "Благодарим за поддержку!")
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
                await message.answer(text = "У вас не осталось бесплатных запросов.Купить подписку вы можете перейдя в профиль")
                return
            
        free_ref_sub = await  time_to_give_free_referal_sub(str(user_id))
        if free_ref_sub:
            ref_text = """✅ Basic подписка получена!
    ✅ Награда за 5 приглашённых друзей
    ✅ Активна 30 дней"""
            await message.answer(text = ref_text)    
            
        
        document = message.document
        
        filename = document.file_name.lower()
        
        #file_bytes = await message.bot.download_file(document.file_id)
        
        file_info = await message.bot.get_file(document.file_id)
        
        
        user_messages = await get_all_user_messsages(str(message.from_user.id))
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename).suffix) as tmp_fi:
            await message.bot.download_file(file_info.file_path,tmp_fi.name)
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
                await message.answer(text="Формат файла не поддерживается")
                return
            
            if os.path.exists(file_path):
                os.unlink(file_path)
            
            if text == "" or not text or text is None:
                await message.asnwer(text="Текст с данного файда не был извлечен")    
                
            is_user_subbed_ = await is_user_subbed(str(user_id))
            if not is_user_subbed_:
                user_req = await get_amount_of_zaproses(str(user_id))
                user_basic_sub = await is_user_subbed_basic(str(user_id))
                if user_req == 0:
                    if user_basic_sub:
                        await think_message.delete()
                        await message.answer(text = "У вас на сегодня закончились запросы.Попробуйте снова завтра")
                    else:
                        await think_message.delete()
                        await message.answer(text = "У вас не осталось бесплатных запросов.Купить подписку вы можете перейдя в профиль или просто докупить запросы.")
                else:
                    full_text: str = str(message.text) + "\n" + str(message.caption) + "\n" + text
                    await remove_free_zapros(str(user_id))
                    response = ask_chat_gpt(f"Вот все сообщение пользователя что бы тебе было легче его понимать : {user_messages},это его история сообщений что бы ты его понимал.Ты отвечаешь кратко и по делу. А вот его текущие сообщение : {full_text}")
                    try:
                        await think_message.delete()
                    except Exception as e:
                        raise Exception(f"Error : {e}")
                    
                    time.sleep(0.5)
                    if len(response) > 4096:
                        for i in range(0,len(response),4096):
                            part = response[i:i + 4096]
                            await message.answer(text = part)
                    else:
                        await message.answer(text = response)
                    await write_message(str(user_id), str(full_text), response)
            else:
                full_text = str(message.text) + "\n" + str(message.caption) + "\n" + text
                response = ask_chat_gpt(f"Вот все сообщение пользователя что бы тебе было легче его понимать : {user_messages},это его история сообщений что бы ты его понимал.Ты отвечаешь кратко и по делу. А вот его текущие сообщение : {full_text}")
                try:
                    await think_message.delete()
                except Exception as e:
                    raise Exception(f"Error : {e}")
                
                time.sleep(0.5)
                if len(response) > 4096:
                    for i in range(0,len(response),4096):
                        part = response[i:i + 4096]
                        await message.answer(text = part)
                else:
                    await message.asnwer(text = response)      
                await write_message(str(user_id), str(full_text), response)
                    
        except Exception as e:
            raise Exception(f"Error : {e}")
    else:
        await message.answer(text="❌ Команда не распознана. Чтобы включить режим чата, нажмите кнопку «Чат».")    







# добавить иконки к кнопкам
