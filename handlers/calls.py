from aiogram import Router, F
from aiogram.types import Message

from logger import logger
from config import SUPPORT_PHONE, BILLING_PHONE

router = Router()

@router.message(F.text == "📞 Позвонить в абонентский отдел")
async def call_billing(message: Message):
    logger.debug(f"Пользователь {message.chat.id} ({message.from_user.full_name}) "
                f"запросил номер абонентского отдела")
    await message.answer(f"📞 Номер абонентского отдела: {BILLING_PHONE}")


@router.message(F.text == "📞 Позвонить в техподдержку")
async def call_support(message: Message):
    logger.debug(f"Пользователь {message.chat.id} ({message.from_user.full_name}) "
                f"запросил номер технической поддержки")
    await message.answer(f"📞 Номер технической поддержки: {SUPPORT_PHONE}")

