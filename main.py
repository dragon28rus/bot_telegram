import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from config import BOT_TOKEN, WEBHOOK_URL, WEBHOOK_PATH
from handlers import register_handlers, handle_billing_notification, handle_broadcast_notification
from logger import logger, set_chat_id
from aiohttp import web
from db import init_db

async def on_startup(bot: Bot, webhook_url: str):
    set_chat_id('system')
    init_db()
    await bot.set_webhook(webhook_url)
    logger.info("Webhook set and DB initialized")

async def on_shutdown(bot: Bot):
    set_chat_id('system')
    await bot.delete_webhook()
    logger.info("Webhook deleted")

def main():
    set_chat_id('system')
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
    
    app.on_startup.append(lambda _: on_startup(bot, WEBHOOK_URL + WEBHOOK_PATH))
    app.on_shutdown.append(lambda _: on_shutdown(bot))
    
    logger.info("Starting bot")
    web.run_app(app, host='0.0.0.0', port=8444)

if __name__ == '__main__':
    main()