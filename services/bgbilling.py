import aiohttp
import asyncio
from aiohttp import ClientTimeout, ClientError
from typing import Optional, Union, List, Dict, Any
from config import BGBILLING_API_URL, BGBILLING_AUTH
from logger import logger

# Таймаут для всех запросов (секунды)
REQUEST_TIMEOUT = 5


async def authenticate(contract_number: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Выполняет запрос /jsonWebApi/login и возвращает словарь с:
      - 'status' (как пришёл в API),
      - оригинальными ключами 'contractId'/'contractTitle' (если есть),
      - нормализованными 'contract_id' (str) и 'contract_title'.
    Это даёт обратно-совместимость для разных хэндлеров.
    """
    url = f"{BGBILLING_API_URL}/jsonWebApi/login"
    params = {"login": contract_number, "password": password, "midAuth": 0}
    logger.debug(f"[authenticate] Запрос {url} params={params}")

    try:
        async with aiohttp.ClientSession(
            auth=aiohttp.BasicAuth(*BGBILLING_AUTH),
            timeout=ClientTimeout(total=REQUEST_TIMEOUT),
            connector=aiohttp.TCPConnector(ssl=False)  # если у вас self-signed, иначе можно убрать
        ) as session:
            async with session.get(url, params=params) as response:
                text = await response.text()
                logger.debug(f"[authenticate] Ответ {response.status}: {text[:1000]}")

                if response.status != 200:
                    logger.error(f"[authenticate] HTTP {response.status}")
                    return None

                data = await response.json()

                # если API вернул статус Ok — нормализуем и возвращаем
                status = data.get("status")
                contract_id_raw = data.get("contractId") or data.get("contract_id")
                contract_title_raw = data.get("contractTitle") or data.get("contract_title") or contract_number

                result = {
                    "status": status,
                    "contractId": contract_id_raw,
                    "contractTitle": contract_title_raw,
                    # нормализованные ключи (строка для хранения в БД)
                    "contract_id": str(contract_id_raw) if contract_id_raw is not None else None,
                    "contract_title": contract_title_raw
                }
                logger.debug(f"[authenticate] Нормализованный результат: {result}")
                return result

    except asyncio.TimeoutError:
        logger.error("[authenticate] Таймаут")
        return None
    except ClientError as e:
        logger.error(f"[authenticate] ClientError: {e}")
        return None
    except Exception as e:
        logger.exception(f"[authenticate] Unexpected error: {e}")
        return None
    finally:
        # небольшой sleep, как в остальном модуле (если нужен)
        await asyncio.sleep(0.05)


async def get_balance(contract_id: str) -> Optional[dict]:
    """Получает баланс договора."""
    url = f"{BGBILLING_API_URL}/jsonWebApi/contractBalance"
    params = {"contractId": contract_id}
    logger.debug(f"[get_balance] Запрос {url} params={params}")

    try:
        async with aiohttp.ClientSession(
            auth=aiohttp.BasicAuth(*BGBILLING_AUTH),
            timeout=ClientTimeout(total=REQUEST_TIMEOUT),
            connector=aiohttp.TCPConnector(ssl=False)
        ) as session:
            async with session.get(url, params=params) as response:
                text = await response.text()
                logger.debug(f"[get_balance] Ответ {response.status}: {text}")
                if response.status == 200:
                    data = await response.json()
                    if data.get("status") == "Ok":
                        return {
                            "balance": data.get("sum"),
                            "currency": data.get("currencyTitleMedium")
                        }
                    return None
                return None
    except aiohttp.ClientTimeout:
        logger.error("[get_balance] Таймаут")
        return None
    except Exception as e:
        logger.exception(f"[get_balance] Ошибка: {e}")
        return None
    finally:
        await asyncio.sleep(0.05)


async def get_tariff_plan(contract_id: str) -> Optional[dict]:
    """Получает текущий тарифный план договора."""
    url = f"{BGBILLING_API_URL}/jsonWebApi/contractTarifPlans"
    params = {"contractId": contract_id}
    logger.debug(f"[get_tariff_plan] Запрос {url} params={params}")

    try:
        async with aiohttp.ClientSession(
            auth=aiohttp.BasicAuth(*BGBILLING_AUTH),
            timeout=ClientTimeout(total=REQUEST_TIMEOUT),
            connector=aiohttp.TCPConnector(ssl=False)
        ) as session:
            async with session.get(url, params=params) as response:
                text = await response.text()
                logger.debug(f"[get_tariff_plan] Ответ {response.status}: {text}")
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
                return None
    except aiohttp.ClientTimeout:
        logger.error("[get_tariff_plan] Таймаут")
        return None
    except Exception as e:
        logger.exception(f"[get_tariff_plan] Ошибка: {e}")
        return None
    finally:
        await asyncio.sleep(0.05)


async def get_news(contract_id: str) -> Union[dict, None]:
    """Получение последних новостей по договору из BGBilling."""
    url = f"{BGBILLING_API_URL}/jsonWebApi/newsList"
    params = {"contractId": contract_id}
    logger.debug(f"[get_news] Запрос {url} params={params}")

    try:
        async with aiohttp.ClientSession(
            auth=aiohttp.BasicAuth(*BGBILLING_AUTH),
            timeout=ClientTimeout(total=REQUEST_TIMEOUT),
            connector=aiohttp.TCPConnector(ssl=False)
        ) as session:
            async with session.get(url, params=params) as response:
                text = await response.text()
                logger.debug(f"[get_news] Ответ {response.status}: {text}")
                if response.status == 200:
                    return await response.json()
                return None
    except aiohttp.ClientTimeout:
        logger.error("[get_news] Таймаут")
        return None
    except ClientError as e:
        logger.error(f"[get_news] ClientError: {e}")
        return None
    except Exception as e:
        logger.exception(f"[get_news] Unexpected error: {e}")
        return None
    finally:
        await asyncio.sleep(0.05)


async def get_payments(contract_id: str, limit: int = 3) -> Optional[List[Dict]]:
    """Получает последние платежи по договору."""
    url = f"{BGBILLING_API_URL}/jsonWebApi/lastContractPayments"
    params = {"contractId": contract_id, "members": 1, "lastPayments": limit}
    logger.debug(f"[get_payments] Запрос {url} params={params}")

    try:
        async with aiohttp.ClientSession(
            auth=aiohttp.BasicAuth(*BGBILLING_AUTH),
            timeout=ClientTimeout(total=REQUEST_TIMEOUT),
            connector=aiohttp.TCPConnector(ssl=False)
        ) as session:
            async with session.get(url, params=params) as response:
                text = await response.text()
                logger.debug(f"[get_payments] Ответ {response.status}: {text}")
                if response.status == 200:
                    data = await response.json()
                    if data.get("status") == "Ok":
                        return [
                            {
                                "date": p.get("date"), 
                                "sum": p.get("sum"), 
                                "type": p.get("typeTitle")
                            }
                            for p in data.get("contractPayments", [])
                        ]
                    return None
                return None
    except aiohttp.ClientTimeout:
        logger.error("[get_payments] Таймаут")
        return None
    except Exception as e:
        logger.exception(f"[get_payments] Ошибка: {e}")
        return None
    finally:
        await asyncio.sleep(0.05)


# ==============================
# Заглушки для будущих методов
# ==============================

async def save_chat_id(contract_id: str, chat_id: str) -> None:
    """
    Заглушка для сохранения chat_id на стороне биллинга.
    Пока ничего не делает, но пишет лог.
    """
    logger.debug(f"[save_chat_id] Вызвана заглушка для contract_id={contract_id}, chat_id={chat_id}")
    await asyncio.sleep(0.01)


async def get_tariff_cost(contract_id: str) -> Optional[dict]:
    """
    Заглушка для получения стоимости тарифного плана.
    Пока не реализовано.
    """
    logger.debug(f"[get_tariff_cost] Вызвана заглушка для contract_id={contract_id}")
    await asyncio.sleep(0.01)
    return None
