from aiogram.types import ReplyKeyboardMarkup,KeyboardButton,InlineKeyboardButton,InlineKeyboardMarkup
import os
import sys
from config import PROJECT_ROOT

main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True,keyboard=[
    [KeyboardButton(text = "Чат"),KeyboardButton(text = "Профиль"),KeyboardButton(text = "Реферальная программа")],
    [KeyboardButton(text = "Сбросить Контекст"),KeyboardButton(text = "Помощь"),KeyboardButton(text = "Поддержка"),KeyboardButton(text = "Выбрать Модель")]
])

subcribtion_key_board = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text = "Подписаться Premium",callback_data = "subscribe_premium")],
    [InlineKeyboardButton(text = "Купить Запросы",callback_data = "buy_requests")],
    [InlineKeyboardButton(text = "Подписаться Basic",callback_data = "subscribe_basic")]
])



back_keyboard = ReplyKeyboardMarkup(resize_keyboard=True,keyboard=[
    [KeyboardButton(text = "Назад")]
])

buy_req_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text = "5 Запросов",callback_data="5_req")],
    [InlineKeyboardButton(text = "10 Запросов",callback_data="10 req")],
    [InlineKeyboardButton(text = "20 Запросов",callback_data="20 req")]
])

inline_pay = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text = "Заплатить 250 ⭐",pay = True)]
])




inline_pay_basic = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text = "Заплатить 199 ⭐",pay = True)]
])


choose_ai_keyboard = InlineKeyboardMarkup(inline_keyboard =  [
    [InlineKeyboardButton(text = "Gemini 3",callback_data = "google/gemini-3-flash-preview"),InlineKeyboardButton(text = "Gemini 2",callback_data="google/gemini-2.5-flash")]
])