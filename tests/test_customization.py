import json

from aiogram.types import MessageEntity

from app.keyboards.customization import action_type_markup, style_markup
from app.services.emoji_service import (
    deserialize_entities,
    first_custom_emoji_id,
    localize_custom_emoji_entities,
    serialize_entities,
)


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
        "欢迎\n10482 → 一万零四百八十二",
    )

    assert localized == "欢迎\n10482 🎉 → 一万零四百八十二"
    assert localized_entities[0].custom_emoji_id == "12345"
