from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from logger import logger, set_chat_id

router = Router()


@router.message(Command("check_bot"))
async def check_bot(message: Message):
    set_chat_id(message.from_user.id)
    try:
        bot_member = await message.bot.get_chat_member(message.chat.id, message.bot.id)

        status_map = {
            "creator": "Создатель чата",
            "administrator": "Администратор",
            "member": "Участник",
            "restricted": "Ограничен",
            "left": "Покинул чат",
            "kicked": "Заблокирован",
        }

        status = status_map.get(bot_member.status, bot_member.status)

        response = (
            f"Chat ID: {message.chat.id}\n"
            f"Bot status: {status}\n"
        )

        if bot_member.status in ["administrator", "creator"]:
            rights = bot_member.can_manage_chat if hasattr(bot_member, "can_manage_chat") else None
            perms = []
            for field, value in bot_member.__dict__.items():
                if field.startswith("can_") and value:
                    perms.append(field)

            if perms:
                response += "Доступные права:\n" + "\n".join([f"- {p}" for p in perms])
            else:
                response += "Права администратора не определены или отсутствуют."

        await message.answer(response)
        logger.info(f"Bot status checked: {response}")
    except Exception as e:
        logger.error(f"Error checking bot status: {e}")
        await message.answer("Ошибка при проверке статуса бота.")