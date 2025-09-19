from typing import Optional, Dict, Any
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from logger import logger

from services.bgbilling import authenticate
from db.users import add_user
from keyboards.main_menu import get_main_menu, get_auth_menu
from config import SUPPORT_CHAT_ID

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
    keyboard = await get_auth_menu()
    await message.answer("Введите номер договора (3–6 цифр):", reply_markup=keyboard)
    await state.set_state(AuthStates.waiting_for_contract_id)

@router.message(lambda msg: msg.text == "🔑 Авторизоваться")
async def start_auth_button(message: Message, state: FSMContext):
    """Обработка кнопки 'Авторизоваться' из меню."""
    chat_id = str(message.chat.id)
    if {chat_id} == {SUPPORT_CHAT_ID}:
        # Аккаунт технической поддержки
        keyboard = await get_main_menu(int(chat_id))
        await message.answer("✅ Авторизация прошла успешно!", reply_markup=keyboard)
    else:
        await start_auth(message, state)

@router.message(AuthStates.waiting_for_contract_id)
async def process_contract_id(message: Message, state: FSMContext):
    """
    Обработка номера договора.
    """
    contract_id = message.text.strip()
    if F.text == "❌ Выйти из режима вторизации":
        await message.answer("🚪 Вы вышли из режима авторизации.")
        await get_main_menu(message.chat.id)
        await state.clear()
        return
    elif not contract_id.isdigit() or not (3 <= len(contract_id) <= 6):
        await message.answer("❌ Номер договора должен содержать от 3 до 6 цифр. Попробуйте снова:")
        return

    await state.update_data(contract_id=contract_id)
    await message.answer("Введите пароль статистики:")
    await state.set_state(AuthStates.waiting_for_password)

@router.message(AuthStates.waiting_for_password)
async def process_password(message: Message, state: FSMContext):
    """
    Обрабатываем введённый пароль:
      - вызываем authenticate()
      - корректно извлекаем resolved contract_id и contract_title
      - сохраняем оба поля в БД
    """
    data = await state.get_data()
    contract_input = data.get("contract_id") or data.get("contract")  # что ввёл пользователь
    password = message.text.strip()
    chat_id = str(message.chat.id)

    logger.debug(f"[auth] Попытка авторизации: chat_id={chat_id}, input_contract='{contract_input}'")

    if F.text == "❌ Выйти из режима вторизации":
        await message.answer("🚪 Вы вышли из режима авторизации.")
        await get_main_menu(message.chat.id)
        await state.clear()
        return
    try:
        result: Optional[Dict[str, Any]] = await authenticate(contract_input, password)

        # Поддерживаем два варианта: когда authenticate вернул 'status' или только нормализованные поля
        if result is None:
            logger.warning(f"Ошибка авторизации: chat_id={chat_id}, input='{contract_input}', result=None")
            await message.answer("❌ Ошибка авторизации. Попробуйте позже.")
            await state.clear()
            return

        # Если API вернул status, смотрим на него
        if result.get("status") and result.get("status") != "Ok":
            logger.warning(f"Неверные учётные данные: chat_id={chat_id}, input='{contract_input}', api_status={result.get('status')}")
            await message.answer("❌ Неверный номер договора или пароль.")
            await state.clear()
            return

        # получаем resolved ID и title (в приоритете нормализованные ключи)
        resolved_contract_id = result.get("contract_id") or result.get("contractId")
        resolved_contract_title = result.get("contract_title") or result.get("contractTitle") or contract_input

        if not resolved_contract_id:
            # на всякий случай — если ID не пришёл
            logger.error(f"[auth] Авторизация прошла, но contract_id не найден: chat_id={chat_id}, result={result}")
            await message.answer("❌ Не удалось определить ID договора после авторизации.")
            await state.clear()
            return

        # Сохраняем в БД (contract_id — как строка)
        await add_user(chat_id, str(resolved_contract_id), resolved_contract_title)

        logger.info(
            f"Авторизация успешна: chat_id={chat_id}, input='{contract_input}', resolved_contract_id={resolved_contract_id}, "
            f"resolved_contract_title='{resolved_contract_title}'"
        )

        # Показать главное меню пользователю
        keyboard = await get_main_menu(int(chat_id))
        await message.answer("✅ Авторизация прошла успешно!", reply_markup=keyboard)

    except Exception as e:
        logger.exception(f"Ошибка авторизации chat_id={chat_id}: {e}")
        await message.answer("⚠️ Ошибка при попытке авторизации. Попробуйте позже.")
    finally:
        await state.clear()
