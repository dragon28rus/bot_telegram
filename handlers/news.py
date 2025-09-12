from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from db.users import get_user_by_chat_id
from services.bgbilling import get_news
from logger import logger
from services.utils import clean_html  # функция очистки HTML

router = Router()

@router.message(Command("news"))
@router.message(F.text == "📰 Новости")
async def cmd_news(message: Message):
    chat_id = str(message.chat.id)
    logger.info(f"Пользователь {chat_id} запросил новости")

    user = await get_user_by_chat_id(chat_id)
    if not user or not user.get("contract_id"):  # проверка, есть ли договор
        await message.answer("❌ Новости доступны только авторизованным пользователям.")
        return

    try:
        news_data = await get_news(user.get("contract_id"))
        if not news_data or "newsList" not in news_data:
            await message.answer("⚠️ Не удалось получить новости. Попробуйте позже.")
            return

        news_list = news_data["newsList"]

        # сортируем все новости по дате (от старых к новым)
        news_list.sort(key=lambda n: n.get("date", ""))

        # берём последние 3
        latest_news = news_list[-3:]

        # сортируем их в обратном порядке (новейшие первыми)
        latest_news.sort(key=lambda n: n.get("date", ""), reverse=True)

        logger.debug(f"[cmd_news] Получено {len(news_list)} новостей, показываем последние {len(latest_news)}")

        for news in latest_news:
            title = news.get("title", "Без названия")
            date = news.get("date", "")
            body = clean_html(news.get("body", ""))

            text = f"📰 <b>{title}</b>\n📅 {date}\n\n{body}"
            await message.answer(text, parse_mode="HTML")

    except Exception as e:
        logger.error(f"[get_news] Ошибка при получении новостей для {chat_id}: {e}")
        await message.answer("⚠️ Произошла ошибка при получении новостей.")
