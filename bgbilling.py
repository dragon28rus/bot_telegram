### bgbilling.py
import logging
import requests
from requests.exceptions import Timeout, RequestException
from config import BGBILLING_API_URL, BGBILLING_AUTH
from logger import logger, set_chat_id

# Таймаут для всех запросов (в секундах)
REQUEST_TIMEOUT = 5

def authenticate(contract_number, password, chat_id='unknown'):
    set_chat_id(chat_id)
    try:
        response = requests.get(
            f'{BGBILLING_API_URL}/jsonWebApi/login',
            params={'login': contract_number, 'password': password, 'midAuth': 0},
            auth=BGBILLING_AUTH,
            timeout=REQUEST_TIMEOUT
        )
        if response.status_code == 200:
            logger.info('Authentication request sent')
            return response.json()
        else:
            logger.error(f'Authentication failed with status {response.status_code}')
            return None
    except Timeout:
        logger.error('Timeout connecting to BGBilling API')
        raise
    except RequestException as e:
        logger.error(f'Error connecting to BGBilling API: {e}')
        raise

def save_chat_id(contract_id, chat_id):
    set_chat_id(chat_id)
    try:
        response = requests.get(
            f'{BGBILLING_API_URL}/jsonWebApi/contractParameters',
            params={'contractId': contract_id},
            auth=BGBILLING_AUTH,
            timeout=REQUEST_TIMEOUT
        )
        if response.status_code != 200:
            logger.error(f'Failed to get contract parameters: {response.status_code}')
            return False

        params = response.json().get('contractParameters', [])
        chat_id_param = next((p for p in params if p['title'] == 'chat_id'), None)
        
        update_response = requests.post(
            f'{BGBILLING_API_URL}/jsonWebApi/updateContractParameter',
            auth=BGBILLING_AUTH,
            json={
                'contractId': contract_id,
                'paramId': chat_id_param['id'] if chat_id_param else '100',
                'value': str(chat_id),
                'typeId': '1'
            },
            timeout=REQUEST_TIMEOUT
        )
        if update_response.status_code == 200:
            logger.info('Chat ID saved successfully')
            return True
        else:
            logger.error(f'Failed to update chat_id: {update_response.status_code}')
            return False
    except Timeout:
        logger.error('Timeout connecting to BGBilling API for saving chat_id')
        raise
    except RequestException as e:
        logger.error(f'Error saving chat_id to BGBilling: {e}')
        raise

def get_balance(contract_id, chat_id='unknown'):
    set_chat_id(chat_id)
    try:
        response = requests.get(
            f'{BGBILLING_API_URL}/jsonWebApi/contractBalance',
            params={'contractId': contract_id},
            auth=BGBILLING_AUTH,
            timeout=REQUEST_TIMEOUT
        )
        if response.status_code == 200:
            logger.info('Balance request sent')
            return response.json()
        else:
            logger.error(f'Failed to get balance: {response.status_code}')
            return None
    except Timeout:
        logger.error('Timeout connecting to BGBilling API for balance')
        raise
    except RequestException as e:
        logger.error(f'Error getting balance from BGBilling: {e}')
        raise

def get_tariff_cost(contract_id, chat_id='unknown'):
    set_chat_id(chat_id)
    try:
        response = requests.get(
            f'{BGBILLING_API_URL}/jsonWebApi/contractTarifPlans',
            params={'contractId': contract_id},
            auth=BGBILLING_AUTH,
            timeout=REQUEST_TIMEOUT
        )
        if response.status_code == 200:
            logger.info('Tariff request sent')
            return response.json()
        else:
            logger.error(f'Failed to get tariff: {response.status_code}')
            return None
    except Timeout:
        logger.error('Timeout connecting to BGBilling API for tariff')
        raise
    except RequestException as e:
        logger.error(f'Error getting tariff from BGBilling: {e}')
        raise

def get_news(contract_id, chat_id='unknown'):
    set_chat_id(chat_id)
    try:
        response = requests.get(
            f'{BGBILLING_API_URL}/jsonWebApi/newsList',
            params={'contractId': contract_id},
            auth=BGBILLING_AUTH,
            timeout=REQUEST_TIMEOUT
        )
        if response.status_code == 200:
            logger.info('News request sent')
            return response.json()
        else:
            logger.error(f'Failed to get news: {response.status_code}')
            return None
    except Timeout:
        logger.error('Timeout connecting to BGBilling API for news')
        raise
    except RequestException as e:
        logger.error(f'Error getting news from BGBilling: {e}')
        raise

def get_last_payments(contract_id, chat_id='unknown'):
    set_chat_id(chat_id)
    try:
        response = requests.get(
            f'{BGBILLING_API_URL}/jsonWebApi/lastContractPayments',
            params={'contractId': contract_id, 'members': 1, 'lastPayments': 3},
            auth=BGBILLING_AUTH,
            timeout=REQUEST_TIMEOUT
        )
        if response.status_code == 200:
            logger.info('Payments request sent')
            return response.json()
        else:
            logger.error(f'Failed to get payments: {response.status_code}')
            return None
    except Timeout:
        logger.error('Timeout connecting to BGBilling API for payments')
        raise
    except RequestException as e:
        logger.error(f'Error getting payments from BGBilling: {e}')
        raise