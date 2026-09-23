from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup

from app.keyboards.buttons import compatible_button
from app.services.i18n import LANGUAGES, normalize_language, text


def language_markup(language: str = "en") -> InlineKeyboardMarkup:
    language = normalize_language(language)
    rows = []
    for index in range(0, len(LANGUAGES), 2):
        rows.append([
            compatible_button(
                language.menu_label,
                callback_data=f"lang:{language.code}",
                style="success",
            )
            for language in LANGUAGES[index:index + 2]
        ])
    rows.append([
        compatible_button(
            text("request_language_button", language),
            callback_data="request_language",
            style="primary",
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)