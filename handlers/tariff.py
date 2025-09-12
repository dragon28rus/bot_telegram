from aiogram import Router, F
from aiogram.types import Message

from db.users import get_user_by_chat_id
from services.bgbilling import get_tariff_plan
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
        data = await get_tariff_plan(user["contract_id"])
        plans = data.get("contractTarifPlans", [])
        if plans:
            title = plans[0].get("title", "—")
            date_from = plans[0].get("dateFrom", "")
            date_to = plans[0].get("dateTo", "")
            await message.answer(f"📊 Ваш тариф: <b>{title}</b>\nАктивен с {date_from}</b>\nпо {date_to}")
        else:
            await message.answer("⚠️ Не удалось получить тариф.")
    except Exception as e:
        logger.error(f"Ошибка получения тарифа chat_id={chat_id}: {e}")
        await message.answer("⚠️ Ошибка при получении тарифа.")