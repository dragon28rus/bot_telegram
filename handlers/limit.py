from aiogram import Router, F
from aiogram.types import Message
from db.users import get_user_by_chat_id
from services.bgbilling_custom import request_promised_payment
from keyboards.main_menu import get_main_menu
from logger import logger

router = Router()

@router.message(F.text == "💸 Обещанный платеж")
async def set_lower_limit(message: Message):
    chat_id = message.chat.id
    user = await get_user_by_chat_id(chat_id)

    if not user or not user.get("contract_id"):
        await message.answer("❌ Сначала авторизуйтесь.", reply_markup=await get_main_menu(chat_id))
        return

    try:
        limit = await request_promised_payment(user["contract_id"], 5000)
        if limit:
            status = limit.get("success", "False")
            if "True" in  status:
                await message.answer(
                    f"💸 Ваш лимит успешно понижен на 5 дней"
                )
            else:
                error = limit.get("error", "")
                await message.answer("⚠️ Не удалось понизить лимит. Причина: {error}")
        else:
            await message.answer("⚠️ Не удалось понизить лимит.")
    except Exception as e:
        logger.error(f"Ошибка получения баланса chat_id={chat_id}: {e}")
        await message.answer("⚠️ Ошибка при получении баланса.")
