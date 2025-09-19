from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardBuilder, types
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

    builder = ReplyKeyboardBuilder()

    if user and user.get("contract_id"):
        # Авторизованный пользователь
        builder.row(
            types.KeyboardButton(text="💰 Узнать баланс"),
            types.KeyboardButton(text="📊 Текущий тариф")
        )
        builder.row(
            types.KeyboardButton(text="💳 Последние платежи"),
            types.KeyboardButton(text="💵 Оплатить услуги")
        )
        builder.row(
            types.KeyboardButton(text="📰 Новости"),
            types.KeyboardButton(text="✉️ Техподдержка")
        )
        builder.row(
            types.KeyboardButton(text="📞 Позвонить в абонентский отдел")
        )
        builder.row(
            types.KeyboardButton(text="📞 Позвонить в техподдержку")
        )
        builder.row(
            types.KeyboardButton(text="🔓 Отвязать договор")
        )
        '''
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
        '''
    elif {chat_id} == {SUPPORT_CHAT_ID}:
        # Аккаунт технической поддержки
        builder.row(
            types.KeyboardButton(text="✉️ Написать абоненту"),
            types.KeyboardButton(text="✉️ Масовая рассылка")
        )
        '''
        keyboard = [
            [KeyboardButton(text="✉️ Написать абоненту")],
            [KeyboardButton(text="✉️ Масовая рассылка")],
        ]
        '''
    else:
        # Неавторизованный пользователь
        builder.row(
            types.KeyboardButton(text="🔑 Авторизоваться")
        )
        builder.row(
            types.KeyboardButton(text="✉️ Техподдержка")
        )
        builder.row(
            types.KeyboardButton(text="📞 Позвонить в абонентский отдел")
        )
        builder.row(
            types.KeyboardButton(text="📞 Позвонить в техподдержку")
        )
        '''
        keyboard = [
            [KeyboardButton(text="🔑 Авторизоваться")],
            [KeyboardButton(text="✉️ Техподдержка")],
            [KeyboardButton(text="📞 Позвонить в абонентский отдел")],
            [KeyboardButton(text="📞 Позвонить в техподдержку")],
        ]
        '''

    return ReplyKeyboardMarkup(
        keyboard=builder,
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