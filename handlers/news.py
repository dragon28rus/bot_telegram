import logging
from aiogram import Router, F
from aiogram.types import Message
from db.users import get_user_by_chat_id
from services.bgbilling import get_news
from bs4 import BeautifulSoup
import html

router = Router()
logger = logging.getLogger(__name__)


def clean_html(raw_html: str) -> str:
    """
    Превращает HTML-текст новости в читаемый текст для Telegram.
    """
    if not raw_html:
        return ""

    # Декодируем HTML сущности (&nbsp; → пробел, &quot; → ")
    decoded = html.unescape(raw_html)

    # Парсим HTML
    soup = BeautifulSoup(decoded, "html.parser")

    # Извлекаем только текст с переводами строк
    text = soup.get_text(separator="\n", strip=True)

    # Чистим двойные переносы
    return "\n".join(line.strip() for line in text.splitlines() if line.strip())


@router.message(F.text == "📰 Новости")
async def cmd_news(message: Message):
    chat_id = str(message.chat.id)
    user = await get_user_by_chat_id(chat_id)

    if not user:
        await message.answer("Новости доступны только авторизованным пользователям.")
        return

    contract_id = user.get("contract_id")
    logger.debug(f"[get_news] Пользователь {chat_id}, contract_id={contract_id}")

    try:
        news_list = await get_news(contract_id)
        if not news_list:
            await message.answer("Новости не найдены.")
            return

        for news in news_list[:5]:  # ограничим, например, до 5 последних
            title = news.get("title", "Без названия")
            date = news.get("date", "")
            body = clean_html(news.get("body", ""))

            text = f"📰 <b>{title}</b>\n📅 {date}\n\n{body}"
            await message.answer(text, parse_mode="HTML")

    except Exception as e:
        logger.exception(f"[get_news] Ошибка при получении новостей для {chat_id}: {e}")
        await message.answer("❌ Не удалось получить новости. Попробуйте позже.")
