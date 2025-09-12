from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from db.users import get_user_by_chat_id
from config import SUPPORT_PHONE, BILLING_PHONE


async def get_main_menu(chat_id: int):
    """
    Формирует главное меню в зависимости от того,
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
            [KeyboardButton(text="📰 Новости")],   # Новости только для авторизованных
            [KeyboardButton(text="✉️ Техподдержка")],
            [KeyboardButton(text="🔓 Отвязать договор")],
        ]
    else:
        # Неавторизованный пользователь
        keyboard = [
            [KeyboardButton(text="🔑 Авторизоваться")],
            [KeyboardButton(text="✉️ Техподдержка")],
        ]

    reply_kb = ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )

    # Inline-кнопки для звонков (доступны всем)
    call_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📞 Позвонить в абонентский отдел", url=f"tel:{BILLING_PHONE}")],
            [InlineKeyboardButton(text="📞 Позвонить в техподдержку", url=f"tel:{SUPPORT_PHONE}")],
        ]
    )

    return reply_kb, call_kb
