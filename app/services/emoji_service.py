from __future__ import annotations

import json
from typing import Any

from aiogram.types import MessageEntity


def serialize_entities(entities: list[MessageEntity] | None) -> str:
    return json.dumps([entity.model_dump(exclude_none=True) for entity in (entities or [])], ensure_ascii=False)


def deserialize_entities(value: str | None) -> list[MessageEntity]:
    if not value:
        return []
    try:
        return [MessageEntity.model_validate(item) for item in json.loads(value)]
    except (TypeError, ValueError, json.JSONDecodeError):
        return []


def custom_emoji_ids(entities: list[MessageEntity] | None) -> list[str]:
    return [entity.custom_emoji_id for entity in (entities or []) if entity.type == "custom_emoji" and entity.custom_emoji_id]


def first_custom_emoji_id(entities: list[MessageEntity] | None) -> str | None:
    ids = custom_emoji_ids(entities)
    return ids[0] if ids else None


def first_visible_fallback(text: str, entities: list[MessageEntity] | None) -> str | None:
    """Return the first Unicode emoji-like character for a button fallback."""
    for character in text.strip():
        if ord(character) > 0x1F000:
            return character
    return None
