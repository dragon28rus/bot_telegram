from aiogram import Router, F
from aiogram.types import Message
from db.users import get_user_by_chat_id
from services.bgbilling import get_balance
from keyboards.main_menu import get_main_menu
from logger import logger

router = Router()

@router.message(F.text == "💰 Узнать баланс")
async def get_user_balance(message: Message):
    chat_id = message.chat.id
    user = await get_user_by_chat_id(chat_id)
    
    if not user or not user.get("contract_id"):
        await message.answer("❌ Сначала авторизуйтесь.", reply_markup=await get_main_menu(chat_id))
        return

    try:
        balance = await get_balance(user["contract_id"])
        if balance:
            await message.answer(
                f"💰 Ваш баланс: {balance['balance']} {balance['currency']}"
            )
        else:
            await message.answer("⚠️ Не удалось получить баланс.")
    except Exception as e:
        logger.error(f"Ошибка получения баланса chat_id={chat_id}: {e}")
        await message.answer("⚠️ Ошибка при получении баланса.")
