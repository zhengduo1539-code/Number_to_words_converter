from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from urllib.parse import urlparse

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError, TelegramRetryAfter
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from app.config import Settings
from app.db.models import AdminButton, Broadcast, WelcomeButton
from app.db.repository import (
    create_broadcast,
    find_recipients,
    get_admin_button,
    get_setting,
    get_welcome_button,
    increment_conversion,
    initialize_defaults,
    list_admin_buttons,
    list_users,
    list_welcome_buttons,
    mark_blocked,
    reset_admin_buttons,
    reset_language_messages,
    reset_welcome_buttons,
    reset_welcome_message,
    set_setting,
    stats,
    update_broadcast,
)
from app.keyboards.admin import admin_menu_markup, broadcast_markup, stats_markup, users_markup
from app.keyboards.buttons import admin_markup, compatible_button, welcome_markup
from app.keyboards.customization import (
    action_type_markup,
    admin_buttons_markup,
    cancel_markup,
    customization_markup,
    language_messages_markup,
    reset_all_markup,
    style_markup,
    welcome_buttons_markup,
    welcome_message_markup,
)
from app.services.emoji_service import (
    deserialize_entities,
    first_custom_emoji_id,
    first_visible_fallback,
    localize_custom_emoji_entities,
    remove_custom_emoji_text,
    serialize_entities,
)
from app.services.i18n import (
    without_default_language_decoration,
    without_default_welcome_decoration,
)
from app.states.workflows import (
    AdminButtonStates,
    BroadcastStates,
    LanguageMessageStates,
    WelcomeButtonStates,
    WelcomeMessageStates,
)
from app.utils.formatting import user_label
from app.utils.pagination import page_count
from app.utils.security import is_admin, require_admin_callback

logger = logging.getLogger(__name__)
router = Router(name="admin")
PAGE_SIZE = 5


def unauthorized_message() -> str:
    return "Unauthorized."


@router.message(Command("admin"))
async def admin_command(message: Message, settings: Settings, session) -> None:
    if not is_admin(message.from_user, settings):
        await message.answer(unauthorized_message())
        return
    await initialize_defaults(session)
    await message.answer("🛠 Admin Control Panel", reply_markup=await build_admin_markup(session))


@router.message(Command("ctm"))
async def customization_command(message: Message, settings: Settings, session) -> None:
    if not is_admin(message.from_user, settings):
        await message.answer(unauthorized_message())
        return
    await initialize_defaults(session)
    await message.answer("⚙️ Customization Center", reply_markup=customization_markup())


async def build_admin_markup(session):
    buttons = await list_admin_buttons(session)
    return admin_markup(buttons) if buttons else admin_menu_markup()


async def edit_or_answer(callback: CallbackQuery, text: str, markup=None) -> None:
    try:
        await callback.message.edit_text(text, reply_markup=markup)
    except TelegramBadRequest:
        await callback.message.answer(text, reply_markup=markup)


async def show_stats(callback: CallbackQuery, session) -> None:
    data = await stats(session)
    text = (
        "📊 Bot Statistics\n\n"
        f"Total users: {data['total_users']}\n"
        f"Active today: {data['active_today']}\n"
        f"Active in 7 days: {data['active_7_days']}\n"
        f"Active in 30 days: {data['active_30_days']}\n"
        f"Total conversions: {data['total_conversions']}\n"
        f"Users started: {data['started_users']}\n"
        f"Blocked/inactive: {data['blocked_users']}"
    )
    await edit_or_answer(callback, text, stats_markup())


async def show_users(callback: CallbackQuery, session, page: int = 0) -> None:
    rows, total = await list_users(session, page, PAGE_SIZE)
    pages = page_count(total, PAGE_SIZE)
    text = "👥 <b>Users</b>\n\n"
    text += "\n\n".join(user_label(item) for item in rows) or "No users yet."
    await edit_or_answer(callback, text, users_markup(page, pages))


@router.callback_query(F.data.startswith("admin:"))
async def admin_callbacks(callback: CallbackQuery, settings: Settings, session, state: FSMContext) -> None:
    if not await require_admin_callback(callback, settings):
        return
    await callback.answer()
    parts = callback.data.split(":")
    action = parts[1]
    if action == "stats":
        await show_stats(callback, session)
    elif action == "users":
        await show_users(callback, session, int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0)
    elif action == "broadcast":
        await edit_or_answer(callback, "📣 Choose a broadcast target:", broadcast_markup())
    elif action == "customize":
        await edit_or_answer(callback, "⚙️ Customization Center", customization_markup())
    elif action == "back":
        await state.clear()
        await edit_or_answer(callback, "🛠 Admin Control Panel", await build_admin_markup(session))
    elif action == "close":
        await state.clear()
        await edit_or_answer(callback, "Admin panel closed.")


@router.callback_query(F.data == "noop")
async def noop(callback: CallbackQuery) -> None:
    await callback.answer()


@router.callback_query(F.data.startswith("ctm:"))
async def customization_callbacks(callback: CallbackQuery, settings: Settings, session, state: FSMContext, bot) -> None:
    if not await require_admin_callback(callback, settings):
        return
    await callback.answer()
    parts = callback.data.split(":")
    action = parts[1]
    if action == "home":
        await state.clear()
        await edit_or_answer(callback, "⚙️ Customization Center", customization_markup())
    elif action == "cancel":
        await state.clear()
        await edit_or_answer(callback, "⚙️ Customization Center", customization_markup())
    elif action == "welcome":
        text = await get_setting(session, "welcome_text")
        await edit_or_answer(callback, f"📝 Current welcome message:\n\n{text}", welcome_message_markup())
    elif action == "welcome_edit":
        await state.set_state(WelcomeMessageStates.waiting_text)
        await edit_or_answer(callback, "Send the new welcome message now. Telegram formatting and custom emoji are preserved.", cancel_markup())
    elif action == "welcome_reset":
        await reset_welcome_message(session)
        await edit_or_answer(callback, "Welcome message reset to default.", welcome_message_markup())
    elif action == "language_messages":
        menu_status = "Customized" if await get_setting(session, "language_menu_text") else "Default"
        changed_status = "Customized" if await get_setting(session, "language_changed_text") else "Default"
        await edit_or_answer(
            callback,
            f"🌐 Language Messages\n\nChoose your language: {menu_status}\nLanguage changed: {changed_status}",
            language_messages_markup(),
        )
    elif action == "language_menu_edit":
        await state.set_state(LanguageMessageStates.waiting_menu)
        await edit_or_answer(
            callback,
            "Send the custom “Choose your language” message. Add as many animated emojis as needed; language text will still be localized.",
            cancel_markup(),
        )
    elif action == "language_menu_reset":
        await set_setting(session, "language_menu_text", "")
        await set_setting(session, "language_menu_entities", "[]")
        await edit_or_answer(callback, "Choose-your-language message reset to default.", language_messages_markup())
    elif action == "language_changed_edit":
        await state.set_state(LanguageMessageStates.waiting_changed)
        await edit_or_answer(
            callback,
            "Send the custom “Language changed” message. Add as many animated emojis as needed; language text will still be localized.",
            cancel_markup(),
        )
    elif action == "language_changed_reset":
        await set_setting(session, "language_changed_text", "")
        await set_setting(session, "language_changed_entities", "[]")
        await edit_or_answer(callback, "Language-changed message reset to default.", language_messages_markup())
    elif action == "welcome_buttons":
        await edit_or_answer(callback, "🔘 Welcome Buttons", welcome_buttons_markup(await list_welcome_buttons(session)))
    elif action == "wb_add":
        await state.clear()
        await state.update_data(button_id=None, button_type=None)
        await state.set_state(WelcomeButtonStates.waiting_label)
        await edit_or_answer(callback, "Send the button label. You can include a normal emoji; a custom emoji can be sent in the next step.", cancel_markup())
    elif action == "wb_edit":
        button = await get_welcome_button(session, int(parts[2]))
        if not button:
            await edit_or_answer(callback, "Button not found.", welcome_buttons_markup(await list_welcome_buttons(session)))
            return
        await state.clear()
        await state.update_data(button_id=button.id, button_type=button.button_type)
        await state.set_state(WelcomeButtonStates.waiting_label)
        await edit_or_answer(callback, f"Send the new label for “{button.label}”.", cancel_markup())
    elif action == "wb_remove":
        button = await get_welcome_button(session, int(parts[2]))
        if button:
            await session.delete(button)
            await session.commit()
        await edit_or_answer(callback, "Button removed.", welcome_buttons_markup(await list_welcome_buttons(session)))
    elif action == "wb_reset":
        await reset_welcome_buttons(session)
        await edit_or_answer(callback, "Welcome buttons reset to defaults.", welcome_buttons_markup(await list_welcome_buttons(session)))
    elif action == "wb_type":
        button_type = parts[2]
        await state.update_data(button_type=button_type)
        if button_type == "share":
            await state.set_state(WelcomeButtonStates.waiting_icon)
            await edit_or_answer(
                callback,
                "Optionally send one custom emoji now. The ID is detected automatically. Or send /skip.",
                cancel_markup(),
            )
        else:
            await state.set_state(WelcomeButtonStates.waiting_target)
            await edit_or_answer(callback, "Send the URL or callback action now.", cancel_markup())
    elif action == "wb" and len(parts) >= 4 and parts[2] == "style":
        await save_welcome_button_style(callback, session, state, parts[3])
    elif action == "wb_style":
        await save_welcome_button_style(callback, session, state, parts[2])
    elif action == "ab_edit":
        item = await get_admin_button(session, parts[2])
        if not item:
            await edit_or_answer(callback, "Admin button not found.", admin_buttons_markup(await list_admin_buttons(session)))
            return
        await state.clear()
        await state.update_data(admin_action=item.action)
        await state.set_state(AdminButtonStates.waiting_label)
        await edit_or_answer(callback, f"Send the new label for “{item.label}”.")
    elif action == "ab" and len(parts) >= 4 and parts[2] == "style":
        await save_admin_button_style(callback, session, state, parts[3])
    elif action == "ab_style":
        await save_admin_button_style(callback, session, state, parts[2])
    elif action == "ab_reset":
        await reset_admin_buttons(session)
        await edit_or_answer(callback, "Admin panel buttons reset.", admin_buttons_markup(await list_admin_buttons(session)))
    elif action == "reset_all":
        await edit_or_answer(callback, "⚠️ Reset all customizations? User data and conversion statistics will remain untouched.", reset_all_markup())
    elif action == "reset_confirm":
        await reset_welcome_message(session)
        await reset_language_messages(session)
        await reset_welcome_buttons(session)
        await reset_admin_buttons(session)
        await edit_or_answer(callback, "All customizations reset to defaults.", customization_markup())


async def save_welcome_button_style(callback, session, state, style: str) -> None:
    data = await state.get_data()
    button_type = data.get("button_type", "url")
    if style == "skip":
        style = "primary"
    button = await get_welcome_button(session, data.get("button_id")) if data.get("button_id") else None
    if button is None:
        button = WelcomeButton(label=data["label"], button_type=button_type, sort_order=0)
    else:
        button.button_type = button_type
    button.style = style
    button.url = data.get("target") if button_type == "url" else None
    button.callback_action = data.get("target") if button_type == "callback" else None
    button.icon_custom_emoji_id = data.get("icon_id")
    button.fallback_emoji = data.get("fallback_emoji")
    session.add(button)
    await session.commit()
    await state.clear()
    await edit_or_answer(callback, "Welcome button saved and previewed below.", welcome_buttons_markup(await list_welcome_buttons(session)))


async def save_admin_button_style(callback, session, state, style: str) -> None:
    data = await state.get_data()
    item = await get_admin_button(session, data["admin_action"])
    if item:
        item.label = data.get("label", item.label)
        item.style = "primary" if style == "skip" else style
        item.icon_custom_emoji_id = data.get("icon_id")
        item.fallback_emoji = data.get("fallback_emoji")
        await session.commit()
    await state.clear()
    await edit_or_answer(callback, "Admin button saved. Preview:", admin_buttons_markup(await list_admin_buttons(session)))


@router.message(WelcomeMessageStates.waiting_text)
async def save_welcome_message(message: Message, state: FSMContext, session) -> None:
    if not message.text:
        await message.answer("Please send a text message, or press Cancel.", reply_markup=cancel_markup())
        return
    await set_setting(session, "welcome_text", message.text)
    await set_setting(session, "welcome_entities", serialize_entities(message.entities))
    await state.clear()
    await message.answer("Welcome message saved. Preview:", reply_markup=welcome_markup(await list_welcome_buttons(session), (await message.bot.get_me()).username))
    preview_text = without_default_welcome_decoration(
        remove_custom_emoji_text(message.text, message.entities)
    )
    preview_entities = message.entities or []
    if any(entity.type == "custom_emoji" and entity.custom_emoji_id for entity in preview_entities):
        preview_text, preview_entities = localize_custom_emoji_entities(
            message.text,
            preview_entities,
            preview_text,
        )
    await message.answer(preview_text, entities=preview_entities or None)


async def save_language_message(message: Message, state: FSMContext, session, key: str, entity_key: str, label: str) -> None:
    if not message.text:
        await message.answer("Please send a text message, or press Cancel.", reply_markup=cancel_markup())
        return
    await set_setting(session, key, message.text)
    await set_setting(session, entity_key, serialize_entities(message.entities))
    await state.clear()
    await message.answer(f"{label} saved.", reply_markup=language_messages_markup())
    preview_text = without_default_language_decoration(
        "language_menu" if key == "language_menu_text" else "language_changed",
        message.text,
    )
    preview_entities = message.entities or []
    if any(entity.type == "custom_emoji" and entity.custom_emoji_id for entity in preview_entities):
        preview_text, preview_entities = localize_custom_emoji_entities(
            message.text,
            preview_entities,
            preview_text,
        )
    await message.answer(preview_text, entities=preview_entities or None)


@router.message(LanguageMessageStates.waiting_menu)
async def save_language_menu_message(message: Message, state: FSMContext, session) -> None:
    await save_language_message(
        message,
        state,
        session,
        "language_menu_text",
        "language_menu_entities",
        "Choose-your-language message",
    )


@router.message(LanguageMessageStates.waiting_changed)
async def save_language_changed_message(message: Message, state: FSMContext, session) -> None:
    await save_language_message(
        message,
        state,
        session,
        "language_changed_text",
        "language_changed_entities",
        "Language-changed message",
    )


@router.message(WelcomeButtonStates.waiting_label)
async def welcome_button_label(message: Message, state: FSMContext) -> None:
    if not message.text:
        await message.answer("Send a text label, or press Cancel.", reply_markup=cancel_markup())
        return
    await state.update_data(label=message.text, fallback_emoji=first_visible_fallback(message.text, message.entities))
    await state.set_state(WelcomeButtonStates.waiting_action)
    await message.answer("Choose the button type.", reply_markup=action_type_markup())


@router.message(WelcomeButtonStates.waiting_target)
async def welcome_button_target(message: Message, state: FSMContext) -> None:
    if not message.text:
        await message.answer("Send a URL or callback action, or press Cancel.", reply_markup=cancel_markup())
        return
    data = await state.get_data()
    button_type = data.get("button_type", "url")
    if button_type == "url":
        parsed = urlparse(message.text.strip())
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            await message.answer("Please send a valid http(s) URL.", reply_markup=cancel_markup())
            return
    await state.update_data(target=message.text.strip())
    await state.set_state(WelcomeButtonStates.waiting_icon)
    await message.answer("Optionally send one custom emoji now. The ID is detected automatically. Or send /skip.", reply_markup=cancel_markup())


@router.message(WelcomeButtonStates.waiting_icon)
async def welcome_button_icon(message: Message, state: FSMContext) -> None:
    if message.text == "/skip":
        await state.update_data(icon_id=None)
    else:
        await state.update_data(icon_id=first_custom_emoji_id(message.entities), fallback_emoji=first_visible_fallback(message.text or "", message.entities))
    await state.set_state(WelcomeButtonStates.waiting_style)
    await message.answer("Choose a button style.", reply_markup=style_markup("ctm:wb"))


@router.message(AdminButtonStates.waiting_label)
async def admin_button_label(message: Message, state: FSMContext) -> None:
    if not message.text:
        await message.answer("Send a text label, or press Cancel.", reply_markup=cancel_markup())
        return
    await state.update_data(label=message.text, fallback_emoji=first_visible_fallback(message.text, message.entities))
    await state.set_state(AdminButtonStates.waiting_icon)
    await message.answer("Optionally send one custom emoji, or send /skip.", reply_markup=cancel_markup())


@router.message(AdminButtonStates.waiting_icon)
async def admin_button_icon(message: Message, state: FSMContext, session) -> None:
    if message.text == "/skip":
        await state.update_data(icon_id=None)
    else:
        await state.update_data(icon_id=first_custom_emoji_id(message.entities), fallback_emoji=first_visible_fallback(message.text or "", message.entities))
    await state.set_state(AdminButtonStates.waiting_style)
    await message.answer("Choose a button style.", reply_markup=style_markup("ctm:ab"))


@router.callback_query(F.data.in_({"broadcast:all", "broadcast:one"}))
async def broadcast_callbacks(callback: CallbackQuery, settings: Settings, state: FSMContext) -> None:
    if not await require_admin_callback(callback, settings):
        return
    await callback.answer()
    target = callback.data.split(":")[1]
    await state.clear()
    await state.update_data(target_type=target)
    await state.set_state(BroadcastStates.waiting_target if target == "one" else BroadcastStates.waiting_message)
    prompt = "Send the recipient Telegram numeric ID." if target == "one" else "Send the broadcast message now."
    await edit_or_answer(callback, prompt)


@router.message(BroadcastStates.waiting_target)
async def broadcast_target(message: Message, state: FSMContext) -> None:
    if not message.text or not message.text.strip().isdigit():
        await message.answer("Send a numeric Telegram user ID.")
        return
    await state.update_data(target_user_id=int(message.text.strip()))
    await state.set_state(BroadcastStates.waiting_message)
    await message.answer("Send the message to broadcast.")


@router.message(BroadcastStates.waiting_message)
async def broadcast_message(message: Message, state: FSMContext) -> None:
    if not message.text:
        await message.answer("Only text broadcasts are supported in this workflow.")
        return
    await state.update_data(message_text=message.text, message_entities=serialize_entities(message.entities))
    await state.set_state(BroadcastStates.waiting_confirmation)
    await message.answer(
        "⚠️ You are about to send this message to the selected recipients.\n\n"
        f"{message.text}\n\nConfirm?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            compatible_button("✅ Confirm Broadcast", callback_data="broadcast:confirm", style="success"),
            compatible_button("✖️ Cancel", callback_data="broadcast:cancel", style="danger"),
        ]]),
    )


@router.callback_query(F.data.startswith("user:"))
async def user_callback(callback: CallbackQuery) -> None:
    """Handle configured callback buttons without executing arbitrary input."""
    action = callback.data.removeprefix("user:")
    await callback.answer()
    if action == "help":
        await callback.message.answer("Send a number such as 10482 and I will convert it to English words.")
    elif action == "about":
        await callback.message.answer("Numbers to Words Converter uses American English number formatting.")
    else:
        await callback.message.answer(f"Configured action: {action}")


@router.callback_query(F.data.in_({"broadcast:confirm", "broadcast:cancel"}))
async def broadcast_confirmation(
    callback: CallbackQuery, settings: Settings, session, state: FSMContext, bot
) -> None:
    if not await require_admin_callback(callback, settings):
        return
    await callback.answer()
    if callback.data == "broadcast:cancel":
        await state.clear()
        await edit_or_answer(callback, "Broadcast cancelled.", await build_admin_markup(session))
        return

    data = await state.get_data()
    target_user_id = data.get("target_user_id")
    recipients = await find_recipients(session, target_user_id)
    broadcast = await create_broadcast(
        session,
        target_type=data.get("target_type", "all"),
        target_user_id=target_user_id,
        message_text=data.get("message_text", ""),
        message_entities_json=data.get("message_entities", "[]"),
        total=len(recipients),
        status="running",
    )
    await edit_or_answer(callback, f"Broadcast started for {len(recipients)} recipient(s).")
    entities = deserialize_entities(data.get("message_entities"))
    successful = failed = blocked = 0
    for recipient in recipients:
        try:
            await bot.send_message(recipient.telegram_user_id, data["message_text"], entities=entities or None)
            successful += 1
        except TelegramRetryAfter as error:
            await asyncio.sleep(error.retry_after)
            try:
                await bot.send_message(recipient.telegram_user_id, data["message_text"], entities=entities or None)
                successful += 1
            except Exception:
                failed += 1
        except TelegramForbiddenError:
            blocked += 1
            await mark_blocked(session, recipient.telegram_user_id)
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)
    await update_broadcast(
        session,
        broadcast,
        success_count=successful,
        failure_count=failed,
        blocked_count=blocked,
        finished_at=datetime.now(timezone.utc),
        status="finished",
    )
    await state.clear()
    await callback.message.answer(
        f"✅ Broadcast finished.\n\nSuccessful: {successful}\nFailed: {failed}\nBlocked: {blocked}",
        reply_markup=await build_admin_markup(session),
    )
