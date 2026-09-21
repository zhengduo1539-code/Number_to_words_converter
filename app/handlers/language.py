from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from app.db.repository import set_user_language
from app.keyboards.language import language_markup
from app.services.i18n import LANGUAGE_BY_CODE, language_name, normalize_language, text
from app.handlers.start import send_welcome

router = Router(name="language")


@router.message(Command("lang"))
async def language_command(message: Message, session) -> None:
    current = normalize_language(await _current_language(session, message.from_user.id))
    await message.answer(text("language_menu", current), reply_markup=language_markup())


@router.callback_query(F.data.startswith("lang:"))
async def language_callback(callback: CallbackQuery, session, bot) -> None:
    requested_code = callback.data.split(":", 1)[1].lower()
    if requested_code not in LANGUAGE_BY_CODE:
        await callback.answer("Unsupported language", show_alert=True)
        return
    code = requested_code
    await set_user_language(session, callback.from_user.id, code)
    await callback.answer()
    await callback.message.edit_text(
        text("language_changed", code, language=language_name(code)),
    )
    await send_welcome(callback.message, session, bot, code)


async def _current_language(session, telegram_user_id: int) -> str:
    from app.db.repository import get_user_language

    return await get_user_language(session, telegram_user_id)