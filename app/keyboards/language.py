from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup

from app.keyboards.buttons import compatible_button
from app.services.i18n import LANGUAGES, normalize_language, text


def language_markup(
    language: str = "en",
    custom_emoji_ids: dict[str, str] | None = None,
) -> InlineKeyboardMarkup:
    locale = normalize_language(language)
    icon_ids = custom_emoji_ids or {}
    rows = []
    for index in range(0, len(LANGUAGES), 2):
        row = []
        for item in LANGUAGES[index:index + 2]:
            row.append(
                compatible_button(
                    item.menu_label,
                    callback_data=f"lang:{item.code}",
                    style="success",
                    icon_custom_emoji_id=icon_ids.get(item.code),
                )
            )
        rows.append(row)
    rows.append([
        compatible_button(
            text("request_language_button", locale),
            callback_data="request_language",
            style="primary",
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)
