from __future__ import annotations

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.db.repository import DEFAULT_WELCOME, get_setting, list_welcome_buttons, upsert_user
from app.keyboards.buttons import welcome_markup
from app.services.emoji_service import deserialize_entities, localize_custom_emoji_entities
from app.services.i18n import (
    localized_custom_welcome,
    localized_default_welcome,
    normalize_language,
    without_default_welcome_decoration,
)
from app.services.number_converter import number_to_words

router = Router(name="start")


@router.message(CommandStart())
async def start_handler(message: Message, session, bot) -> None:
    user = await upsert_user(session, message.from_user, started=True)
    await send_welcome(message, session, bot, normalize_language(user.preferred_language))


async def send_welcome(message: Message, session, bot, language: str = "en") -> None:
    # The setting may be missing on an existing database created before
    # defaults were initialized. Never send an empty Telegram message.
    text = await get_setting(session, "welcome_text", DEFAULT_WELCOME)
    if not text.strip():
        text = DEFAULT_WELCOME
    if text == DEFAULT_WELCOME:
        text = localized_default_welcome(language, number_to_words("10482", language))
        entities = []
    else:
        entities = deserialize_entities(await get_setting(session, "welcome_entities", "[]"))
        normalized_language = normalize_language(language)
        localized_text = (
            localized_custom_welcome(language, number_to_words("10482", language))
            if normalized_language != "en"
            else without_default_welcome_decoration(text)
        )
        text, entities = localize_custom_emoji_entities(text, entities, localized_text)
    buttons = await list_welcome_buttons(session)
    me = await bot.get_me()
    await message.answer(
        text,
        entities=entities or None,
        reply_markup=welcome_markup(buttons, me.username, language),
    )
