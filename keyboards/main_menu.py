from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message
from aiogram import Router
from config import SUPPORT_PHONE, BILLING_PHONE
from db.users import get_user_by_chat_id

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
            [KeyboardButton(text="Техподдержка")],
            [KeyboardButton(text="📞 Позвонить в абонентский отдел")],
            [KeyboardButton(text="📞 Позвонить в техподдержку")],
            [KeyboardButton(text="🔓 Отвязать договор")],
        ]
    else:
        # Неавторизованный пользователь
        keyboard = [
            [KeyboardButton(text="🔑 Авторизоваться")],
            [KeyboardButton(text="Техподдержка")],
            [KeyboardButton(text="📞 Позвонить в абонентский отдел")],
            [KeyboardButton(text="📞 Позвонить в техподдержку")],
        ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )


# ==============================
# 📞 Обработчики звонков
# ==============================

@router.message(lambda msg: msg.text == "📞 Позвонить в абонентский отдел")
async def call_billing(message: Message):
    await message.answer(f"📞 Номер абонентского отдела: {BILLING_PHONE}")


@router.message(lambda msg: msg.text == "📞 Позвонить в техподдержку")
async def call_support(message: Message):
    await message.answer(f"📞 Номер технической поддержки: {SUPPORT_PHONE}")
