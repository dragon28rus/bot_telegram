from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import re

from db import save_user, get_contract_id_by_chat_id, is_user_authorized
from bgbilling import check_contract
from logger import logger, set_chat_id

router = Router()


class AuthStates(StatesGroup):
    waiting_for_contract_id = State()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    set_chat_id(message.from_user.id)
    try:
        if await is_user_authorized(message.from_user.id):
            logger.info("User already authorized")
            await message.answer(
                "Вы уже авторизованы. Используйте /menu для доступа к функциям."
            )
        else:
            logger.info("Starting authorization process")
            await message.answer("Введите номер договора (3-6 цифр):")
            await state.set_state(AuthStates.waiting_for_contract_id)
    except Exception as e:
        logger.error(f"Error checking authorization: {e}")
        await message.answer("Ошибка при проверке авторизации. Попробуйте снова позже.")


@router.message(AuthStates.waiting_for_contract_id)
async def process_contract_id(message: Message, state: FSMContext):
    set_chat_id(message.from_user.id)
    contract_id = message.text.strip()

    if not re.match(r"^\d{3,6}$", contract_id):
        logger.warning(f"Invalid contract_id format: {contract_id}")
        await message.answer(
            "Номер договора должен содержать от 3 до 6 цифр. Попробуйте снова:"
        )
        return

    try:
        if await check_contract(contract_id, str(message.from_user.id)):
            await save_user(message.from_user.id, contract_id)
            logger.info(f"User authorized with contract_id: {contract_id}")
            await message.answer(
                "Авторизация успешна! Используйте /menu для доступа к функциям."
            )
            await state.clear()
        else:
            logger.warning(f"Contract_id {contract_id} not found in BGBilling")
            await message.answer("Номер договора не найден. Попробуйте снова:")
    except Exception as e:
        logger.error(f"Error during authorization: {e}")
        await message.answer(
            "Произошла ошибка при авторизации. Попробуйте снова позже."
        )
        await state.clear()