# handlers/tariff.py
from aiogram import Router, types, F

from db.users import get_user_by_chat_id
from services.bgbilling import get_tariff_plan
from logger import logger
from handlers.start import main_menu

router = Router()


@router.message(F.text == "📊 Текущий тариф")
async def show_tariff(message: types.Message):
    chat_id = message.chat.id

    user = await get_user_by_chat_id(chat_id)
    if not user:
        await message.answer(
            "❌ Информация о тарифе доступна только для авторизованных пользователей.\n"
            "Пожалуйста, авторизуйтесь.",
            reply_markup=await main_menu(chat_id),
        )
        return

    contract_id = user["contract_id"]

    try:
        tariff_data = await get_tariff_plan(contract_id)

        if not tariff_data or "tarifs" not in tariff_data:
            await message.answer("ℹ️ Информация о тарифах отсутствует.", reply_markup=await main_menu(chat_id))
            return

        tarifs = tariff_data.get("tarifs", [])
        if not tarifs:
            await message.answer("ℹ️ У вас нет активных тарифных планов.", reply_markup=await main_menu(chat_id))
            return

        # Берём первый активный тариф
        tariff = tarifs[0]
        title = tariff.get("title", "Без названия")
        cost = tariff.get("cost", "Неизвестно")

        await message.answer(
            f"📊 Ваш тарифный план: <b>{title}</b>\n💵 Стоимость: {cost}",
            reply_markup=await main_menu(chat_id),
        )
        logger.info(f"Отправлен тариф chat_id={chat_id}, contract_id={contract_id}")
    except Exception as e:
        await message.answer("⚠ Ошибка при получении тарифа. Попробуйте позже.", reply_markup=await main_menu(chat_id))
        logger.error(f"Ошибка при получении тарифа chat_id={chat_id}, contract_id={contract_id}: {e}")
