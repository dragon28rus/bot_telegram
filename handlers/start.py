from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from keyboards.main_menu import get_main_menu
from db.users import get_user_by_chat_id
from logger import logger

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    chat_id = message.chat.id
    logger.info(f"Пользователь {chat_id} вызвал /start")

    user = await get_user_by_chat_id(chat_id)

    

    if user and user.get("contract_id"):
        text = (
            f"👋 Добро пожаловать снова!\n"
            f"Ваш договор: <b>{user['contract_id']}</b>\n\n"
            f"Выберите действие:"
        )
    else:
        text = (
            "👋 Добро пожаловать!\n"
            "Для доступа к балансу, тарифам и новостям необходимо авторизоваться.\n\n"
            "Выберите действие:"
        )

    keyboard = await get_main_menu(message.chat.id)

    # Сообщение с основным меню
    await message.answer("👋 Добро пожаловать! Выберите действие:", reply_markup=keyboard)
