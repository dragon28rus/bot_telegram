# handlers/start.py
from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from config import SUPPORT_PHONE, BILLING_PHONE
from db.users import get_user_by_chat_id

router = Router()


async def main_menu(chat_id: int) -> types.ReplyKeyboardMarkup:
    """
    Главное меню бота с динамическими кнопками:
    - Если пользователь авторизован → кнопки баланса, тарифа, платежей и отвязки
    - Если нет → кнопка авторизации
    - Новости и звонки доступны всегда
    """
    kb = ReplyKeyboardBuilder()

    user = await get_user_by_chat_id(chat_id)

    if user:
        # Кнопки для авторизованных
        kb.button(text="🔓 Отвязать договор")
        kb.button(text="💰 Узнать баланс")
        kb.button(text="📊 Текущий тариф")
        kb.button(text="💳 Последние платежи")
        kb.button(text="💵 Оплатить услуги")
    else:
        # Если нет договора — только авторизация
        kb.button(text="🔑 Авторизоваться")

    # Кнопки, доступные всем
    kb.button(text="📰 Новости")
    kb.button(text="🛠 Техподдержка")
    kb.button(text="📞 Абон. отдел")
    kb.button(text="☎ Техподдержка")

    # Раскладываем по 2 кнопки в ряд
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


@router.message(CommandStart())
async def cmd_start(message: types.Message):
    """
    Обработка команды /start.
    Показывает главное меню (динамически).
    """
    await message.answer(
        text=(
            "👋 Добро пожаловать в бот компании *Кабельные системы*!\n\n"
            "Выберите нужное действие из меню ниже 👇"
        ),
        reply_markup=await main_menu(message.chat.id)
    )
