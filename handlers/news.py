from aiogram import Router
from aiogram.types import Message

from services.bgbilling import get_news
from db.users import get_user_by_chat_id
from keyboards.main_menu import get_main_menu
from logger import logger

router = Router()


@router.message(lambda msg: msg.text == "📰 Новости")
async def get_latest_news(message: Message):
    """
    Отправка последних новостей (3 шт.) только для авторизованных пользователей
    """
    chat_id = message.chat.id
    user = await get_user_by_chat_id(chat_id)

    if not user or not user.get("contract_id"):
        await message.answer("❌ Для просмотра новостей необходимо авторизоваться.",
                             reply_markup=await get_main_menu(chat_id))
        return

    try:
        data = await get_news(user["contract_id"])
        if data and "news" in data:
            news_list = data["news"][:3]  # последние 3 новости

            if not news_list:
                await message.answer("📰 Пока нет свежих новостей.")
                return

            text = "📰 Последние новости:\n\n"
            for item in news_list:
                title = item.get("title", "").replace("<br>", "\n")
                content = item.get("content", "").replace("<br>", "\n")
                text += f"📌 <b>{title}</b>\n{content}\n\n"

            await message.answer(text.strip())
        else:
            await message.answer("⚠️ Не удалось получить список новостей.")
    except Exception as e:
        logger.error(f"Ошибка при получении новостей chat_id={chat_id}: {e}")
        await message.answer("⚠️ Ошибка при получении новостей.")
