from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup

from app.db.models import AdminButton, WelcomeButton
from app.keyboards.buttons import compatible_button, button_text


def customization_markup() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [compatible_button("📝 Welcome Message", callback_data="ctm:welcome", style="primary")],
        [compatible_button("🔘 Welcome Buttons", callback_data="ctm:welcome_buttons", style="primary")],
        [compatible_button("🛠 Admin Panel Buttons", callback_data="ctm:admin_buttons", style="primary")],
        [compatible_button("♻️ Reset All", callback_data="ctm:reset_all", style="danger")],
        [compatible_button("✖️ Cancel", callback_data="admin:back", style="danger")],
    ])


def welcome_message_markup() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [compatible_button("✏️ Edit", callback_data="ctm:welcome_edit", style="primary"),
         compatible_button("♻️ Reset", callback_data="ctm:welcome_reset", style="danger")],
        [compatible_button("⬅️ Back", callback_data="ctm:home", style="primary")],
    ])


def welcome_buttons_markup(buttons: list[WelcomeButton]) -> InlineKeyboardMarkup:
    rows = [
        [compatible_button(button_text(item.label, item.fallback_emoji), callback_data=f"ctm:wb_edit:{item.id}", style="primary"),
         compatible_button("Remove", callback_data=f"ctm:wb_remove:{item.id}", style="danger")]
        for item in buttons
    ]
    rows.extend([
        [compatible_button("➕ Add Button", callback_data="ctm:wb_add", style="success")],
        [compatible_button("♻️ Reset Defaults", callback_data="ctm:wb_reset", style="danger")],
        [compatible_button("⬅️ Back", callback_data="ctm:home", style="primary")],
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def action_type_markup() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [compatible_button("🔗 Share Bot Button", callback_data="ctm:wb_type:share", style="primary")],
        [compatible_button("🔗 URL Button", callback_data="ctm:wb_type:url", style="primary")],
        [compatible_button("⚡ Callback Button", callback_data="ctm:wb_type:callback", style="primary")],
        [compatible_button("✖️ Cancel", callback_data="ctm:cancel", style="danger")],
    ])


def style_markup(prefix: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [compatible_button("Primary", callback_data=f"{prefix}:style:primary", style="primary"),
         compatible_button("Success", callback_data=f"{prefix}:style:success", style="success"),
         compatible_button("Danger", callback_data=f"{prefix}:style:danger", style="danger")],
        [compatible_button("Skip / Unicode emoji", callback_data=f"{prefix}:style:skip", style="primary"),
         compatible_button("✖️ Cancel", callback_data="ctm:cancel", style="danger")],
    ])


def admin_buttons_markup(buttons: list[AdminButton]) -> InlineKeyboardMarkup:
    rows = [
        [compatible_button(button_text(item.label, item.fallback_emoji), callback_data=f"ctm:ab_edit:{item.action}", style="primary")]
        for item in buttons
    ]
    rows.extend([
        [compatible_button("♻️ Reset Defaults", callback_data="ctm:ab_reset", style="danger")],
        [compatible_button("⬅️ Back", callback_data="ctm:home", style="primary")],
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def reset_all_markup() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [compatible_button("✅ Confirm Reset", callback_data="ctm:reset_confirm", style="danger"),
         compatible_button("✖️ Cancel", callback_data="ctm:home", style="primary")],
    ])


def cancel_markup(callback_data: str = "ctm:cancel") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [compatible_button("✖️ Cancel", callback_data=callback_data, style="danger")],
    ])
