#### handlers/check.py
from aiogram import types
from logger import logger, set_chat_id

async def check_bot(message: types.Message):
    """
    Проверяет статус бота в чате (присутствие и права администратора).
    
    Args:
        message: Входящее сообщение с командой /check_bot
    """
    chat_id = message.chat.id
    set_chat_id(chat_id)
    try:
        chat = await message.bot.get_chat(chat_id)
        bot_member = await message.bot.get_chat_member(chat_id, message.bot.id)
        is_member = bot_member.is_chat_member()
        is_admin = bot_member.is_chat_admin()
        response = (
            f"Chat ID: {chat_id}\n"
            f"Bot status: {'Active' if is_member else 'Not in chat'}\n"
            f"Admin: {is_admin}\n"
            "Для проверки прав на отправку/чтение сообщений: убедитесь, что бот добавлен в группу и имеет права администратора или соответствующие разрешения."
        )
        await message.reply(response)
        logger.info(f'Bot status checked: {response}')
    except Exception as e:
        await message.reply(f"Ошибка при проверке статуса бота: {e}")
        logger.error(f'Error checking bot status: {e}')
