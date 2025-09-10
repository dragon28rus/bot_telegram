#### handlers/auth.py
import re
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from bgbilling import authenticate, save_chat_id
from db import save_user, get_contract_id
from keyboards import get_main_keyboard
from logger import logger, set_chat_id

# Определение состояний для конечного автомата (FSM) аутентификации
class AuthState(StatesGroup):
    contract_number = State()
    password = State()

async def start(message: types.Message):
    """
    Обрабатывает команду /start, проверяет авторизацию пользователя и инициирует процесс аутентификации.
    
    Args:
        message: Входящее сообщение от пользователя
    """
    chat_id = message.chat.id
    set_chat_id(chat_id)
    contract_id = get_contract_id(chat_id)
    if contract_id:
        await message.reply('Вы уже авторизованы!', reply_markup=get_main_keyboard())
        logger.info('User already authorized')
    else:
        await message.reply('Добрый день! Для идентификации введите номер договора.')
        await AuthState.contract_number.set()
        logger.info('Started authorization process')

async def process_contract_number(message: types.Message, state: FSMContext):
    """
    Обрабатывает введённый номер договора, проверяет его формат и запрашивает пароль.
    
    Args:
        message: Входящее сообщение с номером договора
        state: Состояние FSM для хранения данных
    """
    chat_id = message.chat.id
    set_chat_id(chat_id)
    contract_number = message.text.strip()
    # Проверка формата номера договора (3–6 цифр)
    if not re.match(r'^\d{3,6}$', contract_number):
        await message.reply('Неверный формат номера договора. Введите 3–6 цифр.')
        logger.warning('Invalid contract number format')
        return
    await state.update_data(contract_number=contract_number)
    await message.reply('Теперь введите пароль от статистики.')
    await AuthState.password.set()
    logger.info('Contract number received')

async def process_password(message: types.Message, state: FSMContext):
    """
    Обрабатывает введённый пароль, выполняет аутентификацию и сохраняет данные пользователя.
    
    Args:
        message: Входящее сообщение с паролем
        state: Состояние FSM с данными номера договора
    """
    chat_id = message.chat.id
    set_chat_id(chat_id)
    data = await state.get_data()
    contract_number = data.get('contract_number')
    password = message.text
    try:
        auth_result = authenticate(contract_number, password, chat_id=chat_id)
    except Exception as e:
        await message.reply('Ошибка подключения к биллингу. Пожалуйста, попробуйте позже.')
        logger.error(f'Authentication error: {e}')
        return
    
    if auth_result and auth_result.get('status') == 'Ok':
        contract_id = auth_result['contractId']
        try:
            if save_chat_id(contract_id, chat_id) and save_user(chat_id, contract_number, contract_id):
                await message.reply('Аутентификация успешна! Теперь вы можете использовать бота.', reply_markup=get_main_keyboard())
                await state.finish()
                logger.info('Authentication successful')
            else:
                await message.reply('Ошибка при сохранении данных. Попробуйте позже.')
                logger.error('Error saving user data')
        except Exception as e:
            await message.reply('Ошибка подключения к биллингу при сохранении данных. Пожалуйста, попробуйте позже.')
            logger.error(f'Error saving chat_id: {e}')
    else:
        await message.reply('Неверный номер договора или пароль. Попробуйте заново /start.')
        logger.warning('Invalid contract number or password')

def register_auth_handlers(dp):
    """
    Регистрирует хэндлеры для аутентификации.
    
    Args:
        dp: Dispatcher объект для регистрации хэндлеров
    """
    dp.register_message_handler(start, commands=['start'])
    dp.register_message_handler(process_contract_number, state=AuthState.contract_number)
    dp.register_message_handler(process_password, state=AuthState.password)
