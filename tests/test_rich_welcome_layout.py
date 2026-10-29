from aiogram.types import MessageEntity

from app.db.repository import DEFAULT_WELCOME
from app.services.rich_welcome import (
    RICH_LAYOUT_SETTING,
    apply_layout_flags,
    parse_rich_layout,
    render_rich_layout,
    rich_layout_from_text,
    rich_layout_has_unsupported_entities,
    rich_layout_plain_text,
    serialize_rich_layout,
)


def test_default_layout_separates_heading_body_example_and_footer():
    layout = rich_layout_from_text(DEFAULT_WELCOME, [], is_default_welcome=True)

    html = render_rich_layout(layout)

    assert html is not None
    assert html.startswith("<h2>👋 Welcome to Numbers to Words Converter!</h2>")
    assert "<p>Send me any number and I will convert it into English words.</p>" in html
    assert "<hr/>" in html
    assert "<p><b>Example:</b></p>" in html
    assert "<pre>10482 → Ten thousand four hundred eighty-two</pre>" in html
    assert "<footer>Just send a number to get started.</footer>" in html


def test_custom_welcome_stays_whole_body_until_admin_assigns_sections():
    text = "✨ Custom welcome\n\nKeep every existing line."
    layout = rich_layout_from_text(text, [], is_default_welcome=False)

    assert layout["body"] == text
    assert layout["heading"] == ""
    assert layout["show_heading"] is False
    assert layout["show_divider"] is False
    assert layout["show_example"] is False
    assert layout["show_footer"] is False
    assert render_rich_layout(layout) == "<p>✨ Custom welcome<br/><br/>Keep every existing line.</p>"


def test_custom_emoji_is_rendered_as_telegram_rich_emoji():
    text = "🙂 Welcome to the bot"
    entity = MessageEntity(type="custom_emoji", offset=0, length=2, custom_emoji_id="animated-id")
    layout = rich_layout_from_text(text, [entity], is_default_welcome=False)

    html = render_rich_layout(layout)

    assert html is not None
    assert '<tg-emoji emoji-id="animated-id">🙂</tg-emoji>' in html


def test_layout_serialization_round_trips_text_entities_and_switches():
    layout = rich_layout_from_text(DEFAULT_WELCOME, [], is_default_welcome=True)
    layout["heading"] = "✨ New heading"
    layout["show_divider"] = False
    layout["monospace"] = False

    decoded = parse_rich_layout(serialize_rich_layout(layout))

    assert decoded is not None
    assert decoded["heading"] == "✨ New heading"
    assert decoded["show_divider"] is False
    assert decoded["monospace"] is False


def test_layout_escapes_user_provided_html():
    layout = rich_layout_from_text(
        "<Admin> welcome\n\nSend <number>.",
        [],
        is_default_welcome=False,
    )

    html = render_rich_layout(layout)

    assert html == "<p>&lt;Admin&gt; welcome<br/><br/>Send &lt;number&gt;.</p>"


def test_hidden_or_disabled_rich_message_does_not_render():
    layout = rich_layout_from_text(DEFAULT_WELCOME, [], is_default_welcome=True)
    layout["enabled"] = False

    assert render_rich_layout(layout) is None


def test_localized_content_can_use_saved_layout_flags():
    english = rich_layout_from_text(DEFAULT_WELCOME, [], is_default_welcome=True)
    translated = rich_layout_from_text(
        "👋 Bienvenue\n\nEnvoyez un nombre.\n\nExemple:\n12\n\nC'est parti.",
        [],
        is_default_welcome=True,
    )
    english["show_divider"] = False

    result = apply_layout_flags(translated, english)

    assert result["heading"] == "👋 Bienvenue"
    assert result["show_divider"] is False
    assert RICH_LAYOUT_SETTING == "welcome_rich_layout"


def test_unsupported_existing_formatting_is_detected_and_safe_to_fallback():
    text = "Bold welcome"
    entity = MessageEntity(type="bold", offset=0, length=4)
    layout = rich_layout_from_text(text, [entity], is_default_welcome=False)

    assert rich_layout_has_unsupported_entities(layout)
    assert render_rich_layout(layout) is None


def test_layout_plain_text_preview_omits_hidden_sections():
    layout = rich_layout_from_text(DEFAULT_WELCOME, [], is_default_welcome=True)
    layout["show_heading"] = False
    layout["show_example"] = False
    layout["show_footer"] = False

    assert rich_layout_plain_text(layout) == "Send me any number and I will convert it into English words."
