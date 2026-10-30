from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.services.i18n import normalize_language, text


def reminder_settings_markup(enabled: bool, locale: str) -> InlineKeyboardMarkup:
    language = normalize_language(locale)
    action = "reminder_turn_off" if enabled else "reminder_turn_on"
    callback = "reminder:off" if enabled else "reminder:on"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=text(action, language), callback_data=callback)]
        ]
    )
