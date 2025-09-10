#### handlers.py
import re
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiohttp import web
from config import SUPPORT_CHAT_ID
from bgbilling import authenticate, save_chat_id, get_balance, get_tariff_cost, get_news, get_last_payments
from db import save_user, get_contract_id, get_contract_number, delete_user, get_chat_id_by_contract_id
from keyboards import get_main_keyboard
from logger import logger, set_chat_id

# Состояния для FSM
class AuthState(StatesGroup):
    contract_number = State()
    password = State()

# Хэндлер для проверки статуса бота в группе
async def check_bot(message: types.Message):
    chat_id = message.chat.id
    set_chat_id(chat_id)
    try:
        chat = await message.bot.get_chat(chat_id)
        bot_member = await message.bot.get_chat_member(chat_id, message.bot.id)
        is_member = bot_member.is_chat_member()
        is_admin = bot_member.is_chat_admin()
        response = (
            f"Chat ID: {chat_id}\n"
            f"Bot status: {'Active' if is_member else 'Not in chat'}\n"
            f"Admin: {is_admin}\n"
            "Для проверки прав на отправку/чтение сообщений: убедитесь, что бот добавлен в группу и имеет права администратора или соответствующие разрешения."
        )
        await message.reply(response)
        logger.info(f'Bot status checked: {response}')
    except Exception as e:
        await message.reply(f"Ошибка при проверке статуса бота: {e}")
        logger.error(f'Error checking bot status: {e}')

# Хэндлер на старт
async def start(message: types.Message):
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

# Хэндлер для номера договора с валидацией
async def process_contract_number(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    set_chat_id(chat_id)
    contract_number = message.text.strip()
    if not re.match(r'^\d{3,6}$', contract_number):
        await message.reply('Неверный формат номера договора. Введите 3–6 цифр.')
        logger.warning('Invalid contract number format')
        return
    await state.update_data(contract_number=contract_number)
    await message.reply('Теперь введите пароль от статистики.')
    await AuthState.password.set()
    logger.info('Contract number received')

# Хэндлер для пароля и аутентификации
async def process_password(message: types.Message, state: FSMContext):
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

# Хэндлеры для кнопок
async def balance(message: types.Message):
    chat_id = message.chat.id
    set_chat_id(chat_id)
    contract_id = get_contract_id(chat_id)
    if contract_id:
        try:
            balance_data = get_balance(contract_id, chat_id=chat_id)
            if balance_data and balance_data.get('status') == 'Ok':
                await message.reply(f"Ваш баланс: {balance_data['sum']} {balance_data['currencyTitleMedium']}")
                logger.info('Balance retrieved successfully')
            else:
                await message.reply('Ошибка при получении баланса.')
                logger.error('Error retrieving balance')
        except Exception as e:
            await message.reply('Ошибка подключения к биллингу. Пожалуйста, попробуйте позже.')
            logger.error(f'Balance error: {e}')
    else:
        await message.reply('Пожалуйста, пройдите аутентификацию заново /start.')
        logger.warning('User not authorized')

async def news(message: types.Message):
    chat_id = message.chat.id
    set_chat_id(chat_id)
    contract_id = get_contract_id(chat_id)
    if contract_id:
        try:
            news_data = get_news(contract_id, chat_id=chat_id)
            if news_data and news_data.get('status') == 'Ok':
                for news_item in news_data['newsList'][:3]:
                    await message.reply(f"{news_item['date']} - {news_item['title']}\n{news_item['body'][:1000]}...")
                logger.info('News retrieved successfully')
            else:
                await message.reply('Ошибка при получении новостей.')
                logger.error('Error retrieving news')
        except Exception as e:
            await message.reply('Ошибка подключения к биллингу. Пожалуйста, попробуйте позже.')
            logger.error(f'News error: {e}')
    else:
        await message.reply('Пожалуйста, пройдите аутентификацию заново /start.')
        logger.warning('User not authorized')

async def tariff(message: types.Message):
    chat_id = message.chat.id
    set_chat_id(chat_id)
    contract_id = get_contract_id(chat_id)
    if contract_id:
        try:
            tariff_data = get_tariff_cost(contract_id, chat_id=chat_id)
            if tariff_data and tariff_data.get('status') == 'Ok' and tariff_data['contractTarifPlans']:
                tariff = tariff_data['contractTarifPlans'][0]
                await message.reply(f"Ваш тариф: {tariff['title']} (с {tariff['dateFrom']})")
                logger.info('Tariff retrieved successfully')
            else:
                await message.reply('Ошибка при получении тарифа.')
                logger.error('Error retrieving tariff')
        except Exception as e:
            await message.reply('Ошибка подключения к биллингу. Пожалуйста, попробуйте позже.')
            logger.error(f'Tariff error: {e}')
    else:
        await message.reply('Пожалуйста, пройдите аутентификацию заново /start.')
        logger.warning('User not authorized')

async def last_payments(message: types.Message):
    chat_id = message.chat.id
    set_chat_id(chat_id)
    contract_id = get_contract_id(chat_id)
    if contract_id:
        try:
            payments_data = get_last_payments(contract_id, chat_id=chat_id)
            if payments_data and payments_data.get('status') == 'Ok':
                response = f"Последние платежи (общая сумма: {payments_data['totalSum']}):\n"
                for payment in payments_data['contractPayments']:
                    response += f"{payment['date']} - {payment['sum']} ({payment['typeTitle']})\n"
                await message.reply(response)
                logger.info('Payments retrieved successfully')
            else:
                await message.reply('Ошибка при получении платежей.')
                logger.error('Error retrieving payments')
        except Exception as e:
            await message.reply('Ошибка подключения к биллингу. Пожалуйста, попробуйте позже.')
            logger.error(f'Payments error: {e}')
    else:
        await message.reply('Пожалуйста, пройдите аутентификацию заново /start.')
        logger.warning('User not authorized')

async def support(message: types.Message):
    chat_id = message.chat.id
    set_chat_id(chat_id)
    contract_id = get_contract_id(chat_id)
    try:
        if contract_id:
            contract_number = get_contract_number(chat_id)
            await message.bot.send_message(
                SUPPORT_CHAT_ID,
                f"Новое обращение от пользователя (договор: {contract_number}, chat_id: {chat_id}):\nОпишите вашу проблему в ответном сообщении."
            )
        else:
            await message.bot.send_message(
                SUPPORT_CHAT_ID,
                f"Новое обращение от пользователя (не авторизован, chat_id: {chat_id}):\nОпишите вашу проблему в ответном сообщении."
            )
        await message.reply('Ваше сообщение передано в техподдержку. Пожалуйста, опишите вашу проблему.')
        logger.info('Support request sent')
    except Exception as e:
        await message.reply('Ошибка при отправке сообщения в техподдержку. Попробуйте позже.')
        logger.error(f'Error forwarding to support: {e}')

async def call_support(message: types.Message):
    chat_id = message.chat.id
    set_chat_id(chat_id)
    try:
        await message.reply(
            'Позвоните в абонентский отдел по номеру: +74162999900',
            disable_web_page_preview=True
        )
        logger.info('Call support number provided as text')
    except Exception as e:
        await message.reply('Ошибка при предоставлении номера для звонка. Пожалуйста, попробуйте позже.')
        logger.error(f'Error providing call support number: {e}')

async def unlink_contract(message: types.Message):
    chat_id = message.chat.id
    set_chat_id(chat_id)
    contract_id = get_contract_id(chat_id)
    if contract_id:
        try:
            if delete_user(chat_id):
                await message.reply('Ваш договор успешно отвязан. Для новой авторизации используйте /start.')
                logger.info('Contract unlinked successfully')
            else:
                await message.reply('Ошибка при отвязке договора. Попробуйте позже.')
                logger.error('Error unlinking contract')
        except Exception as e:
            await message.reply('Ошибка при отвязке договора. Попробуйте позже.')
            logger.error(f'Error unlinking contract: {e}')
    else:
        await message.reply('Вы не авторизованы. Используйте /start для авторизации.')
        logger.warning('User not authorized for unlink')

async def echo(message: types.Message):
    chat_id = message.chat.id
    set_chat_id(chat_id)
    contract_id = get_contract_id(chat_id)
    try:
        if contract_id:
            contract_number = get_contract_number(chat_id)
            await message.bot.forward_message(SUPPORT_CHAT_ID, message.chat.id, message.message_id)
            await message.bot.send_message(
                SUPPORT_CHAT_ID,
                f"Обращение от пользователя (договор: {contract_number}, chat_id: {chat_id})"
            )
        else:
            await message.bot.forward_message(SUPPORT_CHAT_ID, message.chat.id, message.message_id)
            await message.bot.send_message(
                SUPPORT_CHAT_ID,
                f"Обращение от пользователя (не авторизован, chat_id: {chat_id})"
            )
        await message.reply('Ваше сообщение передано в техподдержку.')
        logger.info('User message forwarded to support')
    except Exception as e:
        await message.reply('Ошибка при отправке сообщения в техподдержку. Попробуйте позже.')
        logger.error(f'Error forwarding to support: {e}')

async def handle_support_reply(message: types.Message):
    set_chat_id('support')
    if not message.reply_to_message:
        logger.warning('No reply-to message found')
        await message.reply('Пожалуйста, используйте функцию "Ответить" на сообщение с chat_id.')
        return
    
    # Извлекаем текст пересланного сообщения
    replied_message = message.reply_to_message.text
    if not replied_message:
        logger.warning('Replied message has no text')
        await message.reply('Пересланное сообщение не содержит текста. Убедитесь, что отвечаете на сообщение с chat_id.')
        return

    logger.info(f'Replied message text: {replied_message}')
    
    # Ищем chat_id в тексте пересланного сообщения
    match = re.search(r'chat_id: (\d+)', replied_message)
    if not match:
        logger.warning('No chat_id found in replied message')
        await message.reply('Не удалось найти chat_id в пересланном сообщении. Убедитесь, что отвечаете на сообщение с chat_id.')
        return

    user_chat_id = int(match.group(1))
    try:
        # Отправляем ответ пользователю
        await message.bot.send_message(user_chat_id, f"Ответ техподдержки: {message.text}")
        logger.info(f'Reply sent to user with chat_id: {user_chat_id}')
        await message.reply(f"Ответ успешно отправлен пользователю (chat_id: {user_chat_id}).")
    except Exception as e:
        logger.error(f'Error sending reply to user with chat_id {user_chat_id}: {e}')
        await message.reply(
            f"Ошибка при отправке ответа пользователю (chat_id: {user_chat_id}). "
            f"Возможные причины: пользователь заблокировал бота или chat_id некорректен. Ошибка: {e}"
        )

async def handle_billing_notification(request, bot):
    try:
        data = await request.json()
        contract_id = data.get('contract_id')
        message = data.get('message')
        if not contract_id or not message:
            set_chat_id('system')
            logger.error('Invalid billing notification: missing contract_id or message')
            return web.json_response({'status': 'error', 'message': 'Missing contract_id or message'}, status=400)
        
        chat_id = get_chat_id_by_contract_id(contract_id)
        if chat_id:
            set_chat_id(chat_id)
            await bot.send_message(chat_id, f"Уведомление от биллинга: {message}")
            logger.info('Billing notification sent to user')
            return web.json_response({'status': 'ok'})
        else:
            set_chat_id('system')
            logger.warning('No chat_id found for contract_id')
            return web.json_response({'status': 'error', 'message': 'No user found for contract_id'}, status=404)
    except Exception as e:
        set_chat_id('system')
        logger.error(f'Error processing billing notification: {e}')
        return web.json_response({'status': 'error', 'message': str(e)}, status=500)

def register_handlers(dp):
    dp.register_message_handler(check_bot, commands=['check_bot'])
    dp.register_message_handler(start, commands=['start'])
    dp.register_message_handler(process_contract_number, state=AuthState.contract_number)
    dp.register_message_handler(process_password, state=AuthState.password)
    dp.register_message_handler(balance, Text(equals='Узнать баланс'))
    dp.register_message_handler(news, Text(equals='Узнать новости'))
    dp.register_message_handler(tariff, Text(equals='Узнать стоимость по тарифу'))
    dp.register_message_handler(last_payments, Text(equals='Последние платежи'))
    dp.register_message_handler(support, Text(equals='Обратиться в техническую поддержку'))
    dp.register_message_handler(call_support, Text(equals='Позвонить на абонентский отдел'))
    dp.register_message_handler(unlink_contract, Text(equals='Отвязать договор'))
    dp.register_message_handler(echo)
    dp.register_message_handler(handle_support_reply, chat_id=SUPPORT_CHAT_ID, content_types=types.ContentTypes.TEXT, is_reply=True)