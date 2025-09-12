# handlers/auth.py
from aiogram import Router, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from db.users import add_user
from services.bgbilling import authenticate
from logger import logger
from handlers.start import main_menu

router = Router()


class AuthStates(StatesGroup):
    waiting_for_contract = State()
    waiting_for_password = State()


@router.message(F.text == "🔑 Авторизоваться")
async def start_auth(message: types.Message, state: FSMContext):
    await state.set_state(AuthStates.waiting_for_contract)
    await message.answer("Введите номер договора (3–6 цифр):")


@router.message(AuthStates.waiting_for_contract, F.text.regexp(r"^\d{3,6}$"))
async def auth_get_contract(message: types.Message, state: FSMContext):
    await state.update_data(contract_id=message.text)
    await state.set_state(AuthStates.waiting_for_password)
    await message.answer("Введите пароль статистики:")


@router.message(AuthStates.waiting_for_contract)
async def auth_wrong_contract(message: types.Message):
    await message.answer("❌ Номер договора должен содержать 3–6 цифр. Попробуйте ещё раз.")


@router.message(AuthStates.waiting_for_password)
async def auth_get_password(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    contract_id = user_data.get("contract_id")
    password = message.text
    chat_id = message.chat.id

    try:
        auth_response = await authenticate(contract_id, password)

        if auth_response and auth_response.get("status") == "Ok":
            contract_title = auth_response.get("contractTitle", str(contract_id))
            await add_user(chat_id, int(contract_id), contract_title)

            await message.answer(
                f"✅ Авторизация успешна!\n📄 Договор: <b>{contract_title}</b>",
                reply_markup=await main_menu(chat_id)
            )
            logger.info(f"Пользователь {chat_id} авторизован (договор {contract_id})")
        else:
            await message.answer("❌ Неверный номер договора или пароль.", reply_markup=await main_menu(chat_id))
            logger.warning(f"Неудачная попытка авторизации: chat_id={chat_id}, contract={contract_id}")
    except Exception as e:
        await message.answer("⚠ Ошибка при авторизации. Попробуйте позже.", reply_markup=await main_menu(chat_id))
        logger.error(f"Ошибка авторизации chat_id={chat_id}: {e}")

    await state.clear()
