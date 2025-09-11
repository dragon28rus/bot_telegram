# main.py
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiohttp import web

from config import BOT_TOKEN
from logger import logger
from handlers import admin
from webhooks.billing import handle_billing_notification, handle_broadcast_notification
from db.users import init_users_table


async def main():
    # --- инициализация базы данных ---
    await init_users_table()

    # --- настройка Telegram бота ---
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML")
    )

    # Удаляем webhook, иначе polling не запустится
    await bot.delete_webhook(drop_pending_updates=True)

    dp = Dispatcher()

    # --- подключаем роутеры ---
    dp.include_router(admin.router)
    # позже сюда добавим остальные: auth, balance, news и т.д.

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
        web._run_app(app, host="0.0.0.0", port=8080)  # можно вынести порт в .env
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("🛑 Бот остановлен")