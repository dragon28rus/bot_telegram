from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.types import Message

from keyboards.main_menu import get_main_menu
from db.users import get_user_by_chat_id
from logger import logger

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    """
    Обработчик команды /start.
    Отправляет пользователю приветствие и динамическое главное меню.
    """
    chat_id = message.chat.id

    # Логируем запуск
    logger.info(f"Пользователь {chat_id} вызвал /start")

    # Проверяем есть ли запись о пользователе в БД
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
            "Для доступа к балансу и тарифам необходимо авторизоваться.\n\n"
            "Выберите действие:"
        )

    # Динамически формируем меню
    keyboard = await get_main_menu(chat_id)

    await message.answer(text, reply_markup=keyboard)
