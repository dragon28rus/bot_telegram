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

    if user and user.get("contract_title"):
        text = (
            f"👋 Добро пожаловать снова!\n"
            f"Ваш договор: <b>{user['contract_title']}</b>\n\n"
            f"Выберите действие:"
        )
    else:
        text = (
            "👋 Добро пожаловать!\n"
            "Для доступа к балансу, тарифам и новостям необходимо авторизоваться.\n\n"
            "Выберите действие:"
        )

    keyboard = await get_main_menu(chat_id)

    # Сообщение с динамическим текстом
    await message.answer(text, reply_markup=keyboard)
