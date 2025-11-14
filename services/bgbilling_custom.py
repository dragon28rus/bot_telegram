# services/bgbilling_custom.py
# Кастомное Web API биллинга (нестандартные методы)

import aiohttp
import asyncio
from aiohttp import ClientTimeout, ClientError
from typing import Optional, Dict, Any
from config import BGBILLING_API_URL, BGBILLING_AUTH
from logger import logger

# Таймаут для всех запросов (секунды)
REQUEST_TIMEOUT = 5


async def request_promised_payment(contract_id: str, amount: int) -> Optional[Dict[str, Any]]:
    """
    Запрос обещанного платежа (понижение лимита).
    Эндпоинт: /api/rest/0/telegramApi/lowerLimit?cid={contract_id}&amount={summ}

    Возвращает:
        При успехе:
            {
                "success": true,
                "contractId": int,
                "days": int,
                "newLimit": float,
                "message": str
            }
        При ошибке (например, уже был обещанный платёж):
            {
                "success": false,
                "error": str
            }
        None — при сетевых/таймаут ошибках.
    """
    url = f"{BGBILLING_API_URL}/api/rest/0/telegramApi/lowerLimit"
    params = {
        "cid": contract_id,
        "amount": amount
    }
    logger.debug(f"[request_promised_payment] Запрос {url} params={params}")

    try:
        async with aiohttp.ClientSession(
            auth=aiohttp.BasicAuth(*BGBILLING_AUTH),
            timeout=ClientTimeout(total=REQUEST_TIMEOUT),
            connector=aiohttp.TCPConnector(ssl=False)  # если self-signed сертификат
        ) as session:
            async with session.get(url, params=params) as response:
                text = await response.text()
                logger.debug(f"[request_promised_payment] Ответ {response.status}: {text[:1000]}")

                if response.status != 200:
                    logger.error(f"[request_promised_payment] HTTP {response.status}")
                    return None

                data = await response.json()

                # Проверяем наличие поля success
                if data.get("success") is True:
                    result = {
                        "success": True,
                        "contract_id": str(data.get("contractId")),
                        "days": data.get("days"),
                        "new_limit": data.get("newLimit"),
                        "message": data.get("message")
                    }
                    logger.info(f"[request_promised_payment] Обещанный платёж успешен: {result}")
                    return result
                else:
                    error_msg = data.get("error", "Неизвестная ошибка")
                    logger.warning(f"[request_promised_payment] Обещанный платёж отклонён: {error_msg}")
                    return {
                        "success": False,
                        "error": error_msg
                    }

    except asyncio.TimeoutError:
        logger.error("[request_promised_payment] Таймаут")
        return None
    except ClientError as e:
        logger.error(f"[request_promised_payment] ClientError: {e}")
        return None
    except Exception as e:
        logger.exception(f"[request_promised_payment] Unexpected error: {e}")
        return None
    finally:
        await asyncio.sleep(0.05)