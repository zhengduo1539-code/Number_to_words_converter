from __future__ import annotations

from aiogram import F, Router
from aiogram.types import Message

from app.db.repository import get_user_language, increment_conversion
from app.services.i18n import text
from app.services.number_converter import is_number, number_to_words

router = Router(name="converter")


@router.message(F.text)
async def convert_handler(message: Message, session) -> None:
    value = message.text.strip()
    language = await get_user_language(session, message.from_user.id)
    if not is_number(value):
        await message.answer(text("invalid_number", language))
        return
    try:
        result = number_to_words(value)
    except ValueError:
        await message.answer(text("too_large", language))
        return
    await increment_conversion(session, message.from_user.id)
    await message.answer(number_to_words(value, language))
