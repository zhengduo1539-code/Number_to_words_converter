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


def _utf16_length(value: str) -> int:
    return len(value.encode("utf-16-le")) // 2


def _utf16_to_index(value: str, offset: int) -> int:
    """Convert a Telegram UTF-16 offset to a Python string index."""
    units = 0
    for index, character in enumerate(value):
        next_units = units + _utf16_length(character)
        if next_units > offset:
            return index
        units = next_units
        if units == offset:
            return index + 1
    return len(value)


def localize_custom_emoji_entities(
    source_text: str,
    source_entities: list[MessageEntity] | None,
    localized_text: str,
) -> tuple[str, list[MessageEntity]]:
    """Put custom emoji from a source message into its localized counterpart.

    Telegram entity offsets are UTF-16 based. The source and localized messages
    normally have the same line structure, so keeping each emoji on its source
    line preserves the admin's visual layout. Leading and trailing emojis stay
    anchored to the corresponding edge after translation.
    """
    custom_entities = [
        entity
        for entity in (source_entities or [])
        if entity.type == "custom_emoji" and entity.custom_emoji_id
    ]
    if not custom_entities:
        return localized_text, []

    source_line_starts = [0]
    for index, character in enumerate(source_text):
        if character == "\n":
            source_line_starts.append(index + 1)
    localized_lines = localized_text.split("\n")
    localized_line_starts = [0]
    for index, character in enumerate(localized_text):
        if character == "\n":
            localized_line_starts.append(index + 1)

    insertions: list[tuple[int, str, MessageEntity, str]] = []
    for entity in custom_entities:
        source_start = _utf16_to_index(source_text, entity.offset)
        source_end = _utf16_to_index(source_text, entity.offset + entity.length)
        source_before = source_text[:source_start]
        source_line = source_before.count("\n")
        source_line_start = source_line_starts[min(source_line, len(source_line_starts) - 1)]
        target_line = min(source_line, len(localized_lines) - 1)
        target_line_text = localized_lines[target_line]
        target_line_start = localized_line_starts[target_line]
        source_line_end = source_text.find("\n", source_line_start)
        if source_line_end == -1:
            source_line_end = len(source_text)
        source_after = source_text[source_end:source_line_end]
        source_line_prefix = source_text[source_line_start:source_start]

        # Keep an emoji anchored to the edge where the admin placed it.
        # Translating a line changes its length, so copying the original
        # character column can incorrectly put a trailing emoji in the
        # middle of the translated sentence.
        if not source_line_prefix.strip():
            target_column = 0
        elif not source_after.strip():
            target_column = _utf16_length(target_line_text)
        else:
            source_column = _utf16_length(source_text[source_line_start:source_start])
            for previous_entity in custom_entities:
                previous_start = _utf16_to_index(source_text, previous_entity.offset)
                if previous_start >= source_start:
                    continue
                previous_line = source_text[:previous_start].count("\n")
                if previous_line == source_line:
                    previous_end = _utf16_to_index(
                        source_text,
                        previous_entity.offset + previous_entity.length,
                    )
                    source_column -= _utf16_length(
                        source_text[previous_start:previous_end]
                    )
            target_column = min(max(source_column, 0), _utf16_length(target_line_text))
        target_index = _utf16_to_index(
            localized_text[target_line_start:],
            target_column,
        ) + target_line_start
        emoji_text = source_text[source_start:source_end] or "🙂"
        separator = ""
        if (
            not source_after.strip()
            and source_start > source_line_start
            and source_text[source_start - 1].isspace()
            and not target_line_text.endswith((" ", "\t"))
        ):
            separator = " "
        insertions.append((target_index, separator + emoji_text, entity, separator))

    result = localized_text
    localized_entities: list[MessageEntity] = []
    shift = 0
    for target_index, inserted_text, entity, separator in sorted(
        insertions,
        key=lambda item: item[0],
    ):
        insertion_index = target_index + shift
        result = result[:insertion_index] + inserted_text + result[insertion_index:]
        localized_entities.append(
            entity.model_copy(
                update={
                    "offset": _utf16_length(
                        result[:insertion_index + len(separator)]
                    ),
                    "length": _utf16_length(inserted_text[len(separator):]),
                }
            )
        )
        shift += len(inserted_text)
    return result, localized_entities


def remove_custom_emoji_text(
    source_text: str,
    source_entities: list[MessageEntity] | None,
) -> str:
    """Remove custom-emoji placeholder characters before reinserting entities.

    Telegram stores a custom emoji as both visible placeholder text and an
    entity. If the source text is reused as the localized target, inserting
    the entity again would duplicate the emoji.
    """
    spans = []
    for entity in (source_entities or []):
        if entity.type != "custom_emoji" or not entity.custom_emoji_id:
            continue
        start = _utf16_to_index(source_text, entity.offset)
        end = _utf16_to_index(source_text, entity.offset + entity.length)
        spans.append((start, end))

    for start, end in sorted(spans, reverse=True):
        source_text = source_text[:start] + source_text[end:]
    return source_text


def first_visible_fallback(text: str, entities: list[MessageEntity] | None) -> str | None:
    """Return the first Unicode emoji-like character for a button fallback."""
    for character in text.strip():
        if ord(character) > 0x1F000:
            return character
    return None
