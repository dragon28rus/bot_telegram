from aiogram import Router, F
from aiogram.types import Message

from logger import logger
from config import SUPPORT_PHONE, BILLING_PHONE
from keyboards.main_menu import get_phone_menu, get_main_menu

router = Router()

@router.message(F.text == "📞 Позвонить")
async def call(message: Message):
    await message.answer(
        "Для отоброжения номера выберите отдел",
        reply_markup=await get_phone_menu()
    )

@router.message(F.text == "📞 Позвонить в техподдержку")
async def call1(message: Message):
    await message.answer(
        "Для отоброжения номера выберите отдел",
        reply_markup=await get_phone_menu()
    )

@router.message(F.text == "🔙 Вернуться назад")
async def exit_support(message: Message):
    await message.answer(
        "🚪 Вы вернулись в основное меню.",
        reply_markup=await get_main_menu(message.chat.id)
    )

@router.message(F.text.startswith("📞 Позвонить в абонентский отдел"))
async def call_billing(message: Message):
    logger.debug(f"Пользователь {message.chat.id} ({message.from_user.full_name}) "
                f"запросил номер абонентского отдела")
    await message.answer(f"📞 Номер абонентского отдела: {BILLING_PHONE}")


@router.message(F.text.startswith("📞 Позвонить в техническую поддержку"))
async def call_support(message: Message):
    logger.debug(f"Пользователь {message.chat.id} ({message.from_user.full_name}) "
                f"запросил номер технической поддержки")
    await message.answer(f"📞 Номер технической поддержки: {SUPPORT_PHONE}")

