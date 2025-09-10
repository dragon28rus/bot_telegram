#### handlers/support.py
import re
from aiogram import types
from config import SUPPORT_CHAT_ID
from logger import logger, set_chat_id

async def handle_support_reply(message: types.Message):
    """
    Обрабатывает ответы техподдержки в группе, отправляя их пользователям по chat_id.
    
    Args:
        message: Входящее сообщение от оператора в группе поддержки
    """
    set_chat_id('support')
    if not message.reply_to_message:
        logger.warning('No reply-to message found')
        await message.reply('Пожалуйста, используйте функцию "Ответить" на сообщение с chat_id.')
        return
    
    # Извлекаем текст пересланного сообщения
    replied_message = message.reply_to_message.text
    if not replied_message:
        logger.warning('Replied message has no text')
        await message.reply('Пересланное сообщение не содержит текста. Убедитесь, что отвечаете на сообщение с chat_id.')
        return

    logger.info(f'Replied message text: {replied_message}')
    
    # Ищем chat_id в тексте пересланного сообщения
    match = re.search(r'chat_id: (\d+)', replied_message)
    if not match:
        logger.warning('No chat_id found in replied message')
        await message.reply('Не удалось найти chat_id в пересланном сообщении. Убедитесь, что отвечаете на сообщение с chat_id.')
        return

    user_chat_id = int(match.group(1))
    try:
        # Отправляем ответ пользователю
        await message.bot.send_message(user_chat_id, f"Ответ техподдержки: {message.text}")
        logger.info(f'Reply sent to user with chat_id: {user_chat_id}')
        await message.reply(f"Ответ успешно отправлен пользователю (chat_id: {user_chat_id}).")
    except Exception as e:
        logger.error(f'Error sending reply to user with chat_id {user_chat_id}: {e}')
        await message.reply(
            f"Ошибка при отправке ответа пользователю (chat_id: {user_chat_id}). "
            f"Возможные причины: пользователь заблокировал бота или chat_id некорректен. Ошибка: {e}"
        )

def register_support_handlers(dp):
    """
    Регистрирует хэндлер для ответов техподдержки.
    
    Args:
        dp: Dispatcher объект для регистрации хэндлера
    """
    dp.register_message_handler(handle_support_reply, chat_id=SUPPORT_CHAT_ID, content_types=types.ContentTypes.TEXT, is_reply=True)
