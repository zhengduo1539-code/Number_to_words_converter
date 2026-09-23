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
    assert len(buttons) == len(LANGUAGES)
    assert {button.style for button in buttons} == {"success"}


def test_supported_language_outputs():
    expected = {
        "en": "Ten thousand four hundred eighty-two",
        "zh": "一万零四百八十二",
        "my": "တစ်သောင်း လေးရာ ရှစ်ဆယ့်နှစ်",
        "am": "አስር ሺህ አራት መቶ ሰማንያ ሁለት",
        "om": "kudhan kuma fi afur dhibba fi saddeetama fi lama",
        "es": "diez mil cuatrocientos ochenta y dos",
        "fr": "dix mille quatre cent quatre-vingt-deux",
        "ru": "десять тысяч четыреста восемьдесят два",
    }
    for language, result in expected.items():
        assert number_to_words("10482", language) == result


def test_language_normalization_and_localized_messages():
    assert normalize_language("zh-CN") == "zh"
    assert normalize_language("unknown") == "en"
    assert "10482" in text("invalid_number", "my")


def test_custom_language_messages_localize_and_remove_default_symbol():
    custom = "🌐 🎉 Choose your language:"
    assert localized_custom_language_text("language_menu", "zh", custom) == "请选择语言："
    assert localized_custom_language_text("language_menu", "en", custom) == "🎉 Choose your language:"
    assert without_default_language_decoration("language_changed", "✅ 🎉 Language changed") == "🎉 Language changed"