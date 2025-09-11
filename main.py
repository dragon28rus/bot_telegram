import asyncio
import signal
import sys
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from config import BOT_TOKEN, WEBHOOK_URL, WEBHOOK_PATH
from logger import logger, set_chat_id
from db import init_db
from handlers import (
    auth_router,
    check_router,
    support_router,
    user_router,
    handle_billing_notification,
    handle_broadcast_notification,
)

def register_handlers(dp: Dispatcher):
    dp.include_router(auth_router)
    dp.include_router(check_router)
    dp.include_router(support_router)
    dp.include_router(user_router)

async def retry_with_backoff(bot: Bot, action: str, max_attempts=3, base_delay=1.0, **kwargs):
    for attempt in range(max_attempts):
        try:
            if action == "set_webhook":
                return await bot.set_webhook(kwargs.get("url"), drop_pending_updates=True)
            elif action == "delete_webhook":
                return await bot.delete_webhook(drop_pending_updates=True)
            else:
                raise ValueError(f"Unknown action: {action}")
        except Exception as e:
            delay = base_delay * (2 ** attempt)
            logger.error(f"Retry error for {action}: {e}. Retrying in {delay} seconds.")
            await asyncio.sleep(delay)
    raise RuntimeError(f"Failed to perform {action} after {max_attempts} attempts")

async def on_startup(bot: Bot, app: web.Application):
    set_chat_id("system")
    try:
        await init_db()
        await retry_with_backoff(bot, "set_webhook", url=WEBHOOK_URL + WEBHOOK_PATH)
        logger.info("Webhook set successfully")
    except Exception as e:
        logger.error(f"Startup error: {e}")

async def on_shutdown(bot: Bot, app: web.Application):
    set_chat_id("system")
    try:
        webhook_info = await bot.get_webhook_info()
        if webhook_info.url:
            await retry_with_backoff(bot, "delete_webhook")
            logger.info("Webhook deleted successfully")

        # Закрываем сессию бота
        try:
            session = await bot.get_session()
            if session and not session.closed:
                await session.close()
        except:
            pass

        logger.info("Bot session closed")
    except Exception as e:
        logger.error(f"Shutdown error: {e}")
    finally:
        await asyncio.sleep(0.5)

async def init_app():
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML")
    )
    dp = Dispatcher()
    register_handlers(dp)

    app = web.Application()

    async def telegram_webhook(request):
        try:
            data = await request.json()
        except Exception as e:
            logger.error(f"Invalid webhook data: {e}")
            return web.Response(status=400, text="Invalid request")

        try:
            await dp.feed_webhook_update(bot, data)
            return web.Response(status=200, text="ok")
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            return web.Response(status=500, text="Internal error")

    # Роуты
    app.router.add_post(WEBHOOK_PATH, telegram_webhook)
    app.router.add_post("/billing", lambda request: handle_billing_notification(request, bot))
    app.router.add_post("/broadcast", lambda request: handle_broadcast_notification(request, bot))
    
    # Health check endpoint
    async def health_check(request):
        return web.Response(text="Bot is running", status=200)
    
    app.router.add_get("/health", health_check)

    app.on_startup.append(lambda app: on_startup(bot, app))
    app.on_shutdown.append(lambda app: on_shutdown(bot, app))

    return app

async def main():
    app = await init_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8443)
    await site.start()
    logger.info("Bot started on port 8443")

    # Обработка сигналов завершения
    stop_event = asyncio.Event()
    
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}")
        stop_event.set()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        await stop_event.wait()
        logger.info("Shutdown signal received")
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    finally:
        logger.info("Cleaning up...")
        await runner.cleanup()
        logger.info("Bot stopped")

if __name__ == "__main__":
    asyncio.run(main())