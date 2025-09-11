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
            return
        logger.info("Starting authorization process")
        await message.answer("Введите номер договора (3-6 цифр):")
        await state.set_state(AuthStates.waiting_for_contract_id)
    except Exception as e:
        logger.error(f"Error checking authorization: {e}")
        await message.answer("Ошибка при проверке авторизации. Попробуйте снова позже.")


@router.message(AuthStates.waiting_for_contract_id)
async def process_contract_id(message: Message, state: FSMContext):
    set_chat_id(message.from_user.id)
    contract_title = message.text.strip()

    # Удаляем пробелы и невидимые символы
    contract_title = re.sub(r"\s+", "", contract_title)

    # Проверяем: только цифры, длина от 3 до 6
    if not (contract_title.isdigit() and 3 <= len(contract_title) <= 6):
        logger.warning(f"Invalid contract_title format: {contract_title}")
        await message.answer("Номер договора должен содержать от 3 до 6 цифр. Попробуйте снова:")
        return

    await state.update_data(contract_title=contract_title)
    await message.answer("Теперь введите пароль от статистики:")
    await state.set_state(AuthStates.waiting_for_password)


@router.message(AuthStates.waiting_for_password)
async def process_password(message: Message, state: FSMContext):
    set_chat_id(message.from_user.id)
    password = message.text.strip()
    data = await state.get_data()
    contract_title = data.get("contract_title")

    if not contract_title:
        logger.error("No contract_title in state when processing password")
        await message.answer("Произошла ошибка. Пожалуйста, начните авторизацию заново (/start).")
        await state.clear()
        return

    try:
        result = await authenticate(contract_title, password, str(message.from_user.id))

        # 🔎 Подробный лог ответа от API
        logger.debug(f"BGBilling raw response for contract {contract_title}: {result}")

        if result and isinstance(result, dict) and result.get("status") == "Ok":
            contract_id = result.get("contractId")       # внутренний ID
            contract_title = result.get("contractTitle") # номер договора
            await save_user(message.from_user.id, contract_id, contract_title)
            logger.info(
                f"User {message.from_user.id} authorized with contract_id={contract_id}, title={contract_title}"
            )
            await message.answer("✅ Авторизация успешна! Используйте /menu для доступа к функциям.")
            await state.clear()
        else:
            logger.warning(
                f"Authorization failed for contract_title {contract_title}. BGBilling response: {result}"
            )
            await message.answer("❌ Неверный номер договора или пароль. Попробуйте снова (/start).")
            await state.clear()
    except Exception as e:
        logger.error(f"Error during authentication: {e}")
        await message.answer("Произошла ошибка при авторизации. Попробуйте снова позже.")
        await state.clear()