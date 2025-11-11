from aiohttp import web
from aiogram import Bot
from config import BOT_TOKEN
from db.users import get_chat_id_by_contract_id, get_all_chat_ids
from logger import logger, set_chat_id  # 👈 добавили set_chat_id

async def handle_billing_notification(request: web.Request) -> web.Response:
    """
    Обработка уведомления от биллинга:
    передаётся contract_id + сообщение, бот отправляет пользователю.
    """
    bot = request.app['bot']
    data = await request.json()
    contract_id = data.get("contract_id")
    message = data.get("message")

    # Привязываем chat_id для логов
    set_chat_id(f"contract:{contract_id}")

    if not contract_id or not message:
        logger.error("Некорректные данные от биллинга")
        return web.json_response({"status": "error", "reason": "invalid data"}, status=400)

    chat_id = await get_chat_id_by_contract_id(contract_id)
    if not chat_id:
        logger.warning(f"Не найден chat_id для договора {contract_id}")
        return web.json_response({"status": "error", "reason": "user not found"}, status=404)

    try:
        await bot.send_message(chat_id, message)
        logger.info(f"Сообщение передано пользователю {chat_id} по договору {contract_id}")
        return web.json_response({"status": "ok"})
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения пользователю {chat_id}: {e}")
        return web.json_response({"status": "error", "reason": str(e)}, status=500)


async def handle_broadcast_notification(request: web.Request) -> web.Response:
    """
    Обработка рассылки от биллинга:
    сообщение отправляется всем пользователям.
    """
    data = await request.json()
    message = data.get("message")

    # Привязываем chat_id как broadcast
    set_chat_id("broadcast")

    if not message:
        logger.error("Сообщение для рассылки пустое")
        return web.json_response({"status": "error", "reason": "empty message"}, status=400)

    chat_ids = await get_all_chat_ids()
    sent, failed = 0, 0
    for chat_id in chat_ids:
        try:
            await bot.send_message(chat_id, message)
            sent += 1
        except Exception as e:
            failed += 1
            logger.error(f"Ошибка при рассылке пользователю {chat_id}: {e}")

    logger.info(f"Рассылка завершена: успешно={sent}, ошибки={failed}")
    return web.json_response({"status": "ok", "sent": sent, "failed": failed})
