from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from db.users import get_user_by_chat_id


async def get_main_menu(chat_id: int) -> ReplyKeyboardMarkup:
    """
    Формирует главное меню в зависимости от того,
    авторизован ли пользователь (есть ли договор в БД).
    """

    user = await get_user_by_chat_id(chat_id)

    # Если пользователь авторизован (есть contract_id)
    if user and user.get("contract_id"):
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
    else:
        # Если пользователь не авторизован
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
