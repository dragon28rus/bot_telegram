from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from config import SUPPORT_CHAT_ID
from db.support import save_support_request, get_chat_id_by_support_message_id
from db.users import get_user_by_chat_id
from logger import logger

router = Router()


# Состояния
class SupportStates(StatesGroup):
    waiting_for_message = State()

# Обработка кнопки "Техподдержка"
@router.message(F.text == "Техподдержка")
async def support_button_handler(message: Message):
    chat_id = message.chat.id
    logger.debug(f"[support_button_handler] Пользователь {chat_id} нажал кнопку 'Техподдержка'")
    await message.answer(
        "🆘 Пожалуйста, опишите вашу проблему, и оператор техподдержки свяжется с вами."
    )

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

    # Сохраняем запрос в БД
    support_message_id = await save_support_request(chat_id, support_message)

    # Получаем договор, если есть
    user = await get_user_by_chat_id(str(chat_id))
    contract_info = ""
    if user and user.get("contract_title"):
        contract_info = f"\n📄 Договор: {user['contract_title']} (ID {user['contract_id']})"

    logger.info(f"Сохранен запрос в техподдержку от {chat_id}, ID {support_message_id}")

    # Уведомляем пользователя
    await message.answer("Ваше обращение принято. Оператор ответит в ближайшее время.")

    # Уведомление админу
    sent = await message.bot.send_message(
        SUPPORT_CHAT_ID,
        f"📩 Новый запрос в поддержку (ID {support_message_id}) от {chat_id}:\n\n{support_message}\n\n"
        f"➡️ Ответьте на это сообщение (Reply), чтобы клиент получил ваш ответ."
    )

    # Вместо sent.conf — сохраняем в БД связь admin_message_id → support_message_id
    from db.support import link_admin_message
    await link_admin_message(support_message_id, sent.message_id)

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
