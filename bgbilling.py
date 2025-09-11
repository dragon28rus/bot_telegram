import aiohttp
from aiohttp import ClientTimeout, ClientError
from typing import Union
from config import BGBILLING_API_URL, BGBILLING_AUTH
from logger import logger, set_chat_id

# Таймаут для всех запросов (в секундах)
REQUEST_TIMEOUT = 5

async def check_contract(contract_id: str, chat_id: str = 'unknown') -> bool:
    """
    Проверяет существование договора в BGBilling по contract_id.
    
    Args:
        contract_id: Номер договора для проверки.
        chat_id: Telegram chat_id для логирования.
    Returns:
        bool: True, если договор существует, False в противном случае.
    """
    set_chat_id(chat_id)
    try:
        async with aiohttp.ClientSession(auth=aiohttp.BasicAuth(*BGBILLING_AUTH), timeout=ClientTimeout(total=REQUEST_TIMEOUT)) as session:
            async with session.get(f'{BGBILLING_API_URL}/jsonWebApi/contract', params={'contractId': contract_id}) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('exists', False):
                        logger.info(f'Contract {contract_id} exists')
                        return True
                    else:
                        logger.warning(f'Contract {contract_id} not found')
                        return False
                else:
                    logger.error(f'Error checking contract {contract_id}: HTTP {response.status}')
                    return False
    except aiohttp.ClientTimeout:
        logger.error(f'Timeout checking contract {contract_id}')
        raise
    except ClientError as e:
        logger.error(f'Error checking contract {contract_id}: {e}')
        raise

async def authenticate(contract_number: str, password: str, chat_id: str = 'unknown') -> Union[dict, None]:
    """
    Аутентифицирует пользователя в BGBilling.
    
    Args:
        contract_number: Номер договора
        password: Пароль
        chat_id: Telegram chat_id для логирования
    Returns:
        Union[dict, None]: Результат аутентификации или None в случае ошибки
    """
    set_chat_id(chat_id)
    try:
        async with aiohttp.ClientSession(auth=aiohttp.BasicAuth(*BGBILLING_AUTH), timeout=ClientTimeout(total=REQUEST_TIMEOUT)) as session:
            async with session.get(
                f'{BGBILLING_API_URL}/jsonWebApi/login',
                params={'login': contract_number, 'password': password, 'midAuth': 0}
            ) as response:
                if response.status == 200:
                    logger.info('Authentication request sent')
                    return await response.json()
                else:
                    logger.error(f'Authentication failed with status {response.status}')
                    return None
    except aiohttp.ClientTimeout:
        logger.error('Timeout connecting to BGBilling API')
        raise
    except ClientError as e:
        logger.error(f'Error connecting to BGBilling API: {e}')
        raise

async def save_chat_id(contract_id: str, chat_id: str) -> bool:
    """
    Сохраняет chat_id в параметрах договора в BGBilling.
    
    Args:
        contract_id: ID договора
        chat_id: Telegram chat_id
    Returns:
        bool: True если успешно, False в случае ошибки
    """
    set_chat_id(chat_id)
    try:
        async with aiohttp.ClientSession(auth=aiohttp.BasicAuth(*BGBILLING_AUTH), timeout=ClientTimeout(total=REQUEST_TIMEOUT)) as session:
            async with session.get(
                f'{BGBILLING_API_URL}/jsonWebApi/contractParameters',
                params={'contractId': contract_id}
            ) as response:
                if response.status != 200:
                    logger.error(f'Failed to get contract parameters: {response.status}')
                    return False
                params = (await response.json()).get('contractParameters', [])
                chat_id_param = next((p for p in params if p['title'] == 'chat_id'), None)
            
            async with session.post(
                f'{BGBILLING_API_URL}/jsonWebApi/updateContractParameter',
                json={
                    'contractId': contract_id,
                    'paramId': chat_id_param['id'] if chat_id_param else '100',
                    'value': str(chat_id),
                    'typeId': '1'
                }
            ) as update_response:
                if update_response.status == 200:
                    logger.info('Chat ID saved successfully')
                    return True
                else:
                    logger.error(f'Failed to update chat_id: {update_response.status}')
                    return False
    except aiohttp.ClientTimeout:
        logger.error('Timeout connecting to BGBilling API for saving chat_id')
        raise
    except ClientError as e:
        logger.error(f'Error saving chat_id to BGBilling: {e}')
        raise

async def get_balance(contract_id: str, chat_id: str = 'unknown') -> Union[dict, None]:
    """
    Получает баланс договора из BGBilling.
    
    Args:
        contract_id: ID договора
        chat_id: Telegram chat_id для логирования
    Returns:
        Union[dict, None]: Данные о балансе или None в случае ошибки
    """
    set_chat_id(chat_id)
    try:
        async with aiohttp.ClientSession(auth=aiohttp.BasicAuth(*BGBILLING_AUTH), timeout=ClientTimeout(total=REQUEST_TIMEOUT)) as session:
            async with session.get(
                f'{BGBILLING_API_URL}/jsonWebApi/contractBalance',
                params={'contractId': contract_id}
            ) as response:
                if response.status == 200:
                    logger.info('Balance request sent')
                    return await response.json()
                else:
                    logger.error(f'Failed to get balance: {response.status}')
                    return None
    except aiohttp.ClientTimeout:
        logger.error('Timeout connecting to BGBilling API for balance')
        raise
    except ClientError as e:
        logger.error(f'Error getting balance from BGBilling: {e}')
        raise

async def get_tariff_cost(contract_id: str, chat_id: str = 'unknown') -> Union[dict, None]:
    """
    Получает информацию о тарифе договора из BGBilling.
    
    Args:
        contract_id: ID договора
        chat_id: Telegram chat_id для логирования
    Returns:
        Union[dict, None]: Данные о тарифе или None в случае ошибки
    """
    set_chat_id(chat_id)
    try:
        async with aiohttp.ClientSession(auth=aiohttp.BasicAuth(*BGBILLING_AUTH), timeout=ClientTimeout(total=REQUEST_TIMEOUT)) as session:
            async with session.get(
                f'{BGBILLING_API_URL}/jsonWebApi/contractTarifPlans',
                params={'contractId': contract_id}
            ) as response:
                if response.status == 200:
                    logger.info('Tariff request sent')
                    return await response.json()
                else:
                    logger.error(f'Failed to get tariff: {response.status}')
                    return None
    except aiohttp.ClientTimeout:
        logger.error('Timeout connecting to BGBilling API for tariff')
        raise
    except ClientError as e:
        logger.error(f'Error getting tariff from BGBilling: {e}')
        raise

async def get_news(contract_id: str, chat_id: str = 'unknown') -> Union[dict, None]:
    """
    Получает последние новости для договора из BGBilling.
    
    Args:
        contract_id: ID договора
        chat_id: Telegram chat_id для логирования
    Returns:
        Union[dict, None]: Данные новостей или None в случае ошибки
    """
    set_chat_id(chat_id)
    try:
        async with aiohttp.ClientSession(auth=aiohttp.BasicAuth(*BGBILLING_AUTH), timeout=ClientTimeout(total=REQUEST_TIMEOUT)) as session:
            async with session.get(
                f'{BGBILLING_API_URL}/jsonWebApi/newsList',
                params={'contractId': contract_id}
            ) as response:
                if response.status == 200:
                    logger.info('News request sent')
                    return await response.json()
                else:
                    logger.error(f'Failed to get news: {response.status}')
                    return None
    except aiohttp.ClientTimeout:
        logger.error('Timeout connecting to BGBilling API for news')
        raise
    except ClientError as e:
        logger.error(f'Error getting news from BGBilling: {e}')
        raise

async def get_last_payments(contract_id: str, chat_id: str = 'unknown') -> Union[dict, None]:
    """
    Получает последние платежи по договору из BGBilling.
    
    Args:
        contract_id: ID договора
        chat_id: Telegram chat_id для логирования
    Returns:
        Union[dict, None]: Данные о платежах или None в случае ошибки
    """
    set_chat_id(chat_id)
    try:
        async with aiohttp.ClientSession(auth=aiohttp.BasicAuth(*BGBILLING_AUTH), timeout=ClientTimeout(total=REQUEST_TIMEOUT)) as session:
            async with session.get(
                f'{BGBILLING_API_URL}/jsonWebApi/lastContractPayments',
                params={'contractId': contract_id, 'members': 1, 'lastPayments': 3}
            ) as response:
                if response.status == 200:
                    logger.info('Payments request sent')
                    return await response.json()
                else:
                    logger.error(f'Failed to get payments: {response.status}')
                    return None
    except aiohttp.ClientTimeout:
        logger.error('Timeout connecting to BGBilling API for payments')
        raise
    except ClientError as e:
        logger.error(f'Error getting payments from BGBilling: {e}')
        raise