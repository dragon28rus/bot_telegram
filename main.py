# main.py
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiohttp import web

from config import BOT_TOKEN, BILLING_WEBHOOK_PORT
from logger import logger
from handlers import admin, start, auth, unlink, balance, news, tariff, payments, support
from webhooks.billing import handle_billing_notification, handle_broadcast_notification
from db.users import init_users_table
from db.support import init_support_table
from keyboards import main_menu



async def main():
    # --- инициализация базы данных ---
    await init_users_table()
    await init_support_table()

    # --- настройка Telegram бота ---
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML")
    )

    # Удаляем webhook, иначе polling не запустится
    await bot.delete_webhook(drop_pending_updates=True)

    dp = Dispatcher()

    # --- подключаем роутеры ---
    dp.include_router(start.router)
    dp.include_router(admin.router)
    dp.include_router(auth.router)
    dp.include_router(balance.router)
    dp.include_router(news.router)
    dp.include_router(tariff.router)
    dp.include_router(payments.router)
    dp.include_router(unlink.router)
    dp.include_router(support.router)
    dp.include_router(main_menu.router)

    # --- aiohttp сервер для биллинга ---
    app = web.Application()

    # Эндпоинт: сообщение конкретному пользователю
    app.router.add_post(
        "/billing/notify", lambda r: handle_billing_notification(r, bot)
    )
    # Эндпоинт: рассылка всем пользователям
    app.router.add_post(
        "/billing/broadcast", lambda r: handle_broadcast_notification(r, bot)
    )

    logger.info("🚀 Бот запускается...")

    # Запускаем бота и вебсервер параллельно
    await asyncio.gather(
        dp.start_polling(bot),
        web._run_app(app, host="0.0.0.0", port=BILLING_WEBHOOK_PORT)
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("🛑 Бот остановлен")