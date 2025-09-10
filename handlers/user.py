#### handlers/user.py
from aiogram import types
from aiogram.dispatcher.filters import Text
from bgbilling import get_balance, get_tariff_cost, get_news, get_last_payments
from db import get_contract_id, get_contract_number, delete_user
from keyboards import get_main_keyboard
from logger import logger, set_chat_id
from config import SUPPORT_CHAT_ID

async def balance(message: types.Message):
    """
    Обрабатывает запрос на получение баланса пользователя.
    
    Args:
        message: Входящее сообщение от пользователя
    """
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
    """
    Обрабатывает запрос на получение последних новостей.
    
    Args:
        message: Входящее сообщение от пользователя
    """
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
    """
    Обрабатывает запрос на получение информации о тарифе.
    
    Args:
        message: Входящее сообщение от пользователя
    """
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
    """
    Обрабатывает запрос на получение последних платежей.
    
    Args:
        message: Входящее сообщение от пользователя
    """
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
    """
    Обрабатывает запрос на обращение в техническую поддержку, пересылая его в группу поддержки.
    
    Args:
        message: Входящее сообщение от пользователя
    """
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
    """
    Обрабатывает запрос на предоставление номера телефона абонентского отдела.
    
    Args:
        message: Входящее сообщение от пользователя
    """
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
    """
    Обрабатывает запрос на отвязку договора пользователя.
    
    Args:
        message: Входящее сообщение от пользователя
    """
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
    """
    Пересылает любое текстовое сообщение в группу техподдержки.
    
    Args:
        message: Входящее сообщение от пользователя
    """
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

def register_user_handlers(dp):
    """
    Регистрирует хэндлеры для пользовательских функций.
    
    Args:
        dp: Dispatcher объект для регистрации хэндлеров
    """
    dp.register_message_handler(balance, Text(equals='Узнать баланс'))
    dp.register_message_handler(news, Text(equals='Узнать новости'))
    dp.register_message_handler(tariff, Text(equals='Узнать стоимость по тарифу'))
    dp.register_message_handler(last_payments, Text(equals='Последние платежи'))
    dp.register_message_handler(support, Text(equals='Обратиться в техническую поддержку'))
    dp.register_message_handler(call_support, Text(equals='Позвонить на абонентский отдел'))
    dp.register_message_handler(unlink_contract, Text(equals='Отвязать договор'))
    dp.register_message_handler(echo)
