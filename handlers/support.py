from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config import SUPPORT_CHAT_ID
from db import save_support_request, get_chat_id_by_support_message_id
from logger import logger, set_chat_id

router = Router()


# FSM состояния
class SupportStates(StatesGroup):
    waiting_for_message = State()


@router.message(F.text == "✉️ Техподдержка")
async def support_start(message: types.Message, state: FSMContext):
    """
    Пользователь выбрал 'Обратиться в техподдержку' → просим ввести описание.
    """
    chat_id = message.chat.id
    set_chat_id(str(chat_id))

    await state.set_state(SupportStates.waiting_for_message)
    await message.answer("Пожалуйста, опишите вашу проблему. Сообщение будет передано оператору.")
    logger.info("Пользователь начал обращение в техподдержку")


@router.message(SupportStates.waiting_for_message)
async def support_forward_to_operator(message: types.Message, state: FSMContext, bot):
    """
    Пользователь отправляет сообщение → пересылаем в чат техподдержки.
    """
    chat_id = message.chat.id
    set_chat_id(str(chat_id))

    try:
        # Пересылаем сообщение оператору
        sent_msg: Message = await bot.send_message(
            SUPPORT_CHAT_ID,
            f"Новое обращение от пользователя {chat_id}:\n\n{message.text}",
        )

        # Сохраняем связь (user_chat_id ↔ support_message_id)
        await save_support_request(str(chat_id), sent_msg.message_id)

        await message.answer("Ваше сообщение передано в техподдержку. Ожидайте ответа.")
        await state.clear()

        logger.info(f"Обращение передано в поддержку (message_id={sent_msg.message_id})")
    except Exception as e:
        logger.error(f"Ошибка при пересылке обращения: {e}")
        await message.answer("Не удалось передать сообщение в техподдержку. Попробуйте позже.")


@router.message(F.reply_to_message)
async def support_reply_from_operator(message: types.Message, bot):
    """
    Оператор отвечает в SUPPORT_CHAT_ID на пересланное сообщение.
    Ответ пересылается обратно пользователю.
    """
    if str(message.chat.id) != str(SUPPORT_CHAT_ID):
        return  # Игнорируем ответы не из чата поддержки

    reply_to_msg = message.reply_to_message
    if not reply_to_msg:
        return

    # Находим user_chat_id по message_id
    user_chat_id = await get_chat_id_by_support_message_id(reply_to_msg.message_id)
    if not user_chat_id:
        logger.warning("Ответ в саппорте не привязан к пользователю")
        return

    set_chat_id(user_chat_id)

    try:
        await bot.send_message(user_chat_id, f"Ответ от техподдержки:\n\n{message.text}")
        logger.info(f"Оператор ответил пользователю {user_chat_id}")
    except Exception as e:
        logger.error(f"Ошибка при отправке ответа пользователю {user_chat_id}: {e}")
