from __future__ import annotations

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.db.repository import DEFAULT_WELCOME, get_setting, list_welcome_buttons, upsert_user
from app.keyboards.buttons import welcome_markup
from app.services.emoji_service import deserialize_entities
from app.services.i18n import localized_default_welcome, normalize_language
from app.services.number_converter import number_to_words

router = Router(name="start")


@router.message(CommandStart())
async def start_handler(message: Message, session, bot) -> None:
    user = await upsert_user(session, message.from_user, started=True)
    await send_welcome(message, session, bot, normalize_language(user.preferred_language))


async def send_welcome(message: Message, session, bot, language: str = "en") -> None:
    text = await get_setting(session, "welcome_text")
    if text == DEFAULT_WELCOME:
        text = localized_default_welcome(language, number_to_words("10482", language))
        entities = []
    else:
        entities = deserialize_entities(await get_setting(session, "welcome_entities", "[]"))
    buttons = await list_welcome_buttons(session)
    me = await bot.get_me()
    await message.answer(
        text,
        entities=entities or None,
        reply_markup=welcome_markup(buttons, me.username, language),
    )
