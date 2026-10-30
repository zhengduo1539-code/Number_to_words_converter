from __future__ import annotations

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from app.db.repository import (
    get_user_language,
    get_user_reminders_enabled,
    set_user_reminders_enabled,
)
from app.keyboards.reminder import reminder_settings_markup
from app.services.i18n import normalize_language, text

router = Router(name="reminder")


def _settings_text(enabled: bool, locale: str) -> str:
    language = normalize_language(locale)
    status_key = "reminder_status_on" if enabled else "reminder_status_off"
    return text(
        "reminder_settings",
        language,
        status=text(status_key, language),
    )


@router.message(Command("reminder"))
async def reminder_command(message: Message, session) -> None:
    language = normalize_language(
        await get_user_language(session, message.from_user.id)
    )
    if message.chat.type != "private":
        await message.answer(text("reminder_private_only", language))
        return

    enabled = await get_user_reminders_enabled(session, message.from_user.id)
    await message.answer(
        _settings_text(enabled, language),
        reply_markup=reminder_settings_markup(enabled, language),
    )


@router.callback_query(F.data.in_({"reminder:on", "reminder:off"}))
async def reminder_toggle_callback(callback: CallbackQuery, session) -> None:
    enabled = callback.data == "reminder:on"
    await set_user_reminders_enabled(session, callback.from_user.id, enabled)
    language = normalize_language(
        await get_user_language(session, callback.from_user.id)
    )
    await callback.answer()
    if callback.message:
        try:
            await callback.message.edit_text(
                _settings_text(enabled, language),
                reply_markup=reminder_settings_markup(enabled, language),
            )
        except TelegramBadRequest:
            await callback.message.answer(
                _settings_text(enabled, language),
                reply_markup=reminder_settings_markup(enabled, language),
            )
