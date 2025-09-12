from aiogram import Router
from aiogram.types import Message

from db.users import remove_user, get_user_by_chat_id
from keyboards.main_menu import get_main_menu
from logger import logger

router = Router()


@router.message(lambda msg: msg.text == "🔓 Отвязать договор")
async def unlink_contract(message: Message):
    """
    Отвязка договора: удаляем пользователя из БД
    """
    chat_id = message.chat.id
    user = await get_user_by_chat_id(chat_id)

    if user and user.get("contract_id"):
        await remove_user(chat_id)
        logger.info(f"Договор отвязан: chat_id={chat_id}, contract_id={user['contract_id']}")
        await message.answer(
            "🔓 Договор успешно отвязан.\nТеперь вы можете авторизоваться снова.",
            reply_markup=await get_main_menu(chat_id)
        )
    else:
        await message.answer("❌ У вас нет активной привязки договора.", reply_markup=await get_main_menu(chat_id))
