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


async def retry_with_backoff(bot: Bot, action: str, max_attempts=3, base_delay=1.0, **kwargs):
    """Retries a Telegram API action with exponential backoff on rate limit errors."""
    for attempt in range(max_attempts):
        try:
            if action == "set_webhook":
                return await bot.set_webhook(kwargs.get("url"), drop_pending_updates=True)
            elif action == "delete_webhook":
                return await bot.delete_webhook(drop_pending_updates=True)
            elif action == "close":
                return await bot.close()
            else:
                raise ValueError(f"Unknown action: {action}")
        except aiohttp.ClientResponseError as e:
            if e.status == 429:  # Too Many Requests
                retry_after = int(e.headers.get("Retry-After", base_delay))
                logger.warning(f"Rate limit hit for {action}, retrying after {retry_after} seconds")
                await asyncio.sleep(retry_after)
                base_delay *= 2  # Exponential backoff
            elif e.status in (400, 401, 403):
                logger.error(f"Unrecoverable error {e.status} for {action}: {e}")
                raise
            else:
                raise
        except Exception as e:
            logger.error(f"Retry error for {action}: {e}")
            if attempt == max_attempts - 1:
                raise
            await asyncio.sleep(base_delay)
            base_delay *= 2


async def on_startup(bot: Bot, webhook_url: str, app: web.Application):
    set_chat_id("system")
    try:
        init_db()
        await retry_with_backoff(bot, "set_webhook", url=webhook_url)
        await bot.set_my_commands([
            BotCommand(command="/start", description="Начать работу с ботом"),
            BotCommand(command="/menu", description="Показать меню"),
            BotCommand(command="/support", description="Связаться с техподдержкой"),
            BotCommand(command="/check_bot", description="Проверить статус бота"),
        ])
        logger.info("Webhook set, commands updated, and DB initialized")
        app["aiohttp_session"] = ClientSession()
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise


async def on_shutdown(bot: Bot, app: web.Application):
    set_chat_id("system")
    try:
        webhook_info = await bot.get_webhook_info()
        if webhook_info.url:
            await retry_with_backoff(bot, "delete_webhook")
        await retry_with_backoff(bot, "close")

        session = app.get("aiohttp_session")
        if session and not session.closed:
            await session.close()

        logger.info("Webhook deleted, bot closed, and aiohttp session closed")
    except Exception as e:
        logger.error(f"Shutdown error: {e}")
    finally:
        await asyncio.sleep(1.0)  # Increased delay for cleanup


async def billing_handler(request: web.Request, bot: Bot):
    return await handle_billing_notification(request, bot)


async def broadcast_handler(request: web.Request, bot: Bot):
    return await handle_broadcast_notification(request, bot)


async def main():
    set_chat_id("system")
    try:
        bot = Bot(token=BOT_TOKEN)
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)

        register_handlers(dp)

        app = web.Application()
        app.router.add_post("/billing_notification", lambda request: billing_handler(request, bot))
        app.router.add_post("/broadcast_notification", lambda request: broadcast_handler(request, bot))

        webhook_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
        webhook_handler.register(app, path=WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)

        app.on_startup.append(lambda app: on_startup(bot, WEBHOOK_URL + WEBHOOK_PATH, app))
        app.on_shutdown.append(lambda app: on_shutdown(bot, app))

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", 8444)
        logger.info("Starting bot on 0.0.0.0:8444")
        await site.start()

        try:
            await asyncio.Event().wait()  # Run forever
        finally:
            await runner.cleanup()
    except Exception as e:
        logger.error(f"Main loop error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
