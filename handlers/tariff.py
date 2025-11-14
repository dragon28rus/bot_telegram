from aiogram import Router, F
from aiogram.types import Message

from db.users import get_user_by_chat_id
from services.bgbilling import get_tariff_plan
from services.bgbilling_custom import get_recommended_payment
from keyboards.main_menu import get_main_menu
from logger import logger

router = Router()

@router.message(F.text == "📊 Текущий тариф")
async def get_user_tariff(message: Message):
    chat_id = message.chat.id
    user = await get_user_by_chat_id(chat_id)

    if not user or not user.get("contract_id"):
        await message.answer("❌ Сначала авторизуйтесь.", reply_markup=await get_main_menu(chat_id))
        return

    try:
        tariff = await get_tariff_plan(user["contract_id"])
        cost_tariff = await get_recommended_payment(user["contract_id"])
        if tariff:
            title = tariff.get("title", "—")
            date_from = tariff.get("dateFrom", "")
            date_to = tariff.get("dateTo", "")
            text = f"📊 Ваш тариф: <b>{title}</b>\nАктивен с {date_from}"
            if date_to:
                text += f"\nпо {date_to}"
            if cost_tariff and cost_tariff["success"]:
                total = cost_tariff["recommend_payment"]
                text += f"\nРекомендуемая сумма для оплаты: {total}"
            await message.answer(text)
        else:
            await message.answer("⚠️ Не удалось получить тариф.")
    except Exception as e:
        logger.error(f"Ошибка получения тарифа chat_id={chat_id}: {e}")
        await message.answer("⚠️ Ошибка при получении тарифа.")
