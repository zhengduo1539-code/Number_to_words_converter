from __future__ import annotations

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.db.repository import get_setting, list_welcome_buttons, upsert_user
from app.keyboards.buttons import welcome_markup
from app.services.emoji_service import deserialize_entities

router = Router(name="start")


@router.message(CommandStart())
async def start_handler(message: Message, session, bot) -> None:
    await upsert_user(session, message.from_user, started=True)
    text = await get_setting(session, "welcome_text")
    entities = deserialize_entities(await get_setting(session, "welcome_entities", "[]"))
    buttons = await list_welcome_buttons(session)
    me = await bot.get_me()
    await message.answer(text, entities=entities or None, reply_markup=welcome_markup(buttons, me.username))
