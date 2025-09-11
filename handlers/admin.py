from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
import os
import sys
import signal
from logger import logger
from config import ADMIN_CHAT_IDS

# Создаем роутер ДО его использования
router = Router()

def is_admin(user_id: int) -> bool:
    """Проверка, является ли пользователь администратором"""
    return str(user_id) in ADMIN_CHAT_IDS if ADMIN_CHAT_IDS else False

@router.message(Command("stop"))
async def stop_bot(message: Message):
    """Команда остановки бота"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав для этой команды")
        return
    
    user_info = f"{message.from_user.full_name} (@{message.from_user.username})" if message.from_user.username else message.from_user.full_name
    logger.info(f"Bot stop command received from admin: {user_info} (ID: {message.from_user.id})")
    
    await message.answer("🛑 Бот останавливается...")
    await message.bot.session.close()
    
    # Отправляем сигнал завершения процессу
    os.kill(os.getpid(), signal.SIGTERM)

@router.message(Command("restart"))
async def restart_bot(message: Message):
    """Команда перезапуска бота"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав для этой команды")
        return
    
    user_info = f"{message.from_user.full_name} (@{message.from_user.username})" if message.from_user.username else message.from_user.full_name
    logger.info(f"Bot restart command received from admin: {user_info} (ID: {message.from_user.id})")
    
    await message.answer("🔄 Бот перезапускается...")
    await message.bot.session.close()
    
    # Перезапуск через execv (полный перезапуск процесса)
    python = sys.executable
    os.execl(python, python, *sys.argv)

@router.message(Command("status"))
async def status_bot(message: Message):
    """Команда проверки статуса бота"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав для этой команды")
        return
    
    await message.answer("✅ Бот работает нормально")

@router.message(Command("help_admin"))
async def help_admin(message: Message):
    """Помощь для администратора"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав для этой команды")
        return
    
    help_text = """
🤖 <b>Административные команды:</b>

/stop - Остановить бота
/restart - Перезапустить бота
/status - Проверить статус бота
/help_admin - Показать это сообщение

⚠️ <i>Используйте с осторожностью!</i>
"""
    await message.answer(help_text, parse_mode="HTML")