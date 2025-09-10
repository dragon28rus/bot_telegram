### main.py
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from aiohttp import web
from config import BOT_TOKEN, WEBHOOK_URL, WEBHOOK_PATH
from logger import logger, set_chat_id
from handlers import register_handlers, handle_billing_notification
from db import init_db

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

async def on_startup(_):
    set_chat_id('system')
    await bot.set_webhook(WEBHOOK_URL + WEBHOOK_PATH)
    init_db()
    register_handlers(dp)
    logger.info('Webhook set and DB initialized')
    # Настройка вебхука для биллинга
    app = web.Application()
    app.router.add_post('/billing_notification', lambda request: handle_billing_notification(request, bot))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8444)
    await site.start()
    logger.info('Billing notification webhook started')

async def on_shutdown(_):
    set_chat_id('system')
    await bot.delete_webhook()
    await storage.close()
    await storage.wait_closed()
    logger.info('Webhook removed')

if __name__ == '__main__':
    from aiogram.utils.executor import start_webhook
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host='0.0.0.0',
        port=8443
    )