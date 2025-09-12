# handlers/news.py
from aiogram import Router, F
from aiogram.types import Message
from db.users import get_user_by_chat_id
from services.bgbilling import get_news
from bs4 import BeautifulSoup

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

        for news in news_data["newsList"][:5]:  # ограничим до 5 последних
            title = news.get("title", "Без названия")
            date = news.get("date", "")
            body = clean_html(news.get("body", ""))

            text = f"📰 <b>{title}</b>\n📅 {date}\n\n{body}"
            await message.answer(text, parse_mode="HTML")

    except Exception as e:
        await message.answer("Ошибка при получении новостей.")
        raise e
