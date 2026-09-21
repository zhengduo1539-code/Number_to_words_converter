from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup

from app.keyboards.buttons import compatible_button
from app.services.i18n import LANGUAGES


def language_markup() -> InlineKeyboardMarkup:
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
    return InlineKeyboardMarkup(inline_keyboard=rows)