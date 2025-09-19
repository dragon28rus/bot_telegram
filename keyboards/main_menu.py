from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import Router, types
from db.users import get_user_by_chat_id
from config import SUPPORT_CHAT_ID


router = Router()

async def get_main_menu(chat_id: int) -> ReplyKeyboardMarkup:
    """
    Формирует главное меню (ReplyKeyboard) в зависимости от того,
    авторизован ли пользователь.
    """
    user = await get_user_by_chat_id(chat_id)

    builder = ReplyKeyboardBuilder()

    if user and user.get("contract_id"):
		# Авторизованный пользователь
        builder.row(
            KeyboardButton(text="💰 Узнать баланс"),
            KeyboardButton(text="📊 Текущий тариф")
        )
        builder.row(
            KeyboardButton(text="💳 Последние платежи"),
            KeyboardButton(text="💵 Оплатить услуги")
        )
        builder.row(
            KeyboardButton(text="📰 Новости"),
            KeyboardButton(text="✉️ Техподдержка")
        )
        builder.row(KeyboardButton(text="📞 Позвонить в абонентский отдел"))
        builder.row(KeyboardButton(text="📞 Позвонить в техподдержку"))
        builder.row(KeyboardButton(text="🔓 Отвязать договор"))

    elif str(chat_id) == str(SUPPORT_CHAT_ID):
		# Аккаунт технической поддержки
        builder.row(
            KeyboardButton(text="✉️ Написать абоненту"),
            KeyboardButton(text="✉️ Массовая рассылка")
        )

    else:
		# Неавторизованный пользователь
        builder.row(KeyboardButton(text="🔑 Авторизоваться"))
        builder.row(KeyboardButton(text="✉️ Техподдержка"))
        builder.row(KeyboardButton(text="📞 Позвонить в абонентский отдел"))
        builder.row(KeyboardButton(text="📞 Позвонить в техподдержку"))

    return builder.as_markup(resize_keyboard=True, one_time_keyboard=False)

# ==============================
# ✉️ Техническая поддержка 
# ==============================
async def get_support_menu() -> ReplyKeyboardMarkup:
    """
    Клавиатура для режима общения с техподдержкой.
    """
    ReplyKeyboardBuilder().row(
            KeyboardButton(text="❌ Выйти из техподдержки")
        )
    return ReplyKeyboardBuilder().as_markup(resize_keyboard=True, one_time_keyboard=False)

async def get_auth_menu() -> ReplyKeyboardMarkup:
    """
    Клавиатура для режима авторизации.
    """
    ReplyKeyboardBuilder().row(
        KeyboardButton(text="❌ Выйти из режима авторизации")
        )
    return ReplyKeyboardBuilder().as_markup(resize_keyboard=True, one_time_keyboard=False)