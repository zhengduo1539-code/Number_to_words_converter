from __future__ import annotations

from aiogram import F, Router
from aiogram.types import Message

from app.db.repository import increment_conversion
from app.services.number_converter import is_number, number_to_words

router = Router(name="converter")


@router.message(F.text)
async def convert_handler(message: Message, session) -> None:
    value = message.text.strip()
    if not is_number(value):
        await message.answer("Please send a valid number, such as 10482, -125, 10,482, or 10.25.")
        return
    try:
        result = number_to_words(value)
    except ValueError:
        await message.answer("That number is too large or has an unsupported format.")
        return
    await increment_conversion(session, message.from_user.id)
    await message.answer(result)
