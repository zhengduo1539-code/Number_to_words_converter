import json

from aiogram.types import MessageEntity

from app.keyboards.customization import action_type_markup, style_markup
from app.services.emoji_service import (
    deserialize_entities,
    first_custom_emoji_id,
    localize_custom_emoji_entities,
    remove_custom_emoji_text,
    serialize_entities,
)
from app.services.i18n import localized_custom_welcome, without_default_welcome_decoration


def test_custom_emoji_entities_round_trip():
    entities = [MessageEntity(type="custom_emoji", offset=0, length=1, custom_emoji_id="12345")]
    encoded = serialize_entities(entities)
    assert json.loads(encoded)[0]["custom_emoji_id"] == "12345"
    decoded = deserialize_entities(encoded)
    assert first_custom_emoji_id(decoded) == "12345"


def test_welcome_button_type_menu_includes_share_button():
    buttons = [
        button
        for row in action_type_markup().inline_keyboard
        for button in row
    ]
    assert any(button.callback_data == "ctm:wb_type:share" for button in buttons)


def test_style_buttons_use_callback_shape_handled_by_customization_router():
    buttons = [
        button
        for row in style_markup("ctm:wb").inline_keyboard
        for button in row
    ]
    assert {button.callback_data for button in buttons[:3]} == {
        "ctm:wb:style:primary",
        "ctm:wb:style:success",
        "ctm:wb:style:danger",
    }


def test_localized_welcome_preserves_animated_emoji_entity():
    source = "Welcome\n10482 🎉 Ten thousand"
    entities = [MessageEntity(type="custom_emoji", offset=14, length=2, custom_emoji_id="12345")]

    localized, localized_entities = localize_custom_emoji_entities(
        source,
        entities,
        localized_custom_welcome("zh", "一万零四百八十二"),
    )

    assert "👋" not in localized
    assert "→" not in localized
    assert "🎉" in localized
    assert localized_entities[0].custom_emoji_id == "12345"


def test_custom_welcome_removes_default_emoji_and_arrow_until_reset():
    assert without_default_welcome_decoration("👋 Hello\n10482 → Ten thousand") == (
        "Hello\n10482 Ten thousand"
    )


def test_custom_emoji_placeholder_is_not_duplicated_in_english_welcome():
    source = "👋 Welcome\n➡️ Send me a number"
    entities = [
        MessageEntity(type="custom_emoji", offset=0, length=2, custom_emoji_id="hand"),
        MessageEntity(type="custom_emoji", offset=11, length=2, custom_emoji_id="arrow"),
    ]
    target = without_default_welcome_decoration(
        remove_custom_emoji_text(source, entities)
    )
    localized, localized_entities = localize_custom_emoji_entities(
        source,
        entities,
        target,
    )

    assert localized == "👋 Welcome\n➡️ Send me a number"
    assert len(localized_entities) == 2


def test_multiple_custom_emojis_keep_their_order_after_placeholder_removal():
    source = "➡️👉 Send me a number"
    entities = [
        MessageEntity(type="custom_emoji", offset=0, length=2, custom_emoji_id="arrow"),
        MessageEntity(type="custom_emoji", offset=2, length=2, custom_emoji_id="point"),
    ]
    localized, _ = localize_custom_emoji_entities(
        source,
        entities,
        remove_custom_emoji_text(source, entities),
    )

    assert localized == source
