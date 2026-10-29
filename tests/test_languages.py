from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.db.models import WelcomeButton
from app.handlers import language as language_handler
from app.keyboards.buttons import welcome_markup
from app.keyboards.customization import language_messages_markup, language_selection_buttons_markup
from app.keyboards.language import language_markup
from app.services.i18n import (
    LANGUAGES,
    localized_custom_language_text,
    normalize_language,
    text,
    without_default_language_decoration,
)
from app.services.number_converter import number_to_words


def test_all_language_buttons_use_success_style():
    markup = language_markup()
    buttons = [button for row in markup.inline_keyboard for button in row]
    language_buttons = [button for button in buttons if button.callback_data.startswith("lang:")]
    request_buttons = [button for button in buttons if button.callback_data == "request_language"]
    assert len(language_buttons) == len(LANGUAGES)
    assert {button.style for button in language_buttons} == {"success"}
    assert len(request_buttons) == 1
    assert request_buttons[0].style == "primary"


def test_language_markup_applies_per_language_custom_emoji_icons():
    custom_icons = {"si": "custom-emoji-si", "ta": "custom-emoji-ta"}
    markup = language_markup("en", custom_icons)
    buttons = {
        button.callback_data: button
        for row in markup.inline_keyboard
        for button in row
        if button.callback_data and button.callback_data.startswith("lang:")
    }

    assert buttons["lang:si"].icon_custom_emoji_id == "custom-emoji-si"
    assert buttons["lang:ta"].icon_custom_emoji_id == "custom-emoji-ta"
    assert buttons["lang:en"].icon_custom_emoji_id is None
    assert len(buttons) == len(LANGUAGES)


def test_language_button_customization_menu_covers_every_language():
    custom_icons = {"si": "custom-emoji-si"}
    markup = language_selection_buttons_markup(custom_icons)
    buttons = [button for row in markup.inline_keyboard for button in row]
    language_buttons = {
        button.callback_data: button
        for button in buttons
        if button.callback_data and button.callback_data.startswith("ctm:language_button:")
    }

    assert set(language_buttons) == {
        f"ctm:language_button:{language.code}" for language in LANGUAGES
    }
    assert language_buttons["ctm:language_button:si"].text.startswith("✅ ")
    assert not language_buttons["ctm:language_button:ta"].text.startswith("✅ ")
    assert any(button.callback_data == "ctm:language_buttons_reset" for button in buttons)


def test_request_language_button_is_localized():
    markup = language_markup("ar")
    request_button = [
        button
        for row in markup.inline_keyboard
        for button in row
        if button.callback_data == "request_language"
    ][0]
    assert request_button.text == "🌐 طلب لغة"




def test_language_messages_customization_includes_request_prompt_and_confirmation():
    markup = language_messages_markup()
    callbacks = {
        button.callback_data
        for row in markup.inline_keyboard
        for button in row
    }

    assert "ctm:request_language_prompt_edit" in callbacks
    assert "ctm:request_language_prompt_reset" in callbacks
    assert "ctm:request_language_sent_edit" in callbacks
    assert "ctm:request_language_sent_reset" in callbacks


@pytest.mark.parametrize(
    ("setting_prefix", "message_key", "custom_text"),
    [
        ("request_language_prompt", "request_language_prompt", "✨ Tell us the language to add."),
        ("request_language_sent", "request_language_sent", "✅ Your request is now with the team."),
    ],
)
async def test_request_language_custom_messages_are_used_for_english(
    monkeypatch,
    setting_prefix,
    message_key,
    custom_text,
):
    session = object()
    callback = SimpleNamespace(
        from_user=SimpleNamespace(id=12345),
        answer=AsyncMock(),
        message=SimpleNamespace(answer=AsyncMock()),
    )
    state = SimpleNamespace(set_state=AsyncMock())

    async def current_language(_session, _user_id):
        return "en"

    async def get_setting(_session, key, default=""):
        values = {
            f"{setting_prefix}_text": custom_text,
            f"{setting_prefix}_entities": "[]",
        }
        return values.get(key, default)

    monkeypatch.setattr(language_handler, "_current_language", current_language)
    monkeypatch.setattr(language_handler, "get_setting", get_setting)

    if message_key == "request_language_prompt":
        await language_handler.request_language_callback(callback, session, state)
        callback.message.answer.assert_awaited_once_with(custom_text, entities=None)
    else:
        message = SimpleNamespace(
            text="Spanish",
            from_user=SimpleNamespace(id=12345, first_name="Tester", username="tester"),
            answer=AsyncMock(),
        )
        state.clear = AsyncMock()
        bot = SimpleNamespace(send_message=AsyncMock())
        settings = SimpleNamespace(admin_ids=[999])
        await language_handler.request_language_message(
            message,
            state,
            session,
            settings,
            bot,
        )
        message.answer.assert_awaited_once_with(custom_text.removeprefix("✅ "), entities=None)
        state.clear.assert_awaited_once()
        bot.send_message.assert_awaited_once()


def test_custom_request_sent_confirmation_removes_default_checkmark_for_translations():
    from app.services.i18n import localized_custom_language_text

    custom = "✅ Thanks, we received your request."
    localized = localized_custom_language_text("request_language_sent", "my", custom)
    assert not localized.startswith("✅ ")
    assert localized == text("request_language_sent", "my")


def test_share_button_falls_back_to_english_for_sinhala_and_tamil():
    share_button = WelcomeButton(label="🔗 Share Bot", button_type="share")

    for language in ("si", "ta"):
        markup = welcome_markup([share_button], "example_bot", language)
        button = markup.inline_keyboard[0][0]
        assert button.text == "🔗 Share Bot"
        assert button.url == (
            "https://t.me/share/url?url=https://t.me/example_bot"
            "&text=Try%20Numbers%20to%20Words%20Converter"
        )



@pytest.mark.parametrize("language", ["si", "ta"])
async def test_language_selection_removes_menu_buttons_and_sends_welcome(
    monkeypatch,
    language,
):
    session = object()
    bot = object()
    message = SimpleNamespace(
        edit_reply_markup=AsyncMock(),
        edit_text=AsyncMock(),
    )
    callback = SimpleNamespace(
        data=f"lang:{language}",
        from_user=SimpleNamespace(id=12345),
        message=message,
        answer=AsyncMock(),
    )
    set_language = AsyncMock()
    send_welcome = AsyncMock()

    async def get_empty_setting(_session, _key, default=""):
        return ""

    monkeypatch.setattr(language_handler, "set_user_language", set_language)
    monkeypatch.setattr(language_handler, "get_setting", get_empty_setting)
    monkeypatch.setattr(language_handler, "send_welcome", send_welcome)

    await language_handler.language_callback(callback, session, bot)

    message.edit_reply_markup.assert_awaited_once_with(reply_markup=None)
    message.edit_text.assert_awaited_once()
    assert "reply_markup" not in message.edit_text.await_args.kwargs
    send_welcome.assert_awaited_once_with(message, session, bot, language)


def test_supported_language_outputs():
    expected = {
        "en": "Ten thousand four hundred eighty-two",
        "bn": "দশ হাজার চারশ বিরাশি",
        "zh": "一万零四百八十二",
        "my": "တစ်သောင်း လေးရာ ရှစ်ဆယ့်နှစ်",
        "am": "አስር ሺህ አራት መቶ ሰማንያ ሁለት",
        "am_latn": "asir shih arat meto semanya hulet",
        "si": "දහය දහස් හාරසිය අසූ දෙක",
        "ta": "பத்து ஆயிரம் நானூற்று எண்பத்து இரண்டு",
        "om": "kudhan kuma fi afur dhibba fi saddeetama fi lama",
        "es": "diez mil cuatrocientos ochenta y dos",
        "fr": "dix mille quatre cent quatre-vingt-deux",
        "ru": "десять тысяч четыреста восемьдесят два",
        "ar": "عشرة آلاف وأربعمائة واثنان وثمانون",
    }
    for language, result in expected.items():
        assert number_to_words("10482", language) == result


def test_language_normalization_and_localized_messages():
    assert normalize_language("zh-CN") == "zh"
    assert normalize_language("bn-BD") == "bn"
    assert normalize_language("am-Latn") == "am_latn"
    assert normalize_language("am_latn") == "am_latn"
    assert normalize_language("si-LK") == "si"
    assert normalize_language("ta-IN") == "ta"
    assert normalize_language("unknown") == "en"
    assert "10482" in text("invalid_number", "my")
    assert text("loading", "my") != text("loading", "en")
    assert text("loading", "bn") != text("loading", "en")
    assert "Tiqurwon" in text("loading", "am-Latn")
    assert text("loading", "si") != text("loading", "en")
    assert text("loading", "ta") != text("loading", "en")
    assert any(language.code == "si" and language.label == "Sinhala (සිංහල)" for language in LANGUAGES)
    assert any(language.code == "ta" and language.label == "Tamil (தமிழ்)" for language in LANGUAGES)


def test_custom_language_messages_localize_and_remove_default_symbol():
    custom = "🌐 🎉 Choose your language:"
    assert localized_custom_language_text("language_menu", "zh", custom) == "请选择语言："
    assert localized_custom_language_text("language_menu", "en", custom) == "🎉 Choose your language:"
    assert without_default_language_decoration("language_changed", "✅ 🎉 Language changed") == "🎉 Language changed"
    assert without_default_language_decoration("loading", text("loading", "zh")) == (
        "正在转换您的数字，请稍候……"
    )