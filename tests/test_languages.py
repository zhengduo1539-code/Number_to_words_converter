from app.db.models import WelcomeButton
from app.keyboards.buttons import welcome_markup
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


def test_request_language_button_is_localized():
    markup = language_markup("ar")
    request_button = [
        button
        for row in markup.inline_keyboard
        for button in row
        if button.callback_data == "request_language"
    ][0]
    assert request_button.text == "🌐 طلب لغة"



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