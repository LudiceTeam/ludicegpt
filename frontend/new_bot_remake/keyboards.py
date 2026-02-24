from aiogram.types import ReplyKeyboardMarkup,KeyboardButton,InlineKeyboardButton,InlineKeyboardMarkup
import os
import sys
from config import PROJECT_ROOT

main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True,keyboard=[
    [KeyboardButton(text = "Чат"),KeyboardButton(text = "Профиль"),KeyboardButton(text = "Реферальная программа")],
    [KeyboardButton(text = "Сбросить Контекст"),KeyboardButton(text = "Помощь"),KeyboardButton(text = "Поддержка"),KeyboardButton(text = "Выбрать Модель")]
])

profile_key_borad = ReplyKeyboardMarkup(resize_keyboard=True,keyboard=[
    [KeyboardButton(text = "Подписаться"),KeyboardButton(text = "Купить Запросы")],
    [KeyboardButton(text = "Назад")]
])



back_keyboard = ReplyKeyboardMarkup(resize_keyboard=True,keyboard=[
    [KeyboardButton(text = "Назад")]
])

buy_req_keyboard = ReplyKeyboardMarkup(resize_keyboard=True,keyboard=[
    [KeyboardButton(text = "5 Запросов"),KeyboardButton(text = "10 Запросов")],
    [KeyboardButton(text = "20 Запросов"),KeyboardButton(text = "Назад")]
])

inline_pay = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text = "Заплатить 250 ⭐",pay = True)]
])


subscrition_keyborad = ReplyKeyboardMarkup(resize_keyboard=True,keyboard=[
    [KeyboardButton(text = "Premium"),KeyboardButton(text = "Basic")],
    [KeyboardButton(text = "Назад")]
])


inline_pay_basic = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text = "Заплатить 199 ⭐",pay = True)]
])