from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from db import is_user_authorized
from logger import logger, set_chat_id

router = Router()

def get_menu_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Обратиться в техническую поддержку"))
    keyboard.add(KeyboardButton("Позвонить в техподдержку"))
    return keyboard

@router.message(Command("menu"))
async def cmd_menu(message: Message):
    set_chat_id(message.from_user.id)
    if not is_user_authorized(message.from_user.id):
        logger.warning("Unauthorized user attempted to access menu")
        await message.answer("Пожалуйста, авторизуйтесь с помощью /start.")
        return
    
    logger.info("Menu accessed")
    await message.answer("Выберите действие:", reply_markup=get_menu_keyboard())