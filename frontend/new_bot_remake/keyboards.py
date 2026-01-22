from aiogram.types import ReplyKeyboardMarkup,KeyboardButton,InlineKeyboardButton,InlineKeyboardMarkup
import os
import sys
from config import PROJECT_ROOT

main_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text = "Chat"),KeyboardButton(text = "Profile")]
])

profile_key_borad = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text = "Subscribe")]
])

buy_sub_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text = "Buy subscribtion")]
])