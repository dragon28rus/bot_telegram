from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from services.bgbilling import authenticate
from db.users import add_user
from logger import logger
from handlers.start import cmd_start  # <-- импортируем start

router = Router()


class AuthStates(StatesGroup):
    waiting_for_contract = State()
    waiting_for_password = State()


@router.message(lambda msg: msg.text == "🔑 Авторизоваться")
async def start_auth(message: Message, state: FSMContext):
    await message.answer("Введите номер договора (3–6 цифр):")
    await state.set_state(AuthStates.waiting_for_contract)


@router.message(AuthStates.waiting_for_contract)
async def process_contract(message: Message, state: FSMContext):
    contract_id = message.text.strip()

    if not contract_id.isdigit() or not (3 <= len(contract_id) <= 6):
        await message.answer("❌ Номер договора должен содержать 3–6 цифр. Попробуйте снова:")
        return

    await state.update_data(contract_id=contract_id)
    await message.answer("Теперь введите пароль статистики:")
    await state.set_state(AuthStates.waiting_for_password)


@router.message(AuthStates.waiting_for_password)
async def process_password(message: Message, state: FSMContext):
    user_data = await state.get_data()
    contract_id = user_data.get("contract_id")
    password = message.text.strip()
    chat_id = message.chat.id

    try:
        result = await authenticate(contract_id, password)
        if result and result.get("status") == "Ok":
            await add_user(chat_id, contract_id)
            logger.info(f"Авторизация успешна: chat_id={chat_id}, contract_id={contract_id}")

            # после успешной авторизации вызываем start.py
            await cmd_start(message)
        else:
            logger.warning(f"Ошибка авторизации: chat_id={chat_id}, contract_id={contract_id}")
            await message.answer("❌ Неверный номер договора или пароль.")
    except Exception as e:
        logger.error(f"Ошибка авторизации chat_id={chat_id}: {e}")
        await message.answer("⚠️ Ошибка при попытке авторизации. Попробуйте позже.")
    finally:
        await state.clear()
