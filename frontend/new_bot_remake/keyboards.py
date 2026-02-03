from aiogram.types import ReplyKeyboardMarkup,KeyboardButton,InlineKeyboardButton,InlineKeyboardMarkup
import os
import sys
from config import PROJECT_ROOT

main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True,keyboard=[
    [KeyboardButton(text = "Chat"),KeyboardButton(text = "Profile")],
    [KeyboardButton(text = "Reset Context"),KeyboardButton(text = "Help"),KeyboardButton(text = "Support")]
])

profile_key_borad = ReplyKeyboardMarkup(resize_keyboard=True,keyboard=[
    [KeyboardButton(text = "Subscribe"),KeyboardButton(text = "Buy Requests")],
    [KeyboardButton(text = "Back")]
])


buy_sub_keyboard = ReplyKeyboardMarkup(resize_keyboard=True,keyboard=[
    [KeyboardButton(text = "Buy subscribtion"),KeyboardButton(text = "Back")]
])

back_keyboard = ReplyKeyboardMarkup(resize_keyboard=True,keyboard=[
    [KeyboardButton(text = "Back")]
])

buy_req_keyboard = ReplyKeyboardMarkup(resize_keyboard=True,keyboard=[
    [KeyboardButton(text = "5 Requests"),KeyboardButton(text = "20 Requests")],
    [KeyboardButton(text = "10 Requests"),KeyboardButton(text = "Back")]
])

inline_pay = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text = "Pay 250 ⭐",pay = True)]
])


subscrition_keyborad = ReplyKeyboardMarkup(resize_keyboard=True,keyboard=[
    [KeyboardButton(text = "Premium"),KeyboardButton(text = "Basic")],
    [KeyboardButton(text = "Back")]
])