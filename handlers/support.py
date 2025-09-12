# handlers/support.py
from aiogram import Router, F
from aiogram.types import Message
from config import SUPPORT_CHAT_ID, ADMIN_CHAT_IDS
from logger import logger
from db.support import save_support_request, get_chat_id_by_support_message_id, get_last_support_message_id
from aiogram.exceptions import TelegramBadRequest

router = Router()


def short_text(text: str, limit: int = 50) -> str:
    """Обрезает текст для логов"""
    if not text:
        return ""
    return text if len(text) <= limit else text[:limit] + "..."


# === Пользователь пишет в поддержку ===
@router.message(F.text.in_(["🆘 Техподдержка", "/support"]))
async def support_request(message: Message):
    chat_id = str(message.chat.id)
    text = message.text

    try:
        support_msg = await message.bot.send_message(
            SUPPORT_CHAT_ID,
            f"📩 Новый запрос от пользователя {chat_id}:\n\n{text}"
        )

        await save_support_request(chat_id, support_msg.message_id)

        await message.answer("✅ Ваш запрос отправлен в техподдержку. Ожидайте ответа.")
        logger.info(
            f"[SUPPORT] Пользователь {chat_id} → оператор "
            f"(user_msg_id={message.message_id}, support_msg_id={support_msg.message_id}): "
            f"{short_text(text)}"
        )

    except Exception as e:
        logger.error(f"[SUPPORT] Ошибка при отправке в поддержку (chat_id={chat_id}): {e}")
        await message.answer("❌ Не удалось отправить запрос в техподдержку.")


# === Оператор отвечает пользователю через reply ===
@router.message(F.reply_to_message, F.chat.id == int(SUPPORT_CHAT_ID))
async def support_reply(message: Message):
    operator_id = str(message.from_user.id)
    text = message.text
    reply_to_id = message.reply_to_message.message_id

    if operator_id not in ADMIN_CHAT_IDS:
        logger.warning(f"[SUPPORT] ⚠️ Неавторизованный ответ от {operator_id}")
        return

    try:
        user_chat_id = await get_chat_id_by_support_message_id(reply_to_id)

        if user_chat_id:
            user_msg = await message.bot.send_message(user_chat_id, f"💬 Ответ оператора:\n\n{text}")
            logger.info(
                f"[SUPPORT] Оператор {operator_id} → пользователь {user_chat_id} "
                f"(reply_to_support_id={reply_to_id}, operator_msg_id={message.message_id}, "
                f"user_msg_id={user_msg.message_id}): {short_text(text)}"
            )
        else:
            logger.warning(f"[SUPPORT] Не найдена связка для ответа (reply_to_id={reply_to_id})")

    except TelegramBadRequest as e:
        logger.error(f"[SUPPORT] Ошибка Telegram при ответе: {e}")
    except Exception as e:
        logger.error(f"[SUPPORT] Непредвиденная ошибка: {e}")


# === Оператор пишет без reply (ответ последнему пользователю) ===
@router.message(F.chat.id == int(SUPPORT_CHAT_ID))
async def support_reply_last(message: Message):
    operator_id = str(message.from_user.id)
    text = message.text

    if operator_id not in ADMIN_CHAT_IDS:
        logger.warning(f"[SUPPORT] ⚠️ Неавторизованный ответ от {operator_id}")
        return

    try:
        last_user_chat_id = await get_last_support_message_id(str(message.chat.id))
        if last_user_chat_id:
            user_msg = await message.bot.send_message(last_user_chat_id, f"💬 Ответ оператора:\n\n{text}")
            logger.info(
                f"[SUPPORT] Оператор {operator_id} → последний пользователь {last_user_chat_id} "
                f"(operator_msg_id={message.message_id}, user_msg_id={user_msg.message_id}): "
                f"{short_text(text)}"
            )
        else:
            logger.warning("[SUPPORT] Нет сохранённых обращений для ответа.")

    except Exception as e:
        logger.error(f"[SUPPORT] Ошибка при отправке ответа последнему пользователю: {e}")
