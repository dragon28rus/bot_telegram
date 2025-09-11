import re
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from db import save_user, is_user_authorized
from bgbilling import authenticate
from logger import logger, set_chat_id

router = Router()


class AuthStates(StatesGroup):
    waiting_for_contract_id = State()
    waiting_for_password = State()


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

    if not re.match(r"^\\d{3,6}$", contract_id):
        logger.warning(f"Invalid contract_id format: {contract_id}")
        await message.answer(
            "Номер договора должен содержать от 3 до 6 цифр. Попробуйте снова:"
        )
        return

    await state.update_data(contract_id=contract_id)
    await message.answer("Теперь введите пароль от статистики:")
    await state.set_state(AuthStates.waiting_for_password)


@router.message(AuthStates.waiting_for_password)
async def process_password(message: Message, state: FSMContext):
    set_chat_id(message.from_user.id)
    password = message.text.strip()
    data = await state.get_data()
    contract_id = data.get("contract_id")

    try:
        result = await authenticate(contract_id, password, str(message.from_user.id))
        if result and result.get("success"):
            await save_user(message.from_user.id, contract_id)
            logger.info(f"User {message.from_user.id} authorized with contract_id: {contract_id}")
            await message.answer(
                "✅ Авторизация успешна! Используйте /menu для доступа к функциям."
            )
            await state.clear()
        else:
            logger.warning(f"Authorization failed for contract_id {contract_id}")
            await message.answer("❌ Неверный номер договора или пароль. Попробуйте снова.")
            await state.clear()
    except Exception as e:
        logger.error(f"Error during authentication: {e}")
        await message.answer("Произошла ошибка при авторизации. Попробуйте снова позже.")
        await state.clear()