import sys

with open("/root/security-scanner/bot/bot.py", "r") as f:
    content = f.read()

# 1. Add BroadcastStates after ScanStates
old_scan = """class ScanStates(StatesGroup):
    choosing_manufacturer = State()
    entering_model = State()
    choosing_user_level = State()"""

new_scan = old_scan + """


# FSM состояния для рассылки
class BroadcastStates(StatesGroup):
    waiting_text = State()
    confirming = State()"""

if old_scan not in content:
    print("ERROR: Could not find ScanStates block")
    sys.exit(1)
content = content.replace(old_scan, new_scan)

# 2. Replace the stub handler
old_stub = '@router.callback_query(F.data == "admin_broadcast")\nasync def cb_admin_broadcast(callback: CallbackQuery):\n    """Рассылка (заглушка)"""\n    if callback.from_user.id not in ADMIN_IDS:\n        await callback.answer("Нет доступа", show_alert=True)\n        return\n\n    await callback.answer("Функция рассылки в разработке", show_alert=True)'

if old_stub not in content:
    print("ERROR: Could not find broadcast stub")
    sys.exit(1)

new_broadcast = '''@router.callback_query(F.data == "admin_broadcast")
async def cb_admin_broadcast(callback: CallbackQuery, state: FSMContext):
    """Рассылка — начало"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Нет доступа", show_alert=True)
        return

    await callback.message.edit_text(
        "<b>Рассылка</b>\\n\\n"
        "Напишите текст сообщения.\\n"
        "Поддерживается HTML-разметка: <b>жирный</b>, <i>курсив</i>, <a href=\\"url\\">ссылки</a>.\\n\\n"
        "Для отмены нажмите кнопку ниже.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="< Отмена", callback_data="admin_panel")]
        ])
    )
    await state.set_state(BroadcastStates.waiting_text)
    await callback.answer()


@router.message(BroadcastStates.waiting_text)
async def on_broadcast_text(message: Message, state: FSMContext):
    """Рассылка — получен текст"""
    if message.from_user.id not in ADMIN_IDS:
        return

    text = message.text or message.caption or ""
    if not text:
        await message.answer("Пожалуйста, отправьте текстовое сообщение.")
        return

    await state.update_data(broadcast_text=text)

    # Count users
    from admin.broadcast import get_users_for_broadcast
    users = await get_users_for_broadcast()
    user_count = len(users)

    preview = (
        "<b>Превью рассылки:</b>\\n"
        "━━━━━━━━━━━━━━━\\n"
        + text + "\\n"
        "━━━━━━━━━━━━━━━\\n\\n"
        "Получателей: <b>" + str(user_count) + "</b>\\n\\n"
        "Отправить?"
    )

    await message.answer(
        preview,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="\\u2705 Отправить", callback_data="broadcast_confirm")],
            [InlineKeyboardButton(text="\\u270f\\ufe0f Изменить текст", callback_data="broadcast_edit")],
            [InlineKeyboardButton(text="\\u274c Отмена", callback_data="admin_panel")]
        ])
    )
    await state.set_state(BroadcastStates.confirming)


@router.callback_query(BroadcastStates.confirming, F.data == "broadcast_confirm")
async def on_broadcast_confirm(callback: CallbackQuery, state: FSMContext):
    """Рассылка — подтверждение и отправка"""
    if callback.from_user.id not in ADMIN_IDS:
        return

    data = await state.get_data()
    text = data.get("broadcast_text", "")
    await state.clear()

    if not text:
        await callback.message.edit_text("Ошибка: текст рассылки пуст.")
        await callback.answer()
        return

    await callback.message.edit_text("\\u23f3 Отправка рассылки...")
    await callback.answer()

    # Send broadcast
    from admin.broadcast import send_broadcast
    bot = callback.bot
    result = await send_broadcast(
        bot=bot,
        message=text,
        admin_id=callback.from_user.id
    )

    report = (
        "<b>\\u2705 Рассылка завершена</b>\\n\\n"
        "Отправлено: <b>" + str(result["sent"]) + "</b>\\n"
        "Ошибок: <b>" + str(result["failed"]) + "</b>\\n"
        "Всего получателей: <b>" + str(result["total"]) + "</b>"
    )

    await callback.message.edit_text(
        report,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="< Админ-панель", callback_data="admin_panel")]
        ])
    )


@router.callback_query(BroadcastStates.confirming, F.data == "broadcast_edit")
async def on_broadcast_edit(callback: CallbackQuery, state: FSMContext):
    """Рассылка — редактирование текста"""
    await callback.message.edit_text(
        "<b>Рассылка</b>\\n\\n"
        "Напишите новый текст сообщения.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="< Отмена", callback_data="admin_panel")]
        ])
    )
    await state.set_state(BroadcastStates.waiting_text)
    await callback.answer()'''

content = content.replace(old_stub, new_broadcast)

# 3. Update admin_panel handler to accept state and clear it
old_admin_panel = '@router.callback_query(F.data == "admin_panel")\nasync def cb_admin_panel(callback: CallbackQuery):\n    """Вернуться в админ-панель"""\n    if callback.from_user.id not in ADMIN_IDS:\n        await callback.answer("Нет доступа", show_alert=True)\n        return\n\n    await callback.message.edit_text(\n        "<b>Админ-панель Security Scanner</b>",\n        reply_markup=get_admin_keyboard()\n    )\n    await callback.answer()'

if old_admin_panel not in content:
    print("WARNING: Could not find admin_panel block - may already have state param")
else:
    new_admin_panel = '@router.callback_query(F.data == "admin_panel")\nasync def cb_admin_panel(callback: CallbackQuery, state: FSMContext):\n    """Вернуться в админ-панель"""\n    if callback.from_user.id not in ADMIN_IDS:\n        await callback.answer("Нет доступа", show_alert=True)\n        return\n\n    await state.clear()\n    await callback.message.edit_text(\n        "<b>Админ-панель Security Scanner</b>",\n        reply_markup=get_admin_keyboard()\n    )\n    await callback.answer()'
    content = content.replace(old_admin_panel, new_admin_panel)

with open("/root/security-scanner/bot/bot.py", "w") as f:
    f.write(content)

print("Patch applied successfully")
