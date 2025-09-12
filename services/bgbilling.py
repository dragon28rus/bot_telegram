import aiohttp
import asyncio
from aiohttp import ClientTimeout, ClientError
from typing import Optional, Union
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


async def get_balance(contract_id: str) -> Optional[dict]:
    """
    Получает баланс договора.

    Args:
        contract_id: Номер договора

    Returns:
        dict с ключами:
        {
            "balance": str,
            "currency": str
        }
        или None, если не удалось получить данные.
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
                    data = await response.json()
                    if data.get("status") == "Ok":
                        return {
                            "balance": data.get("sum"),
                            "currency": data.get("currencyTitleMedium")
                        }
                    return None
                logger.error(f"Ошибка получения баланса: {response.status}")
                return None
    except aiohttp.ClientTimeout:
        logger.error("Таймаут при получении баланса")
        return None
    except Exception as e:
        logger.error(f"Ошибка получения баланса: {e}")
        return None
    finally:
        await asyncio.sleep(0.05)


async def get_tariff_plan(contract_id: str) -> Optional[dict]:
    """
    Получает текущий тарифный план договора.

    Args:
        contract_id: Номер договора

    Returns:
        dict с ключами:
        {
            "title": str,
            "dateFrom": str,
            "dateTo": str | None
        }
        или None, если не удалось получить данные.
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
                    data = await response.json()
                    if data.get("status") == "Ok":
                        plans = data.get("contractTarifPlans", [])
                        if plans:
                            plan = plans[0]
                            return {
                                "title": plan.get("title"),
                                "dateFrom": plan.get("dateFrom"),
                                "dateTo": plan.get("dateTo") or None,
                            }
                        return None
                logger.error(f"Ошибка получения тарифа: {response.status}")
                return None
    except aiohttp.ClientTimeout:
        logger.error("Таймаут при получении тарифа")
        return None
    except Exception as e:
        logger.error(f"Ошибка получения тарифа: {e}")
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


async def get_payments(contract_id: str, limit: int = 3) -> Optional[list[dict]]:
    """
    Получает последние платежи по договору.

    Args:
        contract_id: Номер договора
        limit: количество последних платежей (по умолчанию 3)

    Returns:
        list словарей вида:
        [
            {
                "date": "02.09.2025",
                "sum": "600,00",
                "type": "Сбербанк эква́йринг"
            },
            ...
        ]
        или None, если не удалось получить данные.
    """
    try:
        async with aiohttp.ClientSession(
            auth=aiohttp.BasicAuth(*BGBILLING_AUTH),
            timeout=ClientTimeout(total=REQUEST_TIMEOUT)
        ) as session:
            async with session.get(
                f"{BGBILLING_API_URL}/jsonWebApi/lastContractPayments",
                params={"contractId": contract_id, "members": 1, "lastPayments": limit}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("status") == "Ok":
                        return [
                            {
                                "date": p.get("date"),
                                "sum": p.get("sum"),
                                "type": p.get("typeTitle"),
                            }
                            for p in data.get("contractPayments", [])
                        ]
                    return None
                logger.error(f"Ошибка получения платежей: {response.status}")
                return None
    except aiohttp.ClientTimeout:
        logger.error("Таймаут при получении платежей")
        return None
    except Exception as e:
        logger.error(f"Ошибка получения платежей: {e}")
        return None
    finally:
        await asyncio.sleep(0.05)
