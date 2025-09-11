import asyncio
import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.types import BotCommand
from config import BOT_TOKEN, WEBHOOK_URL, WEBHOOK_PATH
from handlers import register_handlers, handle_billing_notification, handle_broadcast_notification
from logger import logger, set_chat_id
from aiohttp import web, ClientSession
from db import init_db

async def retry_with_backoff(coro, max_attempts=3, base_delay=1.0):
    """Retries a coroutine with exponential backoff on Telegram rate limit errors."""
    for attempt in range(max_attempts):
        try:
            return await coro
        except aiohttp.ClientResponseError as e:
            if e.status == 429:  # Too Many Requests
                retry_after = int(e.headers.get('Retry-After', base_delay))
                logger.warning(f"Rate limit hit, retrying after {retry_after} seconds")
                await asyncio.sleep(retry_after)
                base_delay *= 2  # Exponential backoff
            else:
                raise
        except Exception as e:
            logger.error(f"Retry error: {e}")
            if attempt == max_attempts - 1:
                raise
            await asyncio.sleep(base_delay)
            base_delay *= 2

async def on_startup(bot: Bot, webhook_url: str, app: web.Application):
    set_chat_id('system')
    try:
        init_db()
        await retry_with_backoff(bot.set_webhook(webhook_url, drop_pending_updates=True))
        await bot.set_my_commands([
            BotCommand(command="/start", description="Начать работу с ботом"),
            BotCommand(command="/menu", description="Показать меню"),
            BotCommand(command="/support", description="Связаться с техподдержкой"),
            BotCommand(command="/check_bot", description="Проверить статус бота")
        ])
        logger.info("Webhook set, commands updated, and DB initialized")
        app['aiohttp_session'] = ClientSession()
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise

async def on_shutdown(bot: Bot, app: web.Application):
    set_chat_id('system')
    try:
        await retry_with_backoff(bot.delete_webhook(drop_pending_updates=True))
        await retry_with_backoff(bot.close())
        if 'aiohttp_session' in app and not app['aiohttp_session'].closed:
            await app['aiohttp_session'].close()
        logger.info("Webhook deleted, bot closed, and aiohttp session closed")
    except Exception as e:
        logger.error(f"Shutdown error: {e}")
    finally:
        await asyncio.sleep(0.5)  # Increased delay for cleanup

def main():
    set_chat_id('system')
    try:
        bot = Bot(token=BOT_TOKEN)
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)
        
        # Register handlers
        register_handlers(dp)
        
        app = web.Application()
        app.router.add_post('/billing_notification', lambda request: handle_billing_notification(request, bot))
        app.router.add_post('/broadcast_notification', lambda request: handle_broadcast_notification(request, bot))
        
        # Setup aiogram webhook
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