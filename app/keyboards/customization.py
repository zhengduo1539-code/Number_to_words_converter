from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup

from app.db.models import AdminButton, WelcomeButton
from app.services.i18n import LANGUAGES
from app.keyboards.buttons import compatible_button, button_text


def customization_markup() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [compatible_button("📝 Welcome Message", callback_data="ctm:welcome", style="primary")],
        [compatible_button("🌐 Language Messages", callback_data="ctm:language_messages", style="primary")],
        [compatible_button("🌐 Language Selection Buttons", callback_data="ctm:language_buttons", style="primary")],
        [compatible_button("⏳ Loading Message", callback_data="ctm:loading_message", style="primary")],
        [compatible_button("🔔 Inactivity Reminder Messages", callback_data="ctm:reminder", style="primary")],
        [compatible_button("🔘 Welcome Buttons", callback_data="ctm:welcome_buttons", style="primary")],
        [compatible_button("🛠 Admin Panel Buttons", callback_data="ctm:admin_buttons", style="primary")],
        [compatible_button("♻️ Reset All", callback_data="ctm:reset_all", style="danger")],
        [compatible_button("✖️ Cancel", callback_data="admin:back", style="danger")],
    ])


def language_messages_markup() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [compatible_button("✏️ Edit Choose Language", callback_data="ctm:language_menu_edit", style="primary")],
        [compatible_button("♻️ Reset Choose Language", callback_data="ctm:language_menu_reset", style="danger")],
        [compatible_button("✏️ Edit Language Changed", callback_data="ctm:language_changed_edit", style="primary")],
        [compatible_button("♻️ Reset Language Changed", callback_data="ctm:language_changed_reset", style="danger")],
        [compatible_button("✏️ Edit Request Language Prompt", callback_data="ctm:request_language_prompt_edit", style="primary")],
        [compatible_button("♻️ Reset Request Prompt", callback_data="ctm:request_language_prompt_reset", style="danger")],
        [compatible_button("✏️ Edit Request Sent Confirmation", callback_data="ctm:request_language_sent_edit", style="primary")],
        [compatible_button("♻️ Reset Request Sent", callback_data="ctm:request_language_sent_reset", style="danger")],
        [compatible_button("⬅️ Back", callback_data="ctm:home", style="primary")],
    ])

def loading_message_markup() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [compatible_button("✏️ Edit", callback_data="ctm:loading_edit", style="primary"),
         compatible_button("♻️ Reset", callback_data="ctm:loading_reset", style="danger")],
        [compatible_button("⬅️ Back", callback_data="ctm:home", style="primary")],
    ])


def reminder_languages_markup(customized_languages: set[str]) -> InlineKeyboardMarkup:
    rows = []
    for index in range(0, len(LANGUAGES), 2):
        row = []
        for language in LANGUAGES[index:index + 2]:
            label = (
                f"✅ {language.menu_label}"
                if language.code in customized_languages
                else language.menu_label
            )
            row.append(
                compatible_button(
                    label,
                    callback_data=f"ctm:reminder_language:{language.code}",
                    style="primary",
                )
            )
        rows.append(row)
    rows.append([
        compatible_button("⬅️ Back", callback_data="ctm:home", style="primary")
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def reminder_language_markup(language_code: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            compatible_button("✏️ Edit Message", callback_data=f"ctm:reminder_edit:{language_code}", style="primary"),
            compatible_button("👁 Preview", callback_data=f"ctm:reminder_preview:{language_code}", style="success"),
        ],
        [
            compatible_button("♻️ Reset to Default", callback_data=f"ctm:reminder_reset:{language_code}", style="danger"),
        ],
        [
            compatible_button("⬅️ Back to Languages", callback_data="ctm:reminder", style="primary"),
        ],
    ])


def welcome_message_markup() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [compatible_button("✏️ Edit", callback_data="ctm:welcome_edit", style="primary"),
         compatible_button("♻️ Reset", callback_data="ctm:welcome_reset", style="danger")],
        [compatible_button("🧩 Rich Message Layout", callback_data="ctm:rich_layout", style="primary")],
        [compatible_button("⬅️ Back", callback_data="ctm:home", style="primary")],
    ])


def rich_welcome_layout_markup(layout: dict, customized: bool) -> InlineKeyboardMarkup:
    enabled = lambda key: "✅" if layout.get(key, True) else "❌"
    return InlineKeyboardMarkup(inline_keyboard=[
        [compatible_button("✏️ Edit Heading", callback_data="ctm:rich_edit:heading", style="primary"),
         compatible_button("✏️ Edit Body", callback_data="ctm:rich_edit:body", style="primary")],
        [compatible_button("✏️ Edit Example Label", callback_data="ctm:rich_edit:example_heading", style="primary"),
         compatible_button("✏️ Edit Example", callback_data="ctm:rich_edit:example", style="primary")],
        [compatible_button("✏️ Edit Footer", callback_data="ctm:rich_edit:footer", style="primary")],
        [compatible_button(f"{enabled('enabled')} Rich Messages", callback_data="ctm:rich_toggle:enabled", style="primary"),
         compatible_button(f"{enabled('show_heading')} Heading", callback_data="ctm:rich_toggle:show_heading", style="primary")],
        [compatible_button(f"{enabled('show_divider')} Divider", callback_data="ctm:rich_toggle:show_divider", style="primary"),
         compatible_button(f"{enabled('show_example')} Example", callback_data="ctm:rich_toggle:show_example", style="primary")],
        [compatible_button(f"{enabled('monospace')} Monospace", callback_data="ctm:rich_toggle:monospace", style="primary"),
         compatible_button(f"{enabled('show_footer')} Footer", callback_data="ctm:rich_toggle:show_footer", style="primary")],
        [compatible_button("👁 Preview", callback_data="ctm:rich_preview", style="success"),
         compatible_button("♻️ Reset Layout", callback_data="ctm:rich_reset", style="danger")],
        [compatible_button("⬅️ Back", callback_data="ctm:welcome", style="primary")],
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



def language_selection_buttons_markup(icon_ids: dict[str, str]) -> InlineKeyboardMarkup:
    rows = []
    for index in range(0, len(LANGUAGES), 2):
        row = []
        for item in LANGUAGES[index:index + 2]:
            label = f"✅ {item.menu_label}" if icon_ids.get(item.code) else item.menu_label
            row.append(
                compatible_button(
                    label,
                    callback_data=f"ctm:language_button:{item.code}",
                    style="primary",
                )
            )
        rows.append(row)
    request_label = "✅ 🌐 Request Language" if icon_ids.get("request_language") else "🌐 Request Language"
    rows.append([
        compatible_button(
            request_label,
            callback_data="ctm:language_button:request_language",
            style="primary",
        )
    ])
    rows.extend([
        [compatible_button("♻️ Reset All Icons", callback_data="ctm:language_buttons_reset", style="danger")],
        [compatible_button("⬅️ Back", callback_data="ctm:home", style="primary")],
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)
