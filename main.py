# main.py
import asyncio
from aiogram import Bot, Dispatcher
from aiohttp import web

from config import BOT_TOKEN, BILLING_API_TOKEN
from logger import logger
from handlers import admin  # подключим админский роутер для примера
from webhooks.billing import handle_billing_notification, handle_broadcast_notification

async def main():
    # --- Telegram bot ---
    bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher()

    # Подключение роутеров
    dp.include_router(admin.router)  # пока только админ, потом добавим все остальные

    # --- aiohttp web server ---
    app = web.Application()

    # Добавляем роуты для вебхуков биллинга
    app.router.add_post(
        "/billing/notify", lambda r: handle_billing_notification(r, bot)
    )
    app.router.add_post(
        "/billing/broadcast", lambda r: handle_broadcast_notification(r, bot)
    )

    logger.info("🚀 Бот запускается...")

    # Запускаем бота и вебсервер параллельно
    await asyncio.gather(
        dp.start_polling(bot),
        web._run_app(app, host="0.0.0.0", port=8080)
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("🛑 Бот остановлен")