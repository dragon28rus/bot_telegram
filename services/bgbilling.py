import aiohttp
import asyncio
from aiohttp import ClientTimeout, ClientError
from typing import Union
from config import BGBILLING_API_URL, BGBILLING_AUTH
from logger import logger

# Таймаут для всех запросов (секунды)
REQUEST_TIMEOUT = 5


async def authenticate(contract_number: str, password: str) -> Union[dict, None]:
    """
    Авторизация пользователя в BGBilling.
    """
    try:
        async with aiohttp.ClientSession(
            auth=aiohttp.BasicAuth(*BGBILLING_AUTH),
            timeout=ClientTimeout(total=REQUEST_TIMEOUT)
        ) as session:
            async with session.get(
                f"{BGBILLING_API_URL}/jsonWebApi/login",
                params={"login": contract_number, "password": password, "midAuth": 0}
            ) as response:
                if response.status == 200:
                    return await response.json()
                logger.error(f"Authentication failed with status {response.status}")
                return None
    except aiohttp.ClientTimeout:
        logger.error("Timeout connecting to BGBilling API")
        return None
    except ClientError as e:
        logger.error(f"Error connecting to BGBilling API: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in authentication: {e}")
        return None
    finally:
        await asyncio.sleep(0.05)


async def save_chat_id(contract_id: str, chat_id: str) -> bool:
    """
    Заглушка. На будущее: сохранение chat_id в параметрах договора на стороне BGBilling.
    """
    logger.info(f"Stub: save_chat_id(contract_id={contract_id}, chat_id={chat_id})")
    await asyncio.sleep(0.05)
    return True


async def get_balance(contract_id: str) -> Union[dict, None]:
    """
    Получает баланс договора из BGBilling.
    """
    try:
        async with aiohttp.ClientSession(
            auth=aiohttp.BasicAuth(*BGBILLING_AUTH),
            timeout=ClientTimeout(total=REQUEST_TIMEOUT)
        ) as session:
            async with session.get(
                f"{BGBILLING_API_URL}/jsonWebApi/contractBalance",
                params={"contractId": contract_id}
            ) as response:
                if response.status == 200:
                    return await response.json()
                logger.error(f"Failed to get balance: {response.status}")
                return None
    except aiohttp.ClientTimeout:
        logger.error("Timeout connecting to BGBilling API for balance")
        return None
    except ClientError as e:
        logger.error(f"Error getting balance from BGBilling: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error getting balance: {e}")
        return None
    finally:
        await asyncio.sleep(0.05)


async def get_tariff_plan(contract_id: str) -> Union[dict, None]:
    """
    Получает тарифные планы по договору.
    """
    try:
        async with aiohttp.ClientSession(
            auth=aiohttp.BasicAuth(*BGBILLING_AUTH),
            timeout=ClientTimeout(total=REQUEST_TIMEOUT)
        ) as session:
            async with session.get(
                f"{BGBILLING_API_URL}/jsonWebApi/contractTarifPlans",
                params={"contractId": contract_id}
            ) as response:
                if response.status == 200:
                    return await response.json()
                logger.error(f"Failed to get tariff: {response.status}")
                return None
    except aiohttp.ClientTimeout:
        logger.error("Timeout connecting to BGBilling API for tariff")
        return None
    except ClientError as e:
        logger.error(f"Error getting tariff from BGBilling: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error getting tariff: {e}")
        return None
    finally:
        await asyncio.sleep(0.05)


async def get_tariff_cost(contract_id: str) -> Union[dict, None]:
    """
    Заглушка. На будущее: получение стоимости тарифного плана.
    """
    logger.info(f"Stub: get_tariff_cost(contract_id={contract_id})")
    await asyncio.sleep(0.05)
    return None


async def get_news(contract_id: str) -> Union[dict, None]:
    """
    Получение последних новостей по договору из BGBilling.
    """
    try:
        async with aiohttp.ClientSession(
            auth=aiohttp.BasicAuth(*BGBILLING_AUTH),
            timeout=ClientTimeout(total=REQUEST_TIMEOUT)
        ) as session:
            async with session.get(
                f"{BGBILLING_API_URL}/jsonWebApi/newsList",
                params={"contractId": contract_id}
            ) as response:
                if response.status == 200:
                    return await response.json()
                logger.error(f"Failed to get news: {response.status}")
                return None
    except aiohttp.ClientTimeout:
        logger.error("Timeout connecting to BGBilling API for news")
        return None
    except ClientError as e:
        logger.error(f"Error getting news from BGBilling: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error getting news: {e}")
        return None
    finally:
        await asyncio.sleep(0.05)


async def get_last_payments(contract_id: str) -> Union[dict, None]:
    """
    Получение последних платежей по договору.
    """
    try:
        async with aiohttp.ClientSession(
            auth=aiohttp.BasicAuth(*BGBILLING_AUTH),
            timeout=ClientTimeout(total=REQUEST_TIMEOUT)
        ) as session:
            async with session.get(
                f"{BGBILLING_API_URL}/jsonWebApi/lastContractPayments",
                params={"contractId": contract_id, "members": 1, "lastPayments": 3}
            ) as response:
                if response.status == 200:
                    return await response.json()
                logger.error(f"Failed to get payments: {response.status}")
                return None
    except aiohttp.ClientTimeout:
        logger.error("Timeout connecting to BGBilling API for payments")
        return None
    except ClientError as e:
        logger.error(f"Error getting payments from BGBilling: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error getting payments: {e}")
        return None
    finally:
        await asyncio.sleep(0.05)
