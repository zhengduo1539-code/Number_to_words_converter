from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pydantic import ValidationError

from app.db.models import AdminButton, WelcomeButton
from app.services.i18n import normalize_language


def compatible_button(
    text: str,
    *,
    callback_data: str | None = None,
    url: str | None = None,
    style: str | None = None,
    icon_custom_emoji_id: str | None = None,
) -> InlineKeyboardButton:
    payload: dict[str, object] = {"text": text}
    if callback_data:
        payload["callback_data"] = callback_data
    if url:
        payload["url"] = url
    if style:
        payload["style"] = style
    if icon_custom_emoji_id:
        payload["icon_custom_emoji_id"] = icon_custom_emoji_id
    try:
        return InlineKeyboardButton(**payload)
    except (TypeError, ValidationError):
        payload.pop("style", None)
        payload.pop("icon_custom_emoji_id", None)
        return InlineKeyboardButton(**payload)


def button_text(label: str, fallback_emoji: str | None) -> str:
    if fallback_emoji and not label.startswith(fallback_emoji):
        return f"{fallback_emoji} {label}"
    return label


def welcome_markup(
    buttons: list[WelcomeButton], bot_username: str | None, language: str = "en"
) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    share_labels = {
        "en": "🔗 Share Bot",
        "bn": "🔗 বট শেয়ার করুন",
        "zh": "🔗 分享机器人",
        "my": "🔗 Bot ကိုမျှဝေမည်",
        "am": "🔗 ቦቱን አጋራ",
        "om": "🔗 Botii qoodi",
        "es": "🔗 Compartir bot",
        "fr": "🔗 Partager le bot",
        "ru": "🔗 Поделиться ботом",
        "ar": "🔗 مشاركة البوت",
    }
    language = normalize_language(language)
    for item in buttons:
        label = button_text(item.label, item.fallback_emoji)
        if item.button_type == "share":
            if item.label == "🔗 Share Bot":
                label = share_labels[language]
            username = bot_username or "this_bot"
            url = f"https://t.me/share/url?url=https://t.me/{username}&text=Try%20Numbers%20to%20Words%20Converter"
            rows.append([compatible_button(label, url=url, style=item.style, icon_custom_emoji_id=item.icon_custom_emoji_id)])
        elif item.button_type == "url":
            rows.append([compatible_button(label, url=item.url, style=item.style, icon_custom_emoji_id=item.icon_custom_emoji_id)])
        else:
            rows.append([compatible_button(label, callback_data=f"user:{item.callback_action}", style=item.style, icon_custom_emoji_id=item.icon_custom_emoji_id)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def admin_markup(buttons: list[AdminButton]) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for item in buttons:
        rows.append([compatible_button(button_text(item.label, item.fallback_emoji), callback_data=f"admin:{item.action}", style=item.style, icon_custom_emoji_id=item.icon_custom_emoji_id)])
    return InlineKeyboardMarkup(inline_keyboard=rows)
