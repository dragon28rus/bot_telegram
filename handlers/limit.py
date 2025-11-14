from aiogram import Router, F
from aiogram.types import Message
from db.users import get_user_by_chat_id
from services.bgbilling_custom import request_promised_payment
from keyboards.main_menu import get_main_menu, lower_limit_menu
from logger import logger

router = Router()

@router.message(F.text == "👛 Обещанный платеж")
async def lower_limit(message: Message):
    await message.answer(
        "Подтвердите что хотите подключить обещанный платеж",
        reply_markup=await lower_limit_menu()
    )

@router.message(F.text == "👌 Да, подключить!")
async def set_lower_limit(message: Message):
    chat_id = message.chat.id
    user = await get_user_by_chat_id(chat_id)

    if not user or not user.get("contract_id"):
        await message.answer("❌ Сначала авторизуйтесь.", reply_markup=await get_main_menu(chat_id))
        return

    try:
        limit = await request_promised_payment(user["contract_id"], 5000)
        if limit is None:
            await message.answer("⚠️ Ошибка связи с биллингом. Попробуйте позднее")
        elif not limit["success"]:
            await message.answer(f"⚠️ Не удалось понизить лимит. Причина: \n{limit['error']}")
        else:
            await message.answer(
                f"💸 Ваш лимит успешно понижен!\n"
                f"Новый лимит: {limit['new_limit']} руб.\n"
                f"Действует {limit['days']} дней."
            )
    except Exception as e:
        logger.error(f"Ошибка понижения лимита chat_id={chat_id}: {e}")
        await message.answer("⚠️ Ошибка при понижении лимита.")