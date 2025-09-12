from aiogram import Router
from aiogram.types import Message

from services.bgbilling import get_news
from logger import logger

router = Router()


@router.message(lambda msg: msg.text == "📰 Новости")
async def get_latest_news(message: Message):
    """
    Отправка последних новостей (3 шт.), даже если пользователь не авторизован
    """
    chat_id = message.chat.id

    try:
        data = await get_news()
        if data and "news" in data:
            news_list = data["news"][:3]  # последние 3 новости

            if not news_list:
                await message.answer("📰 Пока нет свежих новостей.")
                return

            text = "📰 Последние новости:\n\n"
            for item in news_list:
                # убираем html-теги
                title = item.get("title", "").replace("<br>", "\n")
                content = item.get("content", "").replace("<br>", "\n")
                text += f"📌 <b>{title}</b>\n{content}\n\n"

            await message.answer(text.strip())
        else:
            await message.answer("⚠️ Не удалось получить список новостей.")
    except Exception as e:
        logger.error(f"Ошибка при получении новостей chat_id={chat_id}: {e}")
        await message.answer("⚠️ Ошибка при получении новостей.")
