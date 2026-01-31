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
from backend.database.chats_database.chats_core import write_message,get_all_user_messsages,delete_all_messages
from backend.api import ask_chat_gpt
from backend.database.core import create_deafault_user_data,remove_free_zapros,check_free_zapros_amount,get_amount_of_zaproses,subscribe,set_sub_bac_to_false,get_me,unsub_all_users_whos_sub_is_ending_today,is_user_subbed,buy_zaproses,get_sub_date_end
from datetime import timedelta,datetime
from typing import List
from backend.database.state_database.state_core import create_user_state,change_user_state,get_user_state
import time
from io import BytesIO 

router = Router()


reader = easyocr.Reader(["en","ru"],gpu = False) # будут норм сервера поставить True
os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'

@router.message(CommandStart())
async def start_messsage(message:Message):
    user_name = message.from_user.username
    user_id = message.from_user.id
    await create_deafault_user_data(str(user_id))
    await create_user_state(str(user_id))
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
    await change_user_state(str(user_id),False)
    res_unsub:bool = await unsub_full_func(str(user_id))
    if res_unsub:
        await message.asnwer(text = "Ваша подписка закончилась.Что бы продолжить пользоваться премиум функционалом вам нужно снова ее оформить.Вы можете пользоваться ботом в пределе бесплатного тарифа.Благодарим за поддержку")
    user_data = await get_me(str(user_id))
    user_data[str(user_id)] = user_name
    user_subbed:bool = await  is_user_subbed(str(user_id))
    result = f"""
        Profile of @{user_data[str(user_id)]}
        Requests : {user_data["Free requests"]}
        
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
        start_parameter="subscribtion",
        need_email=True, 
        need_phone_number=False,
        is_flexible=False, 
        #reply_markup=kb.back_keyboard
    )


@router.message(F.text == "Buy Requests")
async def buy_req_handler(message:Message):
    await message.answer(text = "Выберете то количество запросов,которое хотите купить",reply_markup=kb.buy_req_keyboard) 

@router.message(F.text == "5 Requests")
async def buy_5_req_handler(message:Message):
    await message.answer(text = "Текст для покупки 5 запросов")
    # инмвойс в звездах на покупку 5 ти запросов
    
@router.message(F.text == "20 Requests")
async def buy_20_req_handler(message:Message):
    await message.answer(text = "Текст для покупки 20 запросов")
    # инмвойс в звездах на покупку 20 ти запросов
   
@router.message(F.text == "50 Requests")
async def buy_50_req_handler(message:Message):
    await message.answer(text = "Текст для покупки 50 запросов")
    # инмвойс в звездах на покупку 50 ти запросов

@router.message(F.text == "100 Requests")
async def buy_100_req_handler(message:Message):
    await message.answer(text = "Текст для покупки 100 запросов")
    # инмвойс в звездах на покупку 5 ти запросов
        
     

@router.message(F.successful_payment)
async def succesful_payment_handler(message:Message):
    payment = message.successful_payment
    user_id = str(message.from_user.id)
    invoice = payment.split('_')
    if "ludice_team" in payment:
        await buy_zaproses(user_id,int(invoice["-1"]))
        await message.answer(text = f"Вы купили {invoice["-1"]} запросов. Спасибо за покупку. Приятного пользования.")
    elif "subscribtion" in invoice:
        await subscribe(user_id)
        await message.answer("Вы успешно подписались. Спасибо за покупку. Приятного пользования.")
    
@router.message(F.text == "Reset Context")
async def reset(message:Message):
    user_id = str(message.from_user.id)
    await message.answer(text = "Вы удалите все итсторию переписки,после этого ChatGPT создаст новый чат")
    await delete_all_messages(user_id)
    await message.answer(text = "История отчищена.Можете продолжать пользоваться")

@router.message(F.text == "Help")
async def help(message:Message):
    await message.answer(text = "Help")



@router.message(F.text == "Chat")
async def chat_handler(message:Message):
    user_id = message.from_user.id
    await change_user_state(str(user_id),True)
    res_unsub:bool = await unsub_full_func(str(user_id))
    if res_unsub:
        await message.asnwer(text = "Ваша подписка закончилась.Что бы продолжить пользоваться премиум функционалом вам нужно снова ее оформить.Вы можете пользоваться ботом в пределе бесплатного тарифа.Благодарим за поддержку")
   
    await message.answer("Привет я твой помошник ChatGPT от LudiceTeam в Telegram") # написать норм тектс для бота  типо просто первое сообщение в чате

@router.message(F.text & ~F.command)
async def answer_messages(message:Message):
        user_state = await get_user_state(str(message.from_user.id))
        if user_state:
            user_id = message.from_user.id
            res_unsub:bool = await unsub_full_func(str(user_id))
            if res_unsub:
                await message.asnwer(text = "Ваша подписка закончилась.Что бы продолжить пользоваться премиум функционалом вам нужно снова ее оформить.Вы можете пользоваться ботом в пределе бесплатного тарифа.Благодарим за поддержку")
            think_message = await message.answer("Думаю...")
            user_messages = await get_all_user_messsages(str(user_id))
            is_user_subbed_ = await is_user_subbed(str(user_id))
            if not is_user_subbed_:
                user_free_req = await get_amount_of_zaproses(str(user_id))
                if user_free_req == 0:
                    await message.answer(text = "У вас не осталось бесплатных запросов.Купить подписку вы можете перейдя в профиль")
                else:
                    await remove_free_zapros(str(user_id))
                    response = ask_chat_gpt(str(message.text) + f"Вот все сообщение пользователя что бы тебе было легче его понимать : {user_messages},не нужно на это ничего отвечать просто это сообщения человека что бы сохранился контекст")
                    try:
                        await think_message.delete()
                    except Exception as e:
                        raise Exception(f"Error : {e}")
                    time.sleep(0.5)
                    await write_message(str(user_id),str(message.text),response)
                    await message.answer(text = response)
            else:
                try:
                    await think_message.delete()
                except Exception as e:
                    raise Exception(f"Error : {e}")
                time.sleep(0.5)
                response = ask_chat_gpt(str(message.text) + f"Вот все сообщение пользователя что бы тебе было легче его понимать : {user_messages}")
                await write_message(str(user_id),str(message.text),response)
                await message.answer(text = response)
                    
 

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
            
@router.message(F.photo)
async def answer_with_photo(message: Message):
    user_state = await get_user_state(str(message.from_user.id))
    if user_state:
        user_id = message.from_user.id
        res_unsub: bool = await unsub_full_func(str(user_id))
        if res_unsub:
            await message.answer(text="Ваша подписка закончилась. Чтобы продолжить пользоваться премиум функционалом вам нужно снова ее оформить. Вы можете пользоваться ботом в пределах бесплатного тарифа. Благодарим за поддержку")
        
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
            if user_free_req == 0:
                await message.answer(text="У вас не осталось бесплатных запросов. Купить подписку вы можете перейдя в профиль")
                await think_message.delete()
            else:
                full_text: str = str(message.text) + "\n" + (message.caption or "") + "\n" + result_text
                await remove_free_zapros(str(user_id))
                response = ask_chat_gpt(str(full_text) + f"Вот все сообщения пользователя чтобы тебе было легче его понимать : {user_messages}")
                try:
                    await think_message.delete()
                except Exception as e:
                    raise Exception(f"Error: {e}")
                time.sleep(0.5)
                await write_message(str(user_id), str(full_text), response)
                await message.answer(text=response)
        else:
            full_text: str = str(message.text) + "\n" + (message.caption or "") + "\n" + result_text
            response = ask_chat_gpt(str(full_text) + f"Вот все сообщения пользователя чтобы тебе было легче его понимать: {user_messages}")
            try:
                await think_message.delete()
            except Exception as e:
                raise Exception(f"Error: {e}")
            time.sleep(0.5)
            await write_message(str(user_id), str(full_text), response)
            await message.answer(text=response)
            
            
            
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
    if user_state:
        user_id = message.from_user.id
        res_unsub: bool = await unsub_full_func(str(user_id))
        if res_unsub:
            await message.answer(text="Ваша подписка закончилась.Что бы продолжить пользоваться премиум функционалом вам нужно снова ее оформить.Вы можете пользоваться ботом в пределе бесплатного тарифа.Благодарим за поддержку")
        think_message = await message.answer("Думаю...")
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
                if user_req == 0:
                    await message.answer(text="У вас не осталось бесплатных запросов.Купить подписку вы можете перейдя в профиль")
                else:
                    full_text: str = str(message.text) + "\n" + str(message.caption) + "\n" + text
                    await remove_free_zapros(str(user_id))
                    response = ask_chat_gpt(str(full_text) + f"Вот все сообщение пользователя что бы тебе было легче его понимать : {user_messages}")
                    try:
                        await think_message.delete()
                    except Exception as e:
                        raise Exception(f"Error : {e}")
                    time.sleep(0.5)
                    await write_message(str(user_id), str(full_text), response)
                    await message.answer(text=response)
            else:
                full_text = str(message.text) + "\n" + str(message.caption) + "\n" + text
                response = ask_chat_gpt(str(full_text + f"Вот все сообщение пользователя что бы тебе было легче его понимать : {user_messages}"))
                try:
                    await think_message.delete()
                except Exception as e:
                    raise Exception(f"Error : {e}")
                time.sleep(0.5)
                await write_message(str(user_id), str(full_text), response)
                await message.answer(text=response)                
                    
        except Exception as e:
            raise Exception(f"Error : {e}")


#сделать разные цены что можно купить отдельно просто запросы