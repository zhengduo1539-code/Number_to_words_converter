from __future__ import annotations

import asyncio

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message

from app.db.repository import get_setting, get_user_language, increment_conversion
from app.services.emoji_service import (
    deserialize_entities,
    localize_custom_emoji_entities,
    remove_custom_emoji_text,
)
from app.services.i18n import normalize_language, text
from app.services.number_converter import is_number, number_to_words

router = Router(name="converter")
LOADING_DELAY_SECONDS = 2.0


@router.message(F.text)
async def convert_handler(message: Message, session) -> None:
    value = message.text.strip()
    language = await get_user_language(session, message.from_user.id)
    if not is_number(value):
        await message.answer(text("invalid_number", language))
        return
    try:
        result = number_to_words(value, language)
    except ValueError:
        await message.answer(text("too_large", language))
        return

    loading_text = await get_setting(session, "loading_text")
    if loading_text.strip():
        loading_entities = deserialize_entities(
            await get_setting(session, "loading_entities", "[]")
        )
        if normalize_language(language) == "en":
            localized_loading = remove_custom_emoji_text(
                loading_text,
                loading_entities,
            )
        else:
            localized_loading = text("loading", language)
        loading_text, loading_entities = localize_custom_emoji_entities(
            loading_text,
            loading_entities,
            localized_loading,
        )
    else:
        loading_text = text("loading", language)
        loading_entities = []

    loading_message = await message.answer(
        loading_text,
        entities=loading_entities or None,
    )
    await increment_conversion(session, message.from_user.id)
    await asyncio.sleep(LOADING_DELAY_SECONDS)
    try:
        await loading_message.edit_text(result)
    except TelegramBadRequest:
        # If Telegram no longer allows editing the placeholder, still return
        # the conversion result instead of letting the handler fail.
        await message.answer(result)
