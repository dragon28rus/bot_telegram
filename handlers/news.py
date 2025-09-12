# handlers/news.py
from aiogram import Router, types, F
import html2text

from services.bgbilling import authenticate
from logger import logger
from handlers.start import main_menu

router = Router()


@router.message(F.text == "📰 Новости")
async def show_news(message: types.Message):
    """
    Обработчик кнопки "Новости".
    Загружает последние 3 новости и выводит пользователю.
    """
    chat_id = message.chat.id

    try:
        # Получаем список новостей
        news_list = await get_news_list()

        if not news_list:
            await message.answer(
                "ℹ️ Новости отсутствуют.",
                reply_markup=await main_menu(chat_id)
            )
            return

        # Берём максимум 3 последних
        latest_news = news_list[:3]

        # HTML → текст
        h2t = html2text.HTML2Text()
        h2t.ignore_links = True
        h2t.ignore_images = True

        response = []
        for news in latest_news:
            title = news.get("title", "Без названия")
            text = news.get("text", "")
            clean_text = h2t.handle(text).strip()
            response.append(f"📰 <b>{title}</b>\n{clean_text}")

        await message.answer(
            "\n\n".join(response),
            reply_markup=await main_menu(chat_id)
        )
        logger.info(f"Новости отправлены пользователю chat_id={chat_id}")

    except Exception as e:
        await message.answer(
            "⚠ Ошибка при загрузке новостей. Попробуйте позже.",
            reply_markup=await main_menu(chat_id)
        )
        logger.error(f"Ошибка при получении новостей chat_id={chat_id}: {e}")
