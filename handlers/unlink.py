# handlers/unlink.py
from aiogram import Router, types, F

from db.users import get_user_by_chat_id, delete_user
from logger import logger
from handlers.start import main_menu

router = Router()


@router.message(F.text == "🔓 Отвязать договор")
async def unlink_contract(message: types.Message):
    """
    Отвязка договора от пользователя (удаление из БД)
    """
    chat_id = message.chat.id
    user = await get_user_by_chat_id(chat_id)

    if not user:
        await message.answer("ℹ️ У вас нет привязанного договора.", reply_markup=await main_menu(chat_id))
        return

    await delete_user(chat_id)
    await message.answer(
        "🔓 Договор отвязан. Вы можете авторизоваться снова.",
        reply_markup=await main_menu(chat_id)
    )
    logger.info(f"Пользователь {chat_id} отвязал договор")
