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

@router.message(F.text == "✉️ Техподдержка")
async def enter_support(message: Message):
    """
    Вход в режим общения с техподдержкой.
    """
    user = await get_user_by_chat_id(message.chat.id)

    if not user:
        logger.warning(f"[SUPPORT] Неавторизованный пользователь {message.chat.id} "
                       f"пытался войти в поддержку")
        await message.answer("❌ Вы не авторизованы. Для связи с техподдержкой авторизуйтесь.")
        return

    contract_title = user.get("contract_title")
    await start_session(message.chat.id, contract_title)

    logger.info(f"[SUPPORT] Пользователь {message.chat.id} ({message.from_user.full_name}) "
                f"вошёл в поддержку. Договор: {contract_title}")

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

    logger.info(f"[SUPPORT] Пользователь {message.chat.id} ({message.from_user.full_name}) "
                f"вышел из поддержки")

    await message.answer(
        "🚪 Вы вышли из режима общения с техподдержкой.",
        reply_markup=await get_main_menu(message.chat.id)
    )

@router.message()
async def forward_message(message: Message):
    """
    Универсальный хэндлер: пересылка сообщений абонента оператору
    и пересылка reply от оператора абоненту.
    """

    # =============================
    # Сообщения от оператора (SUPPORT_CHAT_ID)
    # =============================
    if str(message.chat.id) == str(SUPPORT_CHAT_ID):
        if not message.reply_to_message:
            logger.debug(f"[SUPPORT] Оператор написал без reply: {message.text}")
            return

        mapping = await get_user_by_support_msg_id(message.reply_to_message.message_id)
        if not mapping:
            logger.warning(f"[SUPPORT] Не найдено соответствие для reply {message.reply_to_message.message_id}")
            return

        chat_id, user_message_id = mapping
        reply_text = f"📩 Ответ от оператора:\n{message.text or '[медиа]'}"

        try:
            await message.bot.send_message(
                chat_id=chat_id,
                text=reply_text,
                reply_to_message_id=user_message_id
            )
            logger.info(f"[SUPPORT] Оператор ({message.from_user.id}) "
                        f"ответил пользователю {chat_id}: {message.text}")
        except Exception as e:
            logger.exception(f"[SUPPORT] Ошибка отправки ответа пользователю {chat_id}: {e}")
        return

    # =============================
    # Сообщения от абонентов (все остальные)
    # =============================
    user = await get_user_by_chat_id(message.chat.id)
    if not user:
        logger.error(f"[SUPPORT] Не найден пользователь в БД (chat_id={message.chat.id})")
        await message.answer("❌ Ошибка: вы не авторизованы.")
        return

    contract_title = user.get("contract_title")

    text = (
        f"📨 Сообщение от абонента:\n"
        f"👤 Пользователь: {message.from_user.full_name} (id={message.chat.id})\n"
        f"📄 Договор: {contract_title}\n\n"
        f"{message.text or '[медиа]'}"
    )

    try:
        support_msg = await message.bot.send_message(SUPPORT_CHAT_ID, text)
        await save_message_mapping(message.chat.id, message.message_id, support_msg.message_id)

        logger.info(f"[SUPPORT] Пользователь {message.chat.id} ({message.from_user.full_name}) "
                    f"отправил сообщение оператору {SUPPORT_CHAT_ID}: {message.text}")

        await message.answer("✅ Ваше сообщение принято. Скоро оператор ответит.")
    except Exception as e:
        logger.exception(f"[SUPPORT] Ошибка пересылки сообщения оператору: {e}")
        await message.answer("⚠️ Ошибка при отправке сообщения в поддержку.")

"""
@router.message()
async def debug_all_messages(message: Message):
    from pprint import pformat
    logger.debug(f"[DEBUG] Пришло сообщение:\n{pformat(message.dict())}")
"""