# handlers/payments_stub.py
from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from services.bgbilling_custom import get_recommended_payment
from keyboards.main_menu import get_main_menu
from config import PAYMENT_SHOP_ID
from db.users import get_user_by_chat_id
from logger import logger

router = Router()

class PaymentState(StatesGroup):
    waiting_for_amount = State()

def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура с кнопкой отмены.
    """
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="⬅️ Вернуться в главное меню")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

@router.message(F.text == "💵 Оплатить услуги")
async def ask_amount(message: Message, state: FSMContext):
    """
    Пользователь нажал кнопку оплаты — спрашиваем сумму.
    """
    await state.set_state(PaymentState.waiting_for_amount)
    chat_id = message.chat.id
    user = await get_user_by_chat_id(chat_id)
    if not user or not user.get("contract_id"):
        await state.clear()
        await message.answer("❌ Сначала авторизуйтесь.", reply_markup=await get_main_menu(chat_id))
        return
    
    result = await get_recommended_payment(user["contract_id"])
    if result and result["success"]:
        total = result["recommend_payment"]
        await message.answer(
            f"Введите сумму, которую хотите оплатить (в рублях, минимум 20)\n"
            f"Рекомендуемая сумма: {total}",
            reply_markup=get_cancel_keyboard()
        )
    else:
        await message.answer(
            "Введите сумму, которую хотите оплатить (в рублях, минимум 20):",
            reply_markup=get_cancel_keyboard()
        )

@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    """
    Отмена операции оплаты.
    """
    user = await get_user_by_chat_id(callback.message.chat.id)
    contract_title = user.get("contract_title") if user else "Не авторизованный пользователь"

    logger.info(
        f"[PAYMENTS] Пользователь {callback.from_user.full_name} (chat_id={callback.message.chat.id}) "
        f"с договором '{contract_title}' отменил оплату."
    )

    await state.clear()

    # отвечаем на сам callback (чтобы Telegram не жаловался)
    await callback.answer("Возврат в меню")

    # редактируем сообщение с кнопками или шлём новое
    await callback.message.answer(
        "⬅️ Вы вернулись в главное меню.",
        reply_markup=await get_main_menu(callback.message.chat.id)
    )

@router.message(PaymentState.waiting_for_amount, F.text == "⬅️ Вернуться в главное меню")
async def cancel_payment_text(message: Message, state: FSMContext):
    user = await get_user_by_chat_id(message.chat.id)
    contract_title = user.get("contract_title") if user else "Не авторизованный пользователь"

    logger.info(
        f"[PAYMENTS] Пользователь {message.from_user.full_name} (chat_id={message.chat.id}) "
        f"с договором '{contract_title}' отменил оплату (reply-кнопка)."
    )

    await state.clear()
    await message.answer(
        "⬅️ Вы вернулись в главное меню.",
        reply_markup=await get_main_menu(message.chat.id)
    )

@router.message(PaymentState.waiting_for_amount, F.text.regexp(r"^\d+[.,]?\d*$"))
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
        f"с договором '{contract_title}' запросил оплату на сумму {amount_rub:.2f} руб. "
        f"(amount={amount} копеек)"
    )

    # Кнопка оплаты
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💳 Перейти к оплате", url=url)],
            [InlineKeyboardButton(text="⬅️ Вернуться в главное меню", callback_data="back_to_main")]
        ]
    )

    await message.answer(
        f"✅ Ссылка для оплаты сформирована на сумму {amount_rub:.2f} руб.\n"
        f"Нажмите кнопку ниже для перехода:",
        reply_markup=keyboard
    )

    await state.clear()

@router.message(PaymentState.waiting_for_amount)
async def invalid_amount(message: Message, state: FSMContext):
    """
    Ловим любые некорректные ответы в состоянии ожидания суммы.
    """
    await message.answer("❌ Введите корректную сумму (например: 200 или 1500.50) "
                         "или нажмите «⬅️ Вернуться в главное меню».")
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Вернуться в главное меню", callback_data="back_to_main")]
        ]
    )
    await message.answer(reply_markup=keyboard)