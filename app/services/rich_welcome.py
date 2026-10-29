from __future__ import annotations

import json
from html import escape
from typing import Any

from aiogram.types import MessageEntity

from app.services.emoji_service import deserialize_entities, serialize_entities


RICH_LAYOUT_SETTING = "welcome_rich_layout"
RICH_LAYOUT_FIELDS = {
    "heading": "Heading",
    "body": "Body",
    "example_heading": "Example label",
    "example": "Example value",
    "footer": "Footer",
}
RICH_LAYOUT_TOGGLES = {
    "enabled": "Rich Messages",
    "show_heading": "Heading",
    "show_divider": "Divider",
    "show_example": "Example section",
    "monospace": "Monospace example",
    "show_footer": "Footer",
}
_TEXT_FIELDS = tuple(RICH_LAYOUT_FIELDS)
_ENTITY_FIELDS = {field: f"{field}_entities" for field in _TEXT_FIELDS}
_FLAG_FIELDS = tuple(RICH_LAYOUT_TOGGLES)


def _default_flags() -> dict[str, Any]:
    return {
        "schema": 1,
        "enabled": True,
        "show_heading": True,
        "show_divider": True,
        "show_example": True,
        "monospace": True,
        "show_footer": True,
    }


def rich_layout_from_text(
    message_text: str,
    entities: list[MessageEntity] | None = None,
    *,
    is_default_welcome: bool,
) -> dict[str, Any]:
    """Create a safe, in-memory layout without modifying saved welcome settings.

    The built-in welcome is split into its known sections. A custom welcome is
    initially kept intact as the body so opening /ctm never changes its content
    or invents a heading/example/footer for the administrator.
    """
    layout = _default_flags()
    for field in _TEXT_FIELDS:
        layout[field] = ""
        layout[_ENTITY_FIELDS[field]] = "[]"

    if is_default_welcome:
        sections = message_text.split("\n\n")
        if len(sections) == 4:
            example_lines = sections[2].split("\n", 1)
            if len(example_lines) == 2:
                layout.update({
                    "heading": sections[0],
                    "body": sections[1],
                    "example_heading": example_lines[0],
                    "example": example_lines[1],
                    "footer": sections[3],
                })
                return layout

    layout["body"] = message_text
    layout[_ENTITY_FIELDS["body"]] = serialize_entities(entities)
    # Keep arbitrary custom content intact until the administrator opts into
    # assigning it to structured Rich Message sections.
    layout.update({
        "show_heading": False,
        "show_divider": False,
        "show_example": False,
        "show_footer": False,
        "monospace": True,
    })
    return layout


def parse_rich_layout(raw_value: str | None) -> dict[str, Any] | None:
    """Validate a persisted layout; malformed settings are ignored safely."""
    if not raw_value:
        return None
    try:
        raw = json.loads(raw_value)
    except (TypeError, ValueError):
        return None
    if not isinstance(raw, dict) or raw.get("schema") != 1:
        return None

    layout = _default_flags()
    for field in _TEXT_FIELDS:
        value = raw.get(field, "")
        if not isinstance(value, str):
            return None
        layout[field] = value
        entity_json = raw.get(_ENTITY_FIELDS[field], "[]")
        if isinstance(entity_json, list):
            entity_json = json.dumps(entity_json, ensure_ascii=False)
        if not isinstance(entity_json, str):
            return None
        # Avoid accepting arbitrary entity types/offsets as executable markup.
        entities = deserialize_entities(entity_json)
        if any(entity.type != "custom_emoji" or not entity.custom_emoji_id for entity in entities):
            return None
        layout[_ENTITY_FIELDS[field]] = serialize_entities(entities)

    for flag in _FLAG_FIELDS:
        value = raw.get(flag, layout.get(flag, True))
        if not isinstance(value, bool):
            return None
        layout[flag] = value
    return layout


def serialize_rich_layout(layout: dict[str, Any]) -> str:
    """Serialize only known, validated fields before storing them in BotSetting."""
    cleaned = _default_flags()
    for field in _TEXT_FIELDS:
        cleaned[field] = str(layout.get(field, ""))
        entities = deserialize_entities(str(layout.get(_ENTITY_FIELDS[field], "[]")))
        if any(entity.type != "custom_emoji" or not entity.custom_emoji_id for entity in entities):
            entities = []
        cleaned[_ENTITY_FIELDS[field]] = serialize_entities(entities)
    for flag in _FLAG_FIELDS:
        cleaned[flag] = bool(layout.get(flag, cleaned.get(flag, True)))
    return json.dumps(cleaned, ensure_ascii=False)


def _utf16_to_index(value: str, offset: int) -> int:
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


def _render_fragment(value: str, raw_entities: str | None = None) -> str | None:
    """Escape editable text and convert only custom-emoji entities into Rich HTML."""
    entities = deserialize_entities(raw_entities)
    spans: list[tuple[int, int, str]] = []
    for entity in entities:
        if entity.type != "custom_emoji" or not entity.custom_emoji_id:
            return None
        start = _utf16_to_index(value, entity.offset)
        end = _utf16_to_index(value, entity.offset + entity.length)
        if start < 0 or end <= start:
            return None
        spans.append((start, end, entity.custom_emoji_id))

    spans.sort(key=lambda item: item[0])
    parts: list[str] = []
    cursor = 0
    for start, end, emoji_id in spans:
        if start < cursor:
            return None
        parts.append(escape(value[cursor:start]).replace("\n", "<br/>"))
        parts.append(
            f'<tg-emoji emoji-id="{escape(emoji_id, quote=True)}">'
            f'{escape(value[start:end])}</tg-emoji>'
        )
        cursor = end
    parts.append(escape(value[cursor:]).replace("\n", "<br/>"))
    return "".join(parts)


def render_rich_layout(layout: dict[str, Any]) -> str | None:
    """Build Telegram Rich Message HTML from validated layout fields."""
    if not layout.get("enabled", True):
        return None

    pieces: list[str] = []
    if layout.get("show_heading") and layout.get("heading", "").strip():
        fragment = _render_fragment(layout["heading"], layout.get("heading_entities"))
        if fragment is None:
            return None
        pieces.append(f"<h2>{fragment}</h2>")

    if layout.get("body", "").strip():
        fragment = _render_fragment(layout["body"], layout.get("body_entities"))
        if fragment is None:
            return None
        pieces.append(f"<p>{fragment}</p>")

    show_example = bool(layout.get("show_example")) and bool(
        layout.get("example_heading", "").strip() or layout.get("example", "").strip()
    )
    if show_example and layout.get("show_divider") and pieces:
        pieces.append("<hr/>")
    if show_example:
        if layout.get("example_heading", "").strip():
            fragment = _render_fragment(
                layout["example_heading"],
                layout.get("example_heading_entities"),
            )
            if fragment is None:
                return None
            pieces.append(f"<p><b>{fragment}</b></p>")
        if layout.get("example", "").strip():
            fragment = _render_fragment(layout["example"], layout.get("example_entities"))
            if fragment is None:
                return None
            if layout.get("monospace"):
                pieces.append(f"<pre>{fragment}</pre>")
            else:
                pieces.append(f"<p>{fragment}</p>")

    if layout.get("show_footer") and layout.get("footer", "").strip():
        fragment = _render_fragment(layout["footer"], layout.get("footer_entities"))
        if fragment is None:
            return None
        pieces.append(f"<footer>{fragment}</footer>")

    return "".join(pieces) if pieces else None


def rich_layout_plain_text(layout: dict[str, Any]) -> str:
    """Build readable fallback/preview text for the configured visible sections."""
    sections: list[str] = []
    if layout.get("show_heading") and layout.get("heading", "").strip():
        sections.append(layout["heading"])
    if layout.get("body", "").strip():
        sections.append(layout["body"])
    if layout.get("show_example"):
        example = "\n".join(
            value for value in (
                layout.get("example_heading", "").strip(),
                layout.get("example", "").strip(),
            ) if value
        )
        if example:
            sections.append(example)
    if layout.get("show_footer") and layout.get("footer", "").strip():
        sections.append(layout["footer"])
    return "\n\n".join(sections)


def apply_layout_flags(content_layout: dict[str, Any], configured_layout: dict[str, Any]) -> dict[str, Any]:
    """Use localized content with the administrator's chosen display switches."""
    result = dict(content_layout)
    for flag in _FLAG_FIELDS:
        result[flag] = configured_layout.get(flag, result.get(flag, True))
    return result
