from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import SUPPORT_CHAT_ID
from logger import logger, set_chat_id
from db import save_support_request, get_chat_id_by_support_message_id

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

    try:
        # Отправляем в чат поддержки текст или пересылаем медиа
        if message.text:
            support_message = await message.bot.send_message(
                SUPPORT_CHAT_ID,
                f"Новое обращение от пользователя {user_chat_id}:\n{message.text}",
            )
        else:
            support_message = await message.forward(SUPPORT_CHAT_ID)

        # Сохраняем связь между сообщением в группе и пользователем
        await save_support_request(user_chat_id, support_message.message_id)

        logger.info("Support request sent")
        await message.answer("Ваше обращение отправлено в техническую поддержку. Ожидайте ответа.")
    except Exception as e:
        logger.error(f"Error sending support request: {e}")
        await message.answer("Ошибка при отправке обращения в поддержку. Попробуйте позже.")
    finally:
        await state.clear()


@router.message(F.chat.id == SUPPORT_CHAT_ID, F.reply_to_message)
async def handle_support_reply(message: Message):
    set_chat_id("support")

    reply_to_message_id = message.reply_to_message.message_id
    user_chat_id = await get_chat_id_by_support_message_id(reply_to_message_id)

    if user_chat_id:
        set_chat_id(user_chat_id)
        try:
            if message.text:
                await message.bot.send_message(user_chat_id, f"Ответ техподдержки: {message.text}")
            elif message.caption or message.photo or message.document:
                await message.copy_to(user_chat_id)

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
