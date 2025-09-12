# handlers/support.py
import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import Command

from db.support import (
    save_support_request,
    update_support_message_id,
    get_chat_id_by_support_message_id,
    link_admin_message,
)
from db.users import get_user_by_chat_id
from config import SUPPORT_CHAT_ID

router = Router()
logger = logging.getLogger(__name__)

# Состояния
class SupportStates(StatesGroup):
    waiting_for_message = State()

@router.message(Command("support"))
@router.message(F.text == "🆘 Техподдержка")
async def start_support(message: Message, state: FSMContext):
    """Начало диалога с техподдержкой"""
    logger.debug(f"[support] Пользователь {message.chat.id} вызвал поддержку")
    await message.answer("🆘 Напишите ваше сообщение для техподдержки, и оператор ответит вам здесь.")
    await state.set_state(SupportStates.waiting_for_message)


@router.message(F.chat.type == "private")
async def process_support_message(message: Message):
    """
    Обработка сообщений пользователей: пересылка в чат поддержки.
    """
    chat_id = message.chat.id
    text = message.text
    logger.debug(f"[support] Получено сообщение от {chat_id}: {text}")

    # Проверяем авторизацию пользователя
    user = await get_user_by_chat_id(chat_id)
    logger.debug(f"[support] Данные пользователя: {user}")

    if user and len(user) >= 3 and user[2]:  # contract_title
        title = user[2]
        text_to_support = f"[{title}] {text}"
    else:
        text_to_support = text

    # Сохраняем обращение в БД
    request_id = await save_support_request(str(chat_id), text)
    logger.debug(f"[support] Запрос сохранён в БД: request_id={request_id}")

    # Пересылаем сообщение в чат поддержки
    sent = await message.bot.send_message(
        SUPPORT_CHAT_ID,
        f"📩 Сообщение от пользователя {chat_id}:\n{text_to_support}",
    )
    logger.debug(f"[support] Сообщение переслано в SUPPORT_CHAT {SUPPORT_CHAT_ID}, message_id={sent.message_id}")

    # Обновляем support_message_id в БД
    await update_support_message_id(request_id, sent.message_id)
    logger.debug(f"[support] Обновлён support_message_id={sent.message_id} для request_id={request_id}")

    await message.answer("✅ Ваше сообщение отправлено в техподдержку.")


@router.message(F.chat.id == SUPPORT_CHAT_ID, F.reply_to_message)
async def process_admin_reply(message: Message):
    """
    Обработка ответов операторов из SUPPORT_CHAT_ID.
    """
    support_message_id = message.reply_to_message.message_id
    logger.debug(f"[support] Ответ администратора, reply_to_message_id={support_message_id}")

    # Получаем chat_id абонента
    user_chat_id = await get_chat_id_by_support_message_id(support_message_id)
    logger.debug(f"[support] Найден user_chat_id={user_chat_id} для support_message_id={support_message_id}")

    if not user_chat_id:
        logger.warning(f"[support] Не найден пользователь для support_message_id={support_message_id}")
        return

    # Привязываем сообщение оператора
    await link_admin_message(support_message_id, message.message_id)
    logger.debug(f"[support] Привязка admin_message_id={message.message_id} к support_message_id={support_message_id}")

    # Отправляем ответ абоненту
    await message.bot.send_message(
        user_chat_id,
        f"💬 Ответ техподдержки:\n{message.text}",
    )
    logger.debug(f"[support] Ответ отправлен пользователю {user_chat_id}")
