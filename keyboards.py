#### keyboards.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('Узнать баланс'))
    keyboard.add(KeyboardButton('Узнать новости'))
    keyboard.add(KeyboardButton('Узнать стоимость по тарифу'))
    keyboard.add(KeyboardButton('Последние платежи'))
    keyboard.add(KeyboardButton('Обратиться в техническую поддержку'))
    keyboard.add(KeyboardButton('Позвонить на абонентский отдел'))
    keyboard.add(KeyboardButton('Отвязать договор'))
    return keyboard

