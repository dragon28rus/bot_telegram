#### handlers/billing.py
from aiohttp import web
from db import get_chat_id_by_contract_id, get_all_chat_ids
from logger import logger, set_chat_id

async def handle_billing_notification(request, bot):
    """
    Обрабатывает уведомления от биллинга для конкретного пользователя по contract_id.
    
    Args:
        request: HTTP-запрос с JSON-данными (contract_id, message)
        bot: Объект бота для отправки сообщений
    Returns:
        web.json_response: Ответ с результатом обработки
    """
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

async def handle_broadcast_notification(request, bot):
    """
    Обрабатывает уведомления от биллинга для отправки всем подписчикам.
    
    Args:
        request: HTTP-запрос с JSON-данными (message)
        bot: Объект бота для отправки сообщений
    Returns:
        web.json_response: Ответ с результатом обработки
    """
    try:
        data = await request.json()
        message = data.get('message')
        if not message:
            set_chat_id('system')
            logger.error('Invalid broadcast notification: missing message')
            return web.json_response({'status': 'error', 'message': 'Missing message'}, status=400)
        
        chat_ids = get_all_chat_ids()
        if not chat_ids:
            set_chat_id('system')
            logger.warning('No subscribers found for broadcast')
            return web.json_response({'status': 'error', 'message': 'No subscribers found'}, status=404)
        
        for chat_id in chat_ids:
            set_chat_id(chat_id)
            try:
                await bot.send_message(chat_id, f"Уведомление от биллинга: {message}")
                logger.info(f'Broadcast notification sent to user with chat_id: {chat_id}')
            except Exception as e:
                logger.error(f'Error sending broadcast to user with chat_id {chat_id}: {e}')
        
        set_chat_id('system')
        logger.info('Broadcast notification sent to all subscribers')
        return web.json_response({'status': 'ok'})
    except Exception as e:
        set_chat_id('system')
        logger.error(f'Error processing broadcast notification: {e}')
        return web.json_response({'status': 'error', 'message': str(e)}, status=500)
