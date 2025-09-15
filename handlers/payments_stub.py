# handlers/payments_stub.py
from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from config import PAYMENT_SHOP_ID
from db.users import get_user_by_chat_id
from logger import logger  # используем общий логгер проекта

router = Router()


class PaymentState(StatesGroup):
    waiting_for_amount = State()

@router.message(F.text == "💵 Оплатить услуги")
async def ask_amount(message: Message, state: FSMContext):
    """
    Пользователь нажал кнопку оплаты — спрашиваем сумму.
    """
    await state.set_state(PaymentState.waiting_for_amount)
    await message.answer("Введите сумму, которую хотите оплатить (в рублях, минимум 20):")


@router.message(PaymentState.waiting_for_amount)
async def process_amount(message: Message, state: FSMContext):
    """
    Обрабатываем сумму и формируем ссылку на оплату.
    """
    try:
        amount_rub = float(message.text.replace(",", "."))
        if amount_rub < 20:
            await message.answer("❌ Минимальная сумма оплаты — 20 рублей. Попробуйте снова:")
            return
    except ValueError:
        await message.answer("❌ Введите корректную сумму (например: 200 или 1500.50)")
        return
    
    # Переводим в копейки
    amount = int(amount_rub * 100)

    # Получаем договор пользователя
    user = await get_user_by_chat_id(message.chat.id)
    contract_title = user.get("contract_title") if user else "Не авторизованный пользователь"

    # Генерируем ссылку
    url = (
        f"https://payframe.ckassa.ru/"
        f"?service={PAYMENT_SHOP_ID}"
        f"&Л_СЧЕТ={contract_title}"
        f"&amount={amount}"
        f"&amount_read_only=false"
    )

    # Логируем событие
    logger.info(
        f"[PAYMENTS] Пользователь {message.from_user.full_name} (chat_id={message.chat.id}) "
        f"с договором '{contract_title}' запросил оплату на сумму {amount_rub:.2f} руб."
    )

    # Кнопка оплаты
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💳 Перейти к оплате", url=url)]
        ]
    )

    await message.answer(
        f"✅ Ссылка для оплаты сформирована на сумму {amount_rub:.2f} руб.\n"
        f"Нажмите кнопку ниже для перехода:",
        reply_markup=keyboard
    )

    await state.clear()
