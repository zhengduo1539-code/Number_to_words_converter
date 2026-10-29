from __future__ import annotations

import re

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
            custom_emoji_id = icon_ids.get(item.code)
            # The custom emoji icon replaces the decorative country flag in the label.
            # Keep the original flag whenever this language has no custom icon configured.
            label = item.menu_label
            if custom_emoji_id:
                label = re.sub(r"^[\U0001F1E6-\U0001F1FF]{2}\s+", "", label, count=1)
            row.append(
                compatible_button(
                    label,
                    callback_data=f"lang:{item.code}",
                    style="success",
                    icon_custom_emoji_id=custom_emoji_id,
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
