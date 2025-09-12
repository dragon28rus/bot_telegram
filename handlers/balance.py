# handlers/balance.py
from aiogram import Router, types, F

from db.users import get_user_by_chat_id
from bgbilling import get_contract_balance
from logger import logger
from handlers.start import main_menu

router = Router()


@router.message(F.text == "💰 Узнать баланс")
async def check_balance(message: types.Message):
    """
    Обработчик кнопки "Узнать баланс".
    Делает запрос в биллинг и возвращает баланс пользователя.
    """
    chat_id = message.chat.id
    user = await get_user_by_chat_id(chat_id)

    if not user:
        await message.answer(
            "❌ У вас нет привязанного договора.\n\n"
            "Для получения баланса сначала авторизуйтесь.",
            reply_markup=await main_menu(chat_id)
        )
        return

    contract_id = user["contract_id"]

    try:
        # Запрос к биллингу
        balance_info = await get_contract_balance(contract_id)

        # Ожидаем, что API возвращает {"balance": ..., "currency": ...}
        balance = balance_info.get("balance")
        currency = balance_info.get("currency", "₽")

        await message.answer(
            f"💰 Баланс по договору <b>{user['contract_title']}</b>: "
            f"<b>{balance} {currency}</b>",
            reply_markup=await main_menu(chat_id)
        )
        logger.info(f"Баланс успешно получен: chat_id={chat_id}, contract_id={contract_id}, balance={balance}")

    except Exception as e:
        await message.answer(
            "⚠ Ошибка при получении баланса. Попробуйте позже.",
            reply_markup=await main_menu(chat_id)
        )
        logger.error(f"Ошибка получения баланса chat_id={chat_id}, contract_id={contract_id}: {e}")
