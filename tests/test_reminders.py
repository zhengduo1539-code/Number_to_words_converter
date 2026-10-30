from app.keyboards.reminder import reminder_settings_markup
from app.services.i18n import LANGUAGES, text


def test_inactivity_reminder_is_localized_for_every_supported_language():
    rendered = {
        language.code: text("inactive_reminder", language.code)
        for language in LANGUAGES
    }

    assert set(rendered) == {language.code for language in LANGUAGES}
    assert all(message.startswith("🥺") for message in rendered.values())
    assert rendered["en"].startswith("🥺 It's been a while!")
    assert rendered["my"] != rendered["en"]
    assert rendered["zh"] != rendered["en"]


def test_reminder_settings_text_supports_localized_status_values():
    for language in LANGUAGES:
        message = text(
            "reminder_settings",
            language.code,
            status=text("reminder_status_on", language.code),
        )
        assert "{status}" not in message
        assert message


def test_reminder_keyboard_offers_the_opposite_action():
    enabled = reminder_settings_markup(True, "my")
    disabled = reminder_settings_markup(False, "my")

    enabled_button = enabled.inline_keyboard[0][0]
    disabled_button = disabled.inline_keyboard[0][0]

    assert enabled_button.callback_data == "reminder:off"
    assert disabled_button.callback_data == "reminder:on"
