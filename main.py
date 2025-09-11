import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from config import BOT_TOKEN, WEBHOOK_URL, WEBHOOK_PATH
from handlers import register_handlers, handle_billing_notification, handle_broadcast_notification
from logger import logger, set_chat_id
from aiohttp import web, ClientSession
from db import init_db

async def on_startup(bot: Bot, webhook_url: str, app: web.Application):
    set_chat_id('system')
    try:
        init_db()
        await bot.set_webhook(webhook_url, drop_pending_updates=True)
        logger.info("Webhook set and DB initialized")
        app['aiohttp_session'] = ClientSession()
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise

async def on_shutdown(bot: Bot, app: web.Application):
    set_chat_id('system')
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.close()
        if 'aiohttp_session' in app and not app['aiohttp_session'].closed:
            await app['aiohttp_session'].close()
        logger.info("Webhook deleted, bot closed, and aiohttp session closed")
    except Exception as e:
        logger.error(f"Shutdown error: {e}")
    finally:
        await asyncio.sleep(0.25)  # Увеличена задержка для завершения операций

def main():
    set_chat_id('system')
    try:
        bot = Bot(token=BOT_TOKEN)
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)
        
        # Регистрация обработчиков
        register_handlers(dp)
        
        app = web.Application()
        app.router.add_post('/billing_notification', lambda request: handle_billing_notification(request, bot))
        app.router.add_post('/broadcast_notification', lambda request: handle_broadcast_notification(request, bot))
        
        # Настройка вебхука aiogram
        webhook_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
        webhook_handler.register(app, path=WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)
        
        app.on_startup.append(lambda app: on_startup(bot, WEBHOOK_URL + WEBHOOK_PATH, app))
        app.on_shutdown.append(lambda app: on_shutdown(bot, app))
        
        logger.info("Starting bot")
        web.run_app(app, host='0.0.0.0', port=8444)
    except Exception as e:
        logger.error(f"Main loop error: {e}")
        raise

if __name__ == '__main__':
    main()