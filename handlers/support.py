from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from db.users import get_user_by_chat_id
from db.support import save_support_request, link_admin_message, get_chat_id_by_support_message_id
from config import SUPPORT_CHAT_ID
from logger import logger

router = Router()

# --- FSM состояния ---
class SupportState(StatesGroup):
    chatting = State()

# --- Клавиатуры ---
main_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="❌ Выйти из техподдержки")]],
    resize_keyboard=True
)

# --- Вход в поддержку ---
@router.message(F.text == "🆘 Техподдержка")
@router.message(Command("support"))
async def enter_support(message: types.Message, state: FSMContext):
    """
    Переводим пользователя в режим общения с техподдержкой.
    """
    await state.set_state(SupportState.chatting)
    await message.answer(
        "Вы вошли в режим общения с техподдержкой.\n"
        "Опишите вашу проблему. Все сообщения будут пересланы оператору.",
        reply_markup=main_kb
    )
    logger.info(f"[support] Пользователь {message.chat.id} вошёл в режим поддержки")

# --- Выход из поддержки ---
@router.message(F.text == "❌ Выйти из техподдержки", SupportState.chatting)
async def exit_support(message: types.Message, state: FSMContext):
    """
    Выход из режима общения с поддержкой.
    """
    await state.clear()
    await message.answer(
        "Вы вышли из режима общения с техподдержкой.",
        reply_markup=types.ReplyKeyboardRemove()
    )
    logger.info(f"[support] Пользователь {message.chat.id} вышел из режима поддержки")

# --- Пересылка сообщений пользователя в поддержку ---
@router.message(SupportState.chatting)
async def forward_to_support(message: types.Message):
    """
    Все сообщения в состоянии chatting пересылаем в чат поддержки.
    """
    user = await get_user_by_chat_id(message.chat.id)
    contract_title = user["contract_title"] if user and user.get("contract_title") else "Не авторизован"

    # Формируем подпись для оператора
    caption = f"📩 Сообщение от абонента\nID: {message.chat.id}\nДоговор: {contract_title}"

    # Пересылаем сообщение
    if message.text:
        sent = await message.bot.send_message(
            SUPPORT_CHAT_ID,
            f"{caption}\n\n{message.text}"
        )
    elif message.photo:
        sent = await message.bot.send_photo(
            SUPPORT_CHAT_ID,
            message.photo[-1].file_id,
            caption=caption
        )
    elif message.document:
        sent = await message.bot.send_document(
            SUPPORT_CHAT_ID,
            message.document.file_id,
            caption=caption
        )
    else:
        sent = await message.forward(SUPPORT_CHAT_ID)

    # Сохраняем в БД
    await save_support_request(
        support_message_id=message.message_id,
        chat_id=message.chat.id,
        contract_title=contract_title,
        message=message.text or message.caption or "<медиа>"
    )
    await link_admin_message(message.message_id, sent.message_id)

    await message.answer("✅ Ваше обращение отправлено оператору.")
    logger.info(f"[support] Сообщение от {message.chat.id} переслано в поддержку")

# --- Ответ оператора пользователю ---
@router.message(F.chat.id == SUPPORT_CHAT_ID)
async def operator_reply(message: types.Message):
    """
    Если оператор отвечает reply на сообщение абонента —
    пересылаем его обратно пользователю с цитированием.
    """
    if not message.reply_to_message:
        return  # игнорируем сообщения без reply

    try:
        from db.support import get_chat_id_by_support_message_id
        # Берём support_message_id исходного пользователя
        support_message_id = message.reply_to_message.message_id
        chat_id = await get_chat_id_by_support_message_id(support_message_id)

        if not chat_id:
            logger.error(f"[support] Не найден пользователь для support_message_id={support_message_id}")
            return

        # Отправляем пользователю с цитированием
        if message.text:
            await message.bot.send_message(
                chat_id,
                message.text,
                reply_to_message_id=support_message_id
            )
        elif message.photo:
            await message.bot.send_photo(
                chat_id,
                message.photo[-1].file_id,
                caption=message.caption or "",
                reply_to_message_id=support_message_id
            )
        elif message.document:
            await message.bot.send_document(
                chat_id,
                message.document.file_id,
                caption=message.caption or "",
                reply_to_message_id=support_message_id
            )
        else:
            # fallback на пересылку
            await message.bot.copy_message(
                chat_id,
                from_chat_id=SUPPORT_CHAT_ID,
                message_id=message.message_id,
                reply_to_message_id=support_message_id
            )

        logger.info(f"[support] Оператор ответил пользователю {chat_id} с цитированием")

    except Exception as e:
        logger.exception(f"[support] Ошибка при отправке ответа пользователю: {e}")