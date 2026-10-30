from __future__ import annotations

from typing import Any

from aiogram.types import MessageEntity

from app.db.repository import set_setting
from app.services.emoji_service import deserialize_entities, serialize_entities
from app.services.i18n import LANGUAGES, normalize_language, text


def reminder_text_setting_key(locale: str) -> str:
    return f"inactive_reminder_text:{normalize_language(locale)}"


def reminder_entities_setting_key(locale: str) -> str:
    return f"inactive_reminder_entities:{normalize_language(locale)}"


async def get_reminder_message(
    database: Any,
    locale: str,
) -> tuple[str, list[MessageEntity]]:
    """Return the configured reminder for one locale, or its localized default."""
    language = normalize_language(locale)
    keys = {
        reminder_text_setting_key(language),
        reminder_entities_setting_key(language),
    }
    documents = await database.bot_settings.find(
        {"key": {"$in": list(keys)}}
    ).to_list(length=2)
    settings = {
        str(item.get("key")): str(item.get("value") or "")
        for item in documents
    }
    custom_text = settings.get(reminder_text_setting_key(language), "")
    if not custom_text.strip():
        return text("inactive_reminder", language), []

    entities = deserialize_entities(
        settings.get(reminder_entities_setting_key(language), "[]")
    )
    return custom_text, entities


async def get_customized_reminder_languages(database: Any) -> set[str]:
    """Return locales with a non-empty custom inactivity reminder."""
    keys = [reminder_text_setting_key(language.code) for language in LANGUAGES]
    documents = await database.bot_settings.find(
        {"key": {"$in": keys}}
    ).to_list(length=len(keys))
    configured = {
        str(item.get("key")): str(item.get("value") or "")
        for item in documents
    }
    return {
        language.code
        for language in LANGUAGES
        if configured.get(reminder_text_setting_key(language.code), "").strip()
    }


async def save_reminder_message(
    session: Any,
    locale: str,
    message_text: str,
    entities: list[MessageEntity] | None,
) -> None:
    language = normalize_language(locale)
    await set_setting(session, reminder_text_setting_key(language), message_text)
    await set_setting(
        session,
        reminder_entities_setting_key(language),
        serialize_entities(entities),
    )


async def reset_reminder_message(session: Any, locale: str) -> None:
    language = normalize_language(locale)
    await set_setting(session, reminder_text_setting_key(language), "")
    await set_setting(session, reminder_entities_setting_key(language), "[]")


async def reset_reminder_messages(session: Any) -> None:
    for language in LANGUAGES:
        await reset_reminder_message(session, language.code)
