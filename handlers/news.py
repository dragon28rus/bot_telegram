# handlers/news.py
from aiogram import Router, F
from aiogram.types import Message
from db.users import get_user_by_chat_id
from services.bgbilling import get_news
from bs4 import BeautifulSoup
from logger import logger

router = Router()


def clean_html(raw_html: str) -> str:
    """
    Убирает HTML-теги и спецсимволы, делает текст читабельным.
    """
    soup = BeautifulSoup(raw_html, "html.parser")
    text = soup.get_text(separator="\n")  # перенос строк вместо склеивания
    return " ".join(text.split())  # убираем лишние пробелы


@router.message(F.text == "📰 Новости")
async def cmd_news(message: Message):
    chat_id = str(message.chat.id)
    user = await get_user_by_chat_id(chat_id)

    if not user or not user.get("contract_id"):
        await message.answer("Новости доступны только авторизованным пользователям.")
        return

    contract_id = user["contract_id"]

    try:
        news_data = await get_news(contract_id)

        if not news_data or "newsList" not in news_data:
            await message.answer("Новости не найдены.")
            return

        news_list = news_data["newsList"]

        # сортировка по дате (свежие первыми)
        news_list.sort(key=lambda n: n.get("date", ""), reverse=True)

        logger.debug(f"[cmd_news] Получено {len(news_list)} новостей, показываем первые 3")

        for news in news_list[:3]:
            title = news.get("title", "Без названия")
            date = news.get("date", "")
            body = clean_html(news.get("body", ""))

            text = f"📰 <b>{title}</b>\n📅 {date}\n\n{body}"
            await message.answer(text, parse_mode="HTML")

    except Exception as e:
        logger.error(f"[cmd_news] Ошибка при получении новостей: {e}")
        await message.answer("Ошибка при получении новостей.")
