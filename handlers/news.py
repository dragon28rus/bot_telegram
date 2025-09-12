# handlers/news.py
from aiogram import Router, types, F
import html2text

from services.bgbilling import get_news
from db.users import get_user_by_chat_id
from logger import logger
from handlers.start import main_menu

router = Router()


@router.message(F.text == "📰 Новости")
async def show_news(message: types.Message):
    chat_id = message.chat.id

    user = await get_user_by_chat_id(chat_id)
    if not user:
        await message.answer(
            "❌ Новости доступны только для авторизованных пользователей.\n"
            "Пожалуйста, авторизуйтесь.",
            reply_markup=await main_menu(chat_id)
        )
        return

    contract_id = user["contract_id"]

    try:
        news_data = await get_news(contract_id)

        if not news_data or not isinstance(news_data, list):
            await message.answer("ℹ️ Новости отсутствуют.", reply_markup=await main_menu(chat_id))
            return

        latest_news = news_data[:3]

        h2t = html2text.HTML2Text()
        h2t.ignore_links = True
        h2t.ignore_images = True

        response = []
        for news in latest_news:
            title = news.get("title", "Без названия")
            text = news.get("text", "")
            clean_text = h2t.handle(text).strip()
            response.append(f"📰 <b>{title}</b>\n{clean_text}")

        await message.answer("\n\n".join(response), reply_markup=await main_menu(chat_id))
        logger.info(f"Новости отправлены chat_id={chat_id}, contract_id={contract_id}")

    except Exception as e:
        await message.answer("⚠ Ошибка при загрузке новостей. Попробуйте позже.", reply_markup=await main_menu(chat_id))
        logger.error(f"Ошибка при получении новостей chat_id={chat_id}, contract_id={contract_id}: {e}")
