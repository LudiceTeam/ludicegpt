from aiogram import Bot,Dispatcher,F,Router
from aiogram.filters import CommandStart,Command
from aiogram.types import Message,File,Video,PhotoSize
import aiogram
import keyboards as kb
from backend.database.core import create_deafault_user_data,remove_free_zapros,check_free_zapros_amount,get_amount_of_zaproses,subscribe,set_sub_bac_to_false,get_me,unsub_all_users_whos_sub_is_ending_today

import sys
import os


current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir) 

sys.path.insert(0, project_root)

router = Router()




@router.message(CommandStart())
async def start_messsage(message:Message):
    user_name = message.from_user.username
    user_id = message.from_user.id
    await create_deafault_user_data(str(user_id))
    await message.answer("Welcome")# вставить сюда норм текст

@router.message(F.text == "Profile")
async def profile_handler(message:Message):
    user_name = message.from_user.username
    user_id = message.from_user.id
    user_data = get_me(str(user_id))
    user_data[str(user_id)] = user_name
    await message.answer(
        user_data        
    )
    
    
       