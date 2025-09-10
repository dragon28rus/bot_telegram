#### handlers/support.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import SUPPORT_CHAT_ID
from logger import logger, set_chat_id
from db import is_user_authorized, get_contract_id_by_chat_id

router = Router()

class SupportStates(StatesGroup):
    waiting_for_support_message = State()

@router.message(Command("support"))
async def cmd_support(message: Message, state: FSMContext):
    set_chat_id(message.from_user.id)
    logger.info("Support command initiated")
    await message.answer("Опишите вашу проблему в ответном сообщении.")
    await state.set_state(SupportStates.waiting_for_support_message)

@router.message(SupportStates.waiting_for_support_message)
async def support_request(message: Message, state: FSMContext):
    set_chat_id(message.from_user.id)
    user_chat_id = message.from_user.id
    contract_id = get_contract_id_by_chat_id(user_chat_id)
    is_authorized = is_user_authorized(user_chat_id)
    
    # Отправляем нейтральное сообщение в группу техподдержки
    support_message = await message.bot.send_message(
        SUPPORT_CHAT_ID,
        "Новое обращение в техническую поддержку. Ответьте на это сообщение, чтобы отправить ответ пользователю."
    )
    
    # Сохраняем связь между сообщением в группе и пользователем
    # Предполагается, что db.py поддерживает функцию save_support_request
    from db import save_support_request
    save_support_request(user_chat_id, support_message.message_id)
    
    logger.info("Support request sent")
    await message.answer("Ваше обращение отправлено в техническую поддержку. Ожидайте ответа.")
    await state.clear()

@router.message(F.chat.id == SUPPORT_CHAT_ID, F.reply_to_message)
async def handle_support_reply(message: Message):
    set_chat_id('support')
    # Получаем message_id из ответа в группе
    reply_to_message_id = message.reply_to_message.message_id
    
    # Ищем chat_id пользователя, связанного с этим message_id
    from db import get_chat_id_by_support_message_id
    user_chat_id = get_chat_id_by_support_message_id(reply_to_message_id)
    
    if user_chat_id:
        set_chat_id(user_chat_id)
        try:
            await message.bot.send_message(user_chat_id, f"Ответ техподдержки: {message.text}")
            logger.info(f"Reply sent to user with chat_id: {user_chat_id}")
            await message.reply("Ответ успешно отправлен пользователю.")
        except Exception as e:
            logger.error(f"Error sending reply to user with chat_id {user_chat_id}: {e}")
            await message.reply("Ошибка при отправке ответа пользователю.")
    else:
        logger.warning("No user found for reply")
        await message.reply("Не удалось найти пользователя для ответа.")

@router.callback_query(F.data == "call_support")
async def call_support(callback: CallbackQuery):
    set_chat_id(callback.from_user.id)
    logger.info("Call support initiated")
    await callback.message.answer("Свяжитесь с технической поддержкой по телефону: +74162999900")
    await callback.answer()