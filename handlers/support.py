# handlers/support.py
from aiogram import Router, F
from aiogram.types import Message
from config import SUPPORT_CHAT_ID
from db.support import start_session, end_session, is_in_support, save_message_mapping
from db.users import get_user_by_chat_id
from main_menu import get_support_menu, get_main_menu

router = Router()


@router.message(F.text == "✉️ Техподдержка")
async def enter_support(message: Message):
    """
    Вход в режим общения с техподдержкой.
    """
    user = await get_user_by_chat_id(message.chat.id)

    if not user:
        await message.answer("❌ Вы не авторизованы. Для связи с техподдержкой авторизуйтесь.")
        return

    contract_title = user.get("contract_title")
    await start_session(message.chat.id, contract_title)

    await message.answer(
        "✉️ Вы вошли в режим общения с техподдержкой.\n"
        "Напишите своё сообщение, оператор ответит вам здесь.",
        reply_markup=await get_support_menu()
    )


@router.message(F.text == "❌ Выйти из техподдержки")
async def exit_support(message: Message):
    """
    Выход из режима общения с техподдержкой.
    """
    await end_session(message.chat.id)

    await message.answer(
        "🚪 Вы вышли из режима общения с техподдержкой.",
        reply_markup=await get_main_menu(message.chat.id)
    )


@router.message(F.text)
async def forward_to_support(message: Message):
    """
    Пересылка текстовых сообщений от абонента в чат техподдержки.
    """
    # Проверяем, находится ли пользователь в режиме поддержки
    if not await is_in_support(message.chat.id):
        return

    user = await get_user_by_chat_id(message.chat.id)
    if not user:
        await message.answer("❌ Ошибка: вы не авторизованы.")
        return

    contract_title = user.get("contract_title")

    # Формируем текст для оператора
    text = (
        f"📨 Сообщение от абонента:\n"
        f"👤 Пользователь: {message.from_user.full_name} (id={message.chat.id})\n"
        f"📄 Договор: {contract_title}\n\n"
        f"{message.text}"
    )

    # Пересылаем сообщение оператору
    support_msg = await message.bot.send_message(SUPPORT_CHAT_ID, text)

    # Сохраняем связь сообщений для reply
    await save_message_mapping(message.chat.id, message.message_id, support_msg.message_id)

    # Если это первое сообщение, уведомляем абонента
    if message.message_id == 1:
        await message.answer("✅ Ваше сообщение принято. Скоро оператор ответит.")
