from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from services.bgbilling import authenticate
from db.users import add_user
from keyboards.main_menu import get_main_menu
from logger import logger

router = Router()


class AuthStates(StatesGroup):
    waiting_for_contract_id = State()
    waiting_for_password = State()


@router.message(Command("auth"))
async def start_auth(message: Message, state: FSMContext):
    """
    Хэндлер для начала авторизации.
    Запрашивает номер договора.
    """
    await message.answer("Введите номер договора (3–6 цифр):")
    await state.set_state(AuthStates.waiting_for_contract_id)

@router.message(lambda msg: msg.text == "🔑 Авторизоваться")
async def start_auth_button(message: Message, state: FSMContext):
    """Обработка кнопки 'Авторизоваться' из меню."""
    await start_auth(message, state)

@router.message(AuthStates.waiting_for_contract_id)
async def process_contract_id(message: Message, state: FSMContext):
    """
    Обработка номера договора.
    """
    contract_id = message.text.strip()
    if not contract_id.isdigit() or not (3 <= len(contract_id) <= 6):
        await message.answer("❌ Номер договора должен содержать от 3 до 6 цифр. Попробуйте снова:")
        return

    await state.update_data(contract_id=contract_id)
    await message.answer("Введите пароль статистики:")
    await state.set_state(AuthStates.waiting_for_password)


@router.message(AuthStates.waiting_for_password)
async def process_password(message: Message, state: FSMContext):
    """
    Обработка пароля и попытка авторизации через BGBilling.
    """
    user_data = await state.get_data()
    contract_id = user_data.get("contract_id")
    password = message.text.strip()
    chat_id = message.chat.id

    try:
        result = await authenticate(contract_id, password)

        if isinstance(result, dict) and result.get("status") == "Ok":
            # Успешная авторизация
            await add_user(chat_id, contract_id)
            logger.info(f"Авторизация успешна: chat_id={chat_id}, contract_id={contract_id}")

            # показываем динамическое меню
            keyboard = await get_main_menu(chat_id)
            await message.answer("✅ Авторизация успешна!", reply_markup=keyboard)
        else:
            # Ошибка авторизации
            logger.warning(f"Ошибка авторизации: chat_id={chat_id}, contract_id={contract_id}, result={result}")
            await message.answer("❌ Неверный номер договора или пароль.")
    except Exception as e:
        logger.exception(f"Ошибка авторизации chat_id={chat_id}")
        await message.answer("⚠️ Ошибка при попытке авторизации. Попробуйте позже.")
    finally:
        await state.clear()
