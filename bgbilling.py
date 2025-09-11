import aiohttp
from aiohttp import ClientTimeout, ClientError
from typing import Union
from config import BGBILLING_API_URL, BGBILLING_AUTH
from logger import logger, set_chat_id

# Timeout for all requests (in seconds)
REQUEST_TIMEOUT = 5

async def check_contract(contract_id: str, chat_id: str = 'unknown') -> bool:
    """
    Checks if a contract exists in BGBilling by contract_id.
    
    Args:
        contract_id: Contract number to check.
        chat_id: Telegram chat_id for logging.
    Returns:
        bool: True if contract exists, False otherwise.
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
        return False
    except ClientError as e:
        logger.error(f'Error checking contract {contract_id}: {e}')
        return False
    except Exception as e:
        logger.error(f'Unexpected error checking contract {contract_id}: {e}')
        return False
    finally:
        await asyncio.sleep(0.05)  # Increased delay for cleanup

async def authenticate(contract_number: str, password: str, chat_id: str = 'unknown') -> Union[dict, None]:
    """
    Authenticates a user in BGBilling.
    
    Args:
        contract_number: Contract number
        password: Password
        chat_id: Telegram chat_id for logging
    Returns:
        Union[dict, None]: Authentication result or None on error
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
        return None
    except ClientError as e:
        logger.error(f'Error connecting to BGBilling API: {e}')
        return None
    except Exception as e:
        logger.error(f'Unexpected error in authentication: {e}')
        return None
    finally:
        await asyncio.sleep(0.05)

async def save_chat_id(contract_id: str, chat_id: str) -> bool:
    """
    Saves chat_id to contract parameters in BGBilling.
    
    Args:
        contract_id: Contract ID
        chat_id: Telegram chat_id
    Returns:
        bool: True if successful, False on error
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
        return False
    except ClientError as e:
        logger.error(f'Error saving chat_id to BGBilling: {e}')
        return False
    except Exception as e:
        logger.error(f'Unexpected error saving chat_id: {e}')
        return False
    finally:
        await asyncio.sleep(0.05)

async def get_balance(contract_id: str, chat_id: str = 'unknown') -> Union[dict, None]:
    """
    Retrieves contract balance from BGBilling.
    
    Args:
        contract_id: Contract ID
        chat_id: Telegram chat_id for logging
    Returns:
        Union[dict, None]: Balance data or None on error
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
        return None
    except ClientError as e:
        logger.error(f'Error getting balance from BGBilling: {e}')
        return None
    except Exception as e:
        logger.error(f'Unexpected error getting balance: {e}')
        return None
    finally:
        await asyncio.sleep(0.05)

async def get_tariff_cost(contract_id: str, chat_id: str = 'unknown') -> Union[dict, None]:
    """
    Retrieves tariff information for a contract from BGBilling.
    
    Args:
        contract_id: Contract ID
        chat_id: Telegram chat_id for logging
    Returns:
        Union[dict, None]: Tariff data or None on error
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
        return None
    except ClientError as e:
        logger.error(f'Error getting tariff from BGBilling: {e}')
        return None
    except Exception as e:
        logger.error(f'Unexpected error getting tariff: {e}')
        return None
    finally:
        await asyncio.sleep(0.05)

async def get_news(contract_id: str, chat_id: str = 'unknown') -> Union[dict, None]:
    """
    Retrieves recent news for a contract from BGBilling.
    
    Args:
        contract_id: Contract ID
        chat_id: Telegram chat_id for logging
    Returns:
        Union[dict, None]: News data or None on error
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
        return None
    except ClientError as e:
        logger.error(f'Error getting news from BGBilling: {e}')
        return None
    except Exception as e:
        logger.error(f'Unexpected error getting news: {e}')
        return None
    finally:
        await asyncio.sleep(0.05)

async def get_last_payments(contract_id: str, chat_id: str = 'unknown') -> Union[dict, None]:
    """
    Retrieves recent payments for a contract from BGBilling.
    
    Args:
        contract_id: Contract ID
        chat_id: Telegram chat_id for logging
    Returns:
        Union[dict, None]: Payment data or None on error
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
        return None
    except ClientError as e:
        logger.error(f'Error getting payments from BGBilling: {e}')
        return None
    except Exception as e:
        logger.error(f'Unexpected error getting payments: {e}')
        return None
    finally:
        await asyncio.sleep(0.05)