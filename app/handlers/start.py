from __future__ import annotations

import logging
from html import escape

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.types import InputRichMessage, Message

from app.db.repository import DEFAULT_WELCOME, get_setting, list_welcome_buttons, upsert_user
from app.keyboards.buttons import welcome_markup
from app.services.emoji_service import (
    deserialize_entities,
    localize_custom_emoji_entities,
    remove_custom_emoji_text,
)
from app.services.i18n import (
    localized_custom_welcome,
    localized_default_welcome,
    normalize_language,
    without_default_welcome_decoration,
)
from app.services.number_converter import number_to_words

router = Router(name="start")
logger = logging.getLogger(__name__)


def _utf16_to_index(value: str, offset: int) -> int:
    """Translate Telegram's UTF-16 entity offset into a Python string index."""
    if offset < 0:
        return -1
    units = 0
    for index, character in enumerate(value):
        if units == offset:
            return index
        units += len(character.encode("utf-16-le")) // 2
        if units > offset:
            return -1
    return len(value) if units == offset else -1


def _custom_welcome_rich_html(message_text: str, entities: list) -> str | None:
    """Format a custom welcome as rich paragraphs without changing its visible text.

    Only Telegram custom-emoji entities are converted. If any entity offset is
    invalid or an unsupported formatting entity is present, use the old sender.
    """
    custom_entities = []
    for entity in entities:
        if entity.type != "custom_emoji" or not entity.custom_emoji_id:
            return None
        start = _utf16_to_index(message_text, entity.offset)
        end = _utf16_to_index(message_text, entity.offset + entity.length)
        if start < 0 or end <= start:
            return None
        custom_entities.append((start, end, entity.custom_emoji_id))

    custom_entities.sort(key=lambda item: item[0])
    parts = []
    cursor = 0
    for start, end, emoji_id in custom_entities:
        if start < cursor:
            return None
        parts.append(escape(message_text[cursor:start]))
        placeholder = escape(message_text[start:end])
        safe_emoji_id = escape(emoji_id, quote=True)
        parts.append(f'<tg-emoji emoji-id="{safe_emoji_id}">{placeholder}</tg-emoji>')
        cursor = end
    parts.append(escape(message_text[cursor:]))

    escaped_text = "".join(parts)
    paragraphs = escaped_text.split("\n\n")
    rendered_paragraphs = [
        f"<p>{paragraph.replace(chr(10), '<br/>')}</p>"
        for paragraph in paragraphs
    ]
    return "".join(rendered_paragraphs)


def _default_welcome_rich_html(message_text: str) -> str | None:
    """Build a structured rich message only from the known default welcome layout.

    Returning None deliberately keeps the normal-message path as the compatibility
    fallback if a localized template changes its paragraph structure.
    """
    sections = message_text.split("\n\n")
    if len(sections) != 4:
        return None

    heading, introduction, example_section, footer = sections
    example_lines = example_section.split("\n", 1)
    if len(example_lines) != 2:
        return None
    example_heading, example_value = example_lines

    return (
        f"<h2>{escape(heading)}</h2>"
        f"<p>{escape(introduction)}</p>"
        "<hr/>"
        f"<p><b>{escape(example_heading)}</b></p>"
        f"<pre>{escape(example_value)}</pre>"
        f"<footer>{escape(footer)}</footer>"
    )


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
    is_default_welcome = text == DEFAULT_WELCOME
    if is_default_welcome:
        text = localized_default_welcome(language, number_to_words("10482", language))
        entities = []
    else:
        # Keep the stored message and its custom emoji entities untouched in the
        # database; the Rich Message sender below converts them only for delivery.
        entities = deserialize_entities(await get_setting(session, "welcome_entities", "[]"))
        normalized_language = normalize_language(language)
        if normalized_language == "en":
            localized_text = without_default_welcome_decoration(
                remove_custom_emoji_text(text, entities)
            )
        else:
            localized_text = localized_custom_welcome(
                language,
                number_to_words("10482", language),
            )
        text, entities = localize_custom_emoji_entities(text, entities, localized_text)
    buttons = await list_welcome_buttons(session)
    me = await bot.get_me()
    reply_markup = welcome_markup(buttons, me.username, language)

    rich_html = (
        _default_welcome_rich_html(text)
        if is_default_welcome
        else _custom_welcome_rich_html(text, entities)
    )
    send_rich_message = getattr(bot, "send_rich_message", None)
    if rich_html and callable(send_rich_message):
        try:
            await send_rich_message(
                chat_id=message.chat.id,
                rich_message=InputRichMessage(html=rich_html),
                reply_markup=reply_markup,
            )
            return
        except (TelegramBadRequest, TypeError, ValueError) as error:
            # A rejected rich payload should not prevent the user seeing the
            # welcome message; send the exact legacy text instead.
            logger.warning(
                "Could not send rich welcome message; falling back to normal message: %s",
                error,
            )

    await message.answer(
        text,
        entities=entities or None,
        reply_markup=reply_markup,
    )
