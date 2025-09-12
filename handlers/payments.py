from aiogram import Router
from aiogram.types import Message

from services.bgbilling import get_last_payments
from db.users import get_user_by_chat_id
from keyboards.main_menu import get_main_menu
from logger import logger

router = Router()


@router.message(lambda msg: msg.text == "💳 Последние платежи")
async def get_user_payments(message: Message):
    chat_id = message.chat.id
    user = await get_user_by_chat_id(chat_id)

    if not user or not user.get("contract_id"):
        await message.answer("❌ Сначала авторизуйтесь.", reply_markup=await get_main_menu(chat_id))
        return

    try:
        data = await get_last_payments(user["contract_id"])
        if data and "payments" in data:
            payments = data["payments"][:5]  # последние 5
            if payments:
                text = "💳 Последние платежи:\n\n"
                for p in payments:
                    text += f"📅 {p.get('date')}: <b>{p.get('sum')} ₽</b>\n"
                await message.answer(text)
            else:
                await message.answer("📭 Платежей пока нет.")
        else:
            await message.answer("⚠️ Не удалось получить платежи.")
    except Exception as e:
        logger.error(f"Ошибка получения платежей chat_id={chat_id}: {e}")
        await message.answer("⚠️ Ошибка при получении платежей.")
