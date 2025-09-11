from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from logger import logger, set_chat_id

router = Router()

@router.message(Command("check_bot"))
async def check_bot(message: Message):
    set_chat_id(message.chat.id)
    try:
        bot_member = await message.bot.get_chat_member(message.chat.id, message.bot.id)
        is_admin = bot_member.status in ['administrator', 'creator']
        status = "Active" if bot_member.status in ['member', 'administrator', 'creator'] else "Inactive"
        
        response = (
            f"Chat ID: {message.chat.id}\n"
            f"Bot status: {status}\n"
            f"Admin: {is_admin}\n"
            "Для проверки прав на отправку/чтение сообщений: убедитесь, что бот добавлен в группу и имеет права администратора или соответствующие разрешения."
        )
        await message.answer(response)
        logger.info(f"Bot status checked: {response}")
    except Exception as e:
        logger.error(f"Error checking bot status: {e}")
        await message.answer("Ошибка при проверке статуса бота.")