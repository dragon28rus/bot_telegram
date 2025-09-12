@router.message(F.text == "📊 Текущий тариф")
async def get_user_tariff(message: Message):
    chat_id = message.chat.id
    user = await get_user_by_chat_id(chat_id)

    if not user or not user.get("contract_id"):
        await message.answer("❌ Сначала авторизуйтесь.", reply_markup=await get_main_menu(chat_id))
        return

    try:
        plan = await get_tariff_plan(user["contract_id"])
        if plan:
            text = f"📊 Ваш тарифный план: <b>{plan['title']}</b>\n"
            text += f"📅 С {plan['dateFrom']}"
            if plan["dateTo"]:
                text += f" по {plan['dateTo']}"
            await message.answer(text)
        else:
            await message.answer("⚠️ Не удалось получить тарифный план.")
    except Exception as e:
        logger.error(f"Ошибка получения тарифа chat_id={chat_id}: {e}")
        await message.answer("⚠️ Ошибка при получении тарифа.")
