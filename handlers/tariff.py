from aiogram import Router
from aiogram.types import Message

from services.bgbilling import get_tariff_plan
from db.users import get_user_by_chat_id
from keyboards.main_menu import get_main_menu
from logger import logger

router = Router()


@router.message(lambda msg: msg.text == "📊 Текущий тариф")
async def get_user_tariff(message: Message):
    chat_id = message.chat.id
    user = await get_user_by_chat_id(chat_id)

    if not user or not user.get("contract_id"):
        await message.answer("❌ Сначала авторизуйтесь.", reply_markup=await get_main_menu(chat_id))
        return

    try:
        data = await get_tariff_plan(user["contract_id"])
        if data:
            plan = data.get("title", "неизвестно")
            await message.answer(f"📊 Ваш тарифный план: <b>{plan}</b>")
        else:
            await message.answer("⚠️ Не удалось получить тарифный план.")
    except Exception as e:
        logger.error(f"Ошибка получения тарифа chat_id={chat_id}: {e}")
        await message.answer("⚠️ Ошибка при получении тарифа.")
