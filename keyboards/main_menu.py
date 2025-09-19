from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram import Router
from db.users import get_user_by_chat_id
from config import SUPPORT_CHAT_ID

router = Router()

async def get_main_menu(chat_id: int) -> ReplyKeyboardMarkup:
    """
    Формирует главное меню (ReplyKeyboard) в зависимости от того,
    авторизован ли пользователь.
    """
    user = await get_user_by_chat_id(chat_id)

    if user and user.get("contract_id"):
        # Авторизованный пользователь
        keyboard = [
            [KeyboardButton(text="💰 Узнать баланс")],
            [KeyboardButton(text="📊 Текущий тариф")],
            [KeyboardButton(text="💳 Последние платежи")],
            [KeyboardButton(text="💵 Оплатить услуги")],
            [KeyboardButton(text="📰 Новости")],
            [KeyboardButton(text="✉️ Техподдержка")],
            [KeyboardButton(text="📞 Позвонить в абонентский отдел")],
            [KeyboardButton(text="📞 Позвонить в техподдержку")],
            [KeyboardButton(text="🔓 Отвязать договор")],
        ]
    elif {chat_id} == {SUPPORT_CHAT_ID}:
        # Аккаунт технической поддержки
        keyboard = [
            [KeyboardButton(text="✉️ Написать абоненту")],
            [KeyboardButton(text="✉️ Масовая рассылка")],
        ]
    else:
        # Неавторизованный пользователь
        keyboard = [
            [KeyboardButton(text="🔑 Авторизоваться")],
            [KeyboardButton(text="✉️ Техподдержка")],
            [KeyboardButton(text="📞 Позвонить в абонентский отдел")],
            [KeyboardButton(text="📞 Позвонить в техподдержку")],
        ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )

# ==============================
# ✉️ Техническая поддержка 
# ==============================
async def get_support_menu() -> ReplyKeyboardMarkup:
    """
    Клавиатура для режима общения с техподдержкой.
    """
    keyboard = [
        [KeyboardButton(text="❌ Выйти из техподдержки")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )

async def get_auth_menu() -> ReplyKeyboardMarkup:
    """
    Клавиатура для режима авторизации.
    """
    keyboard = [
        [KeyboardButton(text="❌ Выйти из режима авторизации")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )