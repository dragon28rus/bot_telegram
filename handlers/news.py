import re
from aiogram import Router
from aiogram.types import Message
from aiogram.enums.parse_mode import ParseMode

from services.bgbilling import get_news
from db.users import get_user_by_chat_id
from keyboards.main_menu import get_main_menu
from logger import logger

router = Router()


def clean_html(raw_html: str) -> str:
    """Удаляет HTML-теги из текста"""
    clean = re.sub(r"<.*?>", "", raw_html or "")
    return clean.strip()


def extract_images(raw_html: str) -> list[str]:
    """Извлекает ссылки на картинки из HTML"""
    return re.findall(r'<img[^>]+src="([^"]+)"', raw_html or "")


@router.message(lambda msg: msg.text == "📰 Новости")
async def get_latest_news(message: Message):
    """
    Отправка последних новостей (3 шт.) только для авторизованных пользователей
    """
    chat_id = message.chat.id
    user = await get_user_by_chat_id(chat_id)

    if not user or not user.get("contract_id"):
        await message.answer(
            "❌ Для просмотра новостей необходимо авторизоваться.",
            reply_markup=await get_main_menu(chat_id),
        )
        return

    try:
        data = await get_news(user["contract_id"])
        if data and "newsList" in data:
            news_list = data["newsList"][:3]  # последние 3 новости

            if not news_list:
                await message.answer("📰 Пока нет свежих новостей.")
                return

            for item in news_list:
                title = clean_html(item.get("title", ""))
                body = item.get("body", "")

                text = f"📌 <b>{title}</b>\n{clean_html(body)}"
                await message.answer(text.strip(), parse_mode=ParseMode.HTML)

                # Отправка картинок, если есть
                images = extract_images(body)
                for img_url in images:
                    await message.answer_photo(img_url)

        else:
            await message.answer("⚠️ Не удалось получить список новостей.")
    except Exception as e:
        logger.error(f"Ошибка при получении новостей chat_id={chat_id}: {e}")
        await message.answer("⚠️ Ошибка при получении новостей.")
