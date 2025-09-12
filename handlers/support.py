import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from db.users import get_user_by_chat_id
from db.support import save_support_request, link_admin_message, get_chat_id_by_support_message_id
from config import SUPPORT_CHAT_ID

router = Router()
logger = logging.getLogger(__name__)

class SupportStates(StatesGroup):
    waiting_for_message = State()


@router.message(Command("support"))
@router.message(F.text == "🆘 Техподдержка")
async def start_support(message: Message, state: FSMContext):
    await message.answer("Опишите вашу проблему, оператор свяжется с вами.")
    await state.set_state(SupportStates.waiting_for_message)


@router.message(SupportStates.waiting_for_message)
async def process_support_message(message: Message, state: FSMContext):
    chat_id = message.chat.id
    user = await get_user_by_chat_id(chat_id)
    contract_title = user.get("contract_title") if user else None

    # определяем тип сообщения
    if message.text:
        message_type = "text"
        content = message.text
    elif message.photo:
        message_type = "photo"
        content = f"Photo {message.photo[-1].file_id}"
    elif message.document:
        message_type = "document"
        content = f"Document {message.document.file_id}"
    else:
        message_type = "other"
        content = "Unsupported message"

    # сохраняем в БД
    support_message_id = message.message_id
    await save_support_request(message.chat.id, contract_title, support_message_id, content, message_type)

    # формируем текст для оператора
    operator_text = f"📩 Сообщение от пользователя {message.chat.id}\n"
    if contract_title:
        operator_text += f"Договор: {contract_title}\n"
    if message.text:
        operator_text += f"\n{message.text}"

    # пересылаем в чат поддержки
    if message.photo:
        sent = await message.bot.send_photo(SUPPORT_CHAT_ID, message.photo[-1].file_id, caption=operator_text)
    elif message.document:
        sent = await message.bot.send_document(SUPPORT_CHAT_ID, message.document.file_id, caption=operator_text)
    else:
        sent = await message.bot.send_message(SUPPORT_CHAT_ID, operator_text)

    # линкуем сообщения
    await link_admin_message(support_message_id, sent.message_id)

    # подтверждение пользователю
    await message.answer("✅ Ваше обращение принято. Оператор ответит в ближайшее время.")

    await state.clear()

'''
@router.message(F.reply_to_message, F.chat.id == SUPPORT_CHAT_ID)
async def process_operator_reply(message: Message):
    """Ответ от оператора приходит в reply на сообщение пользователя"""
    reply_to = message.reply_to_message.message_id
    chat_id = await get_chat_id_by_support_message_id(reply_to)
    if chat_id:
        if message.text:
            await message.bot.send_message(chat_id, f"💬 Ответ оператора:\n{message.text}")
        elif message.photo:
            await message.bot.send_photo(chat_id, message.photo[-1].file_id,
                                         caption=f"💬 Ответ оператора\n{message.caption or ''}")
        elif message.document:
            await message.bot.send_document(chat_id, message.document.file_id,
                                            caption=f"💬 Ответ оператора\n{message.caption or ''}")
'''

# --- Обработка ответа от оператора
@router.message(F.reply_to_message, F.chat.id == SUPPORT_CHAT_ID)
async def process_admin_reply(message: Message):
    reply_to_id = message.reply_to_message.message_id
    logging.debug(f"[support] Ответ оператора. reply_to_id={reply_to_id}, message_id={message.message_id}")

    user_chat_id = await get_chat_id_by_support_message_id(reply_to_id)
    if not user_chat_id:
        logging.warning(f"[support] Не найден chat_id по support_message_id={reply_to_id}")
        return

    try:
        text = f"✉️ Ответ от поддержки:\n{message.text or '[медиа]'}"
        await message.bot.send_message(chat_id=user_chat_id, text=text)
        logging.info(f"[support] Ответ доставлен пользователю chat_id={user_chat_id}")

        await link_admin_message(reply_to_id, message.message_id)
    except Exception as e:
        logging.error(f"[support] Ошибка при отправке ответа пользователю: {e}")

# --- абонент отвечает на сообщение оператора ---
@router.message(F.reply_to_message)
async def process_user_reply(message: Message):
    chat_id = message.chat.id

    # Проверим, что это ответ именно на сообщение бота (ответ поддержки)
    reply_id = message.reply_to_message.message_id
    logging.debug(f"[support] Абонент {chat_id} ответил на сообщение {reply_id}")

    # Найдём связанный support_message_id по admin_message_id
    from db.support import get_support_message_id_by_admin_message_id
    support_message_id = await get_support_message_id_by_admin_message_id(reply_id)

    if not support_message_id:
        logging.warning(f"[support] Не найден support_message_id для ответа абонента {chat_id}")
        return

    # Получим данные абонента
    user = await get_user_by_chat_id(chat_id)
    contract_title = user[2] if user and len(user) >= 3 and user[2] else "не авторизован"

    # Подготовим сообщение в техподдержку
    text = (
        f"📨 Ответ от абонента ({contract_title}):\n"
        f"{message.text or '[медиа]'}"
    )

    try:
        await message.bot.send_message(chat_id=SUPPORT_CHAT_ID, text=text,
                                       reply_to_message_id=support_message_id)
        logging.info(f"[support] Ответ абонента {chat_id} переслан оператору")
    except Exception as e:
        logging.error(f"[support] Ошибка при пересылке ответа абонента {chat_id}: {e}")