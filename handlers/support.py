from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from config import SUPPORT_CHAT_ID, ADMIN_CHAT_IDS
from db.support import save_support_request, get_chat_id_by_support_message_id
from logger import logger

router = Router()


# Состояния
class SupportStates(StatesGroup):
    waiting_for_message = State()


# Пользователь нажал кнопку "🆘 Техподдержка"
@router.message(F.text == "🆘 Техподдержка")
async def support_request_button(message: Message, state: FSMContext):
    logger.info(f"Пользователь {message.chat.id} нажал кнопку 🆘 Техподдержка")
    await message.answer("Опишите вашу проблему, оператор свяжется с вами.")
    await state.set_state(SupportStates.waiting_for_message)


# Пользователь ввёл команду /support
@router.message(Command("support"))
async def support_request_command(message: Message, state: FSMContext):
    logger.info(f"Пользователь {message.chat.id} вызвал команду /support")
    await message.answer("Опишите вашу проблему, оператор свяжется с вами.")
    await state.set_state(SupportStates.waiting_for_message)


# Обработка текста запроса пользователя
@router.message(SupportStates.waiting_for_message)
async def process_support_message(message: Message, state: FSMContext):
    chat_id = message.chat.id
    support_message = message.text

    # Сохраняем сообщение в БД
    support_message_id = await save_support_request(chat_id, support_message)

    logger.info(f"Сохранен запрос в техподдержку от {chat_id}, ID {support_message_id}")

    # Уведомляем пользователя
    await message.answer("Ваше обращение принято. Оператор ответит в ближайшее время.")

    # Уведомление админу
    sent = await message.bot.send_message(
        SUPPORT_CHAT_ID,
        f"📩 Новый запрос в поддержку (ID {support_message_id}) от {chat_id}:\n\n{support_message}\n\n"
        f"➡️ Ответьте на это сообщение, чтобы клиент получил ваш ответ."
    )

    # Привязываем message_id админа к support_message_id
    sent.conf["support_message_id"] = support_message_id

    await state.clear()


# Админ отвечает пользователю через /reply
@router.message(Command("reply"))
async def reply_to_user_command(message: Message):
    parts = message.text.split(maxsplit=2)

    if len(parts) < 3:
        await message.answer("❌ Формат команды: /reply <support_message_id> <текст ответа>")
        return

    support_message_id = parts[1]
    reply_text = parts[2]

    chat_id = await get_chat_id_by_support_message_id(support_message_id)

    if not chat_id:
        await message.answer("❌ Ошибка: не найдено обращение с таким ID.")
        return

    # Отправляем ответ пользователю
    await message.bot.send_message(chat_id, f"📩 Ответ от поддержки:\n\n{reply_text}")

    # Подтверждение админу
    await message.answer(f"✅ Ответ отправлен пользователю {chat_id}")
    logger.info(f"Админ {message.chat.id} ответил на запрос {support_message_id} пользователя {chat_id}")


# Админ отвечает через "reply" на сообщение бота
@router.message(F.reply_to_message)
async def reply_via_reply(message: Message):
    replied = message.reply_to_message
    if not replied or "ID" not in replied.text:
        return  # Это не ответ на сообщение бота с тикетом

    try:
        support_message_id = replied.text.split("ID")[1].split(")")[0].strip()
    except Exception:
        return

    reply_text = message.text
    chat_id = await get_chat_id_by_support_message_id(support_message_id)

    if not chat_id:
        await message.answer("❌ Ошибка: не найдено обращение с таким ID.")
        return

    # Отправляем ответ пользователю
    await message.bot.send_message(chat_id, f"📩 Ответ от поддержки:\n\n{reply_text}")

    # Подтверждение админу
    await message.answer(f"✅ Ответ отправлен пользователю {chat_id}")
    logger.info(f"Админ {message.chat.id} ответил (reply) на запрос {support_message_id} пользователя {chat_id}")
