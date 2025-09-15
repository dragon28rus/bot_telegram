# handlers/support.py
import logging
from aiogram import Router, F
from aiogram.types import Message
from config import SUPPORT_CHAT_ID
from db.support import (
    start_session,
    end_session,
    is_in_support,
    save_message_mapping,
    get_user_by_support_msg_id
)
from db.users import get_user_by_chat_id
from keyboards.main_menu import get_support_menu, get_main_menu
from logger import logger

router = Router()


def format_reply_info(msg: Message) -> str:
    """
    Формирует строку с информацией об оригинальном сообщении (для reply).
    """
    if msg.text:
        return msg.text
    if msg.photo:
        return "[фото]"
    if msg.document:
        return f"[документ: {msg.document.file_name}]"
    if msg.voice:
        return "[голосовое сообщение]"
    if msg.video:
        return "[видео]"
    if msg.audio:
        return f"[аудио: {msg.audio.file_name}]"
    if msg.sticker:
        return "[стикер]"
    return "[медиа]"


# ==============================
# ✉️ Вход в поддержку
# ==============================
@router.message(F.text == "✉️ Техподдержка")
async def enter_support(message: Message):
    """
    Вход в режим общения с техподдержкой.
    """
    user = await get_user_by_chat_id(message.chat.id)
    contract_title = user.get("contract_title") if user else "Не авторизованный пользователь"

    await start_session(message.chat.id, contract_title)

    logger.info(f"[SUPPORT] Пользователь {message.chat.id} ({message.from_user.full_name}) "
                f"вошёл в поддержку. Договор: {contract_title}")

    await message.answer(
        "✉️ Вы вошли в режим общения с техподдержкой.\n"
        "Напишите своё сообщение, оператор ответит вам здесь.",
        reply_markup=await get_support_menu()
    )


# ==============================
# ❌ Выход из поддержки
# ==============================
@router.message(F.text == "❌ Выйти из техподдержки")
async def exit_support(message: Message):
    """
    Выход из режима общения с техподдержкой.
    """
    await end_session(message.chat.id)

    logger.info(f"[SUPPORT] Пользователь {message.chat.id} ({message.from_user.full_name}) "
                f"вышел из поддержки")

    await message.answer(
        "🚪 Вы вышли из режима общения с техподдержкой.",
        reply_markup=await get_main_menu(message.chat.id)
    )


# ==============================
# 🔄 Универсальная пересылка
# ==============================
@router.message()
async def forward_message(message: Message):
    """
    Универсальный хэндлер:
    - пересылка сообщений абонента оператору,
    - пересылка reply от оператора абоненту.
    """

    # -----------------------------
    # Сообщения от ОПЕРАТОРА
    # -----------------------------
    if str(message.chat.id) == str(SUPPORT_CHAT_ID):
        if not message.reply_to_message:
            logger.debug(f"[SUPPORT] Оператор написал без reply: {message.text or '[медиа]'}")
            return

        mapping = await get_user_by_support_msg_id(message.reply_to_message.message_id)
        if not mapping:
            logger.warning(f"[SUPPORT] Не найдено соответствие для reply {message.reply_to_message.message_id}")
            return

        chat_id, user_message_id = mapping

        try:
            sent_msg = await message.copy_to(
                chat_id=chat_id,
                reply_to_message_id=user_message_id
            )
            logger.info(f"[SUPPORT] Оператор ({message.from_user.id}) "
                        f"ответил пользователю {chat_id}: {message.text or '[медиа]'}")
        except Exception as e:
            logger.exception(f"[SUPPORT] Ошибка отправки ответа пользователю {chat_id}: {e}")
        return

    # -----------------------------
    # Сообщения от АБОНЕНТОВ
    # -----------------------------
    user = await get_user_by_chat_id(message.chat.id)
    contract_title = user.get("contract_title") if user else "Не авторизованный пользователь"

    # Проверяем, что абонент в режиме поддержки
    if not await is_in_support(message.chat.id):
        return

    # Если абонент отвечает на сообщение
    reply_info = ""
    if message.reply_to_message:
        original_preview = format_reply_info(message.reply_to_message)
        reply_info = f"\n\n↩️ Ответ на сообщение:\n{original_preview}"

    # Формируем заголовок
    header = (
        f"📨 Сообщение от абонента:\n"
        f"👤 Пользователь: {message.from_user.full_name} @{message.from_user.username}\n"
        f"📄 Договор: {contract_title}"
        f"{reply_info}\n\n"
    )

    try:
        # Сначала шлём заголовок
        await message.bot.send_message(SUPPORT_CHAT_ID, header)

        # Потом пересылаем оригинал (с медиа/текстом)
        sent_msg = await message.copy_to(SUPPORT_CHAT_ID)

        # Сохраняем связь для reply
        await save_message_mapping(message.chat.id, message.message_id, sent_msg.message_id)

        logger.info(f"[SUPPORT] Пользователь {message.chat.id} ({message.from_user.full_name}) "
                    f"отправил сообщение оператору {SUPPORT_CHAT_ID}: {message.text or '[медиа]'}")

        await message.answer("✅ Ваше сообщение принято. Скоро оператор ответит.")
    except Exception as e:
        logger.exception(f"[SUPPORT] Ошибка пересылки сообщения оператору: {e}")
        await message.answer("⚠️ Ошибка при отправке сообщения в поддержку.")
