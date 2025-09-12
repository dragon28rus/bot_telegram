# handlers/payments.py
from aiogram import Router, types, F

from db.users import get_user_by_chat_id
from services.bgbilling import get_last_payments
from logger import logger, set_chat_id
from handlers.start import main_menu

router = Router()


@router.message(F.text == "💳 Последние платежи")
async def show_payments(message: types.Message):
    chat_id = message.chat.id
    set_chat_id(str(chat_id))

    user = await get_user_by_chat_id(chat_id)
    if not user:
        await message.answer(
            "❌ Платежи доступны только для авторизованных пользователей.\n"
            "Пожалуйста, авторизуйтесь.",
            reply_markup=await main_menu(chat_id),
        )
        return

    contract_id = user["contract_id"]

    try:
        payments_data = await get_last_payments(contract_id)

        if not payments_data or "payments" not in payments_data:
            await message.answer("ℹ️ Данные о платежах отсутствуют.", reply_markup=await main_menu(chat_id))
            return

        payments = payments_data.get("payments", [])
        if not payments:
            await message.answer("ℹ️ Платежи не найдены.", reply_markup=await main_menu(chat_id))
            return

        response_lines = []
        for p in payments:
            date = p.get("date", "Неизвестно")
            amount = p.get("sum", "0")
            method = p.get("comment", "Без комментария")
            response_lines.append(f"📅 {date} | 💵 {amount} ₽ | 🏦 {method}")

        response = "\n".join(response_lines)

        await message.answer(f"💳 Последние платежи:\n\n{response}", reply_markup=await main_menu(chat_id))
        logger.info(f"Отправлены платежи chat_id={chat_id}, contract_id={contract_id}")
    except Exception as e:
        await message.answer("⚠ Ошибка при получении платежей. Попробуйте позже.", reply_markup=await main_menu(chat_id))
        logger.error(f"Ошибка при получении платежей chat_id={chat_id}, contract_id={contract_id}: {e}")
