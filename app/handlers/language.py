from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.config import Settings
from app.db.repository import get_setting, set_user_language
from app.keyboards.language import language_markup
from app.services.emoji_service import deserialize_entities, localize_custom_emoji_entities
from app.services.i18n import (
    LANGUAGE_BY_CODE,
    language_name,
    localized_custom_language_text,
    normalize_language,
    text,
)
from app.handlers.start import send_welcome
from app.states.workflows import RequestLanguageStates

router = Router(name="language")
logger = logging.getLogger(__name__)


@router.message(Command("lang"))
async def language_command(message: Message, session) -> None:
    current = normalize_language(await _current_language(session, message.from_user.id))
    custom_text = await get_setting(session, "language_menu_text")
    if custom_text:
        menu_text = localized_custom_language_text("language_menu", current, custom_text)
        menu_text, entities = localize_custom_emoji_entities(
            custom_text,
            deserialize_entities(await get_setting(session, "language_menu_entities", "[]")),
            menu_text,
        )
    else:
        menu_text = text("language_menu", current)
        entities = []
    await message.answer(
        menu_text,
        entities=entities or None,
        reply_markup=language_markup(current),
    )


@router.callback_query(F.data == "request_language")
async def request_language_callback(
    callback: CallbackQuery,
    session,
    state: FSMContext,
) -> None:
    language = normalize_language(await _current_language(session, callback.from_user.id))
    await state.set_state(RequestLanguageStates.waiting_text)
    await callback.answer()
    await callback.message.answer(text("request_language_prompt", language))


@router.callback_query(F.data.startswith("lang:"))
async def language_callback(callback: CallbackQuery, session, bot) -> None:
    requested_code = callback.data.split(":", 1)[1].lower()
    if requested_code not in LANGUAGE_BY_CODE:
        await callback.answer("Unsupported language", show_alert=True)
        return
    code = requested_code
    await set_user_language(session, callback.from_user.id, code)
    await callback.answer()
    custom_text = await get_setting(session, "language_changed_text")
    if custom_text:
        changed_text = localized_custom_language_text(
            "language_changed",
            code,
            custom_text,
            language=language_name(code),
        )
        changed_text, entities = localize_custom_emoji_entities(
            custom_text,
            deserialize_entities(await get_setting(session, "language_changed_entities", "[]")),
            changed_text,
        )
    else:
        changed_text = text("language_changed", code, language=language_name(code))
        entities = []
    await callback.message.edit_text(
        changed_text,
        entities=entities or None,
        reply_markup=language_markup(code),
    )
    await send_welcome(callback.message, session, bot, code)


@router.message(RequestLanguageStates.waiting_text)
async def request_language_message(
    message: Message,
    state: FSMContext,
    session,
    settings: Settings,
    bot,
) -> None:
    language = normalize_language(await _current_language(session, message.from_user.id))
    requested_language = (message.text or "").strip()
    if not requested_language:
        await message.answer(text("request_language_empty", language))
        return

    user = message.from_user
    username = f"@{user.username}" if user.username else "no username"
    admin_message = (
        "🌐 Language request\n\n"
        f"From: {user.first_name or 'Unnamed'} ({username})\n"
        f"Telegram ID: {user.id}\n"
        f"Requested language: {requested_language[:2000]}"
    )
    delivered = 0
    for admin_id in settings.admin_ids:
        try:
            await bot.send_message(admin_id, admin_message)
            delivered += 1
        except (TelegramForbiddenError, TelegramBadRequest) as error:
            logger.warning(
                "Could not send language request to admin %s: %s",
                admin_id,
                error,
            )
        except Exception:
            logger.exception("Unexpected error sending language request to admin %s", admin_id)

    await state.clear()
    result_key = "request_language_sent" if delivered else "request_language_failed"
    await message.answer(text(result_key, language))


async def _current_language(session, telegram_user_id: int) -> str:
    from app.db.repository import get_user_language

    return await get_user_language(session, telegram_user_id)