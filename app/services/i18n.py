from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Language:
    code: str
    label: str
    menu_label: str


LANGUAGES: tuple[Language, ...] = (
    Language("en", "American English", "🇺🇸 American English"),
    Language("zh", "Chinese (Simplified)", "🇨🇳 Chinese (Simplified)"),
    Language("my", "Myanmar", "🇲🇲 Myanmar"),
    Language("am", "Amharic", "🇪🇹 Amharic"),
    Language("om", "Afaan Oromo", "🇪🇹 Afaan Oromo"),
    Language("es", "Spanish", "🇪🇸 Spanish"),
    Language("fr", "French", "🇫🇷 French"),
    Language("ru", "Russian", "🇷🇺 Russian"),
)
LANGUAGE_BY_CODE = {item.code: item for item in LANGUAGES}

TEXTS: dict[str, dict[str, str]] = {
    "en": {
        "language_menu": "🌐 Choose your language:",
        "language_changed": "✅ Language changed to {language}.",
        "invalid_number": "Please send a valid number, such as 10482, -125, 10,482, or 10.25.",
        "too_large": "That number is too large or has an unsupported format.",
        "welcome": "👋 Welcome to Numbers to Words Converter!\n\nSend me any number and I will convert it into {language} words.\n\nExample:\n10482 → {example}\n\nJust send a number to get started.",
        "help": "Send a number such as 10482 and I will convert it into words.",
    },
    "zh": {
        "language_menu": "🌐 请选择语言：",
        "language_changed": "✅ 语言已更改为{language}。",
        "invalid_number": "请输入有效数字，例如 10482、-125、10,482 或 10.25。",
        "too_large": "数字太大或格式不受支持。",
        "welcome": "👋 欢迎使用数字转文字机器人！\n\n发送任意数字，我会将其转换为{language}。\n\n示例：\n10482 → {example}\n\n发送数字即可开始。",
        "help": "发送数字（例如 10482），我会将它转换成文字。",
    },
    "my": {
        "language_menu": "🌐 အသုံးပြုလိုသော ဘာသာစကားကို ရွေးပါ။",
        "language_changed": "✅ ဘာသာစကားကို {language} သို့ ပြောင်းပြီးပါပြီ။",
        "invalid_number": "မှန်ကန်သော ဂဏန်းတစ်ခု ပို့ပါ။ ဥပမာ 10482၊ -125၊ 10,482 သို့မဟုတ် 10.25။",
        "too_large": "ဂဏန်းသည် အလွန်ကြီးလွန်းသည် သို့မဟုတ် ပုံစံမထောက်ပံ့ပါ။",
        "welcome": "👋 Numbers to Words Converter မှ ကြိုဆိုပါတယ်။\n\nမည်သည့်ဂဏန်းမဆို ပို့ပါ၊ {language} ဖြင့် စကားလုံးအဖြစ် ပြောင်းပေးပါမယ်။\n\nဥပမာ -\n10482 → {example}\n\nစတင်ရန် ဂဏန်းတစ်ခု ပို့ပါ။",
        "help": "10482 ကဲ့သို့ ဂဏန်းတစ်ခု ပို့ပါ။ စကားလုံးအဖြစ် ပြောင်းပေးပါမယ်။",
    },
    "am": {
        "language_menu": "🌐 ቋንቋዎን ይምረጡ፦",
        "language_changed": "✅ ቋንቋው ወደ {language} ተቀይሯል።",
        "invalid_number": "እባክዎ ትክክለኛ ቁጥር ይላኩ፣ ለምሳሌ 10482፣ -125፣ 10,482 ወይም 10.25።",
        "too_large": "ቁጥሩ በጣም ትልቅ ነው ወይም ቅርጹ አይደገፍም።",
        "welcome": "👋 ወደ Numbers to Words Converter እንኳን በደህና መጡ!\n\nማንኛውንም ቁጥር ይላኩ፣ ወደ {language} ቃላት እቀይረዋለሁ።\n\nምሳሌ፦\n10482 → {example}\n\nለመጀመር ቁጥር ይላኩ።",
        "help": "እንደ 10482 ያለ ቁጥር ይላኩ። ወደ ቃላት እቀይረዋለሁ።",
    },
    "om": {
        "language_menu": "🌐 Afaan itti fayyadamuu barbaaddu filadhu:",
        "language_changed": "✅ Afaan gara {language} tti jijjiirameera.",
        "invalid_number": "Maaloo lakkoofsa sirrii ergi; fakkeenyaaf 10482, -125, 10,482 ykn 10.25.",
        "too_large": "Lakkoofsi kun baayʼee guddaa dha yookaan bifa hin deeggaramne qaba.",
        "welcome": "👋 Gara Numbers to Words Converter dhuftan!\n\nLakkoofsa kamiyyuu ergi; gara jechoota {language} tti nan jijjiira.\n\nFakkeenya:\n10482 → {example}\n\nJalqabuuf lakkoofsa ergi.",
        "help": "Lakkoofsa akka 10482 ergi; gara jechootaatti nan jijjiira.",
    },
    "es": {
        "language_menu": "🌐 Elige tu idioma:",
        "language_changed": "✅ Idioma cambiado a {language}.",
        "invalid_number": "Envía un número válido, por ejemplo 10482, -125, 10,482 o 10.25.",
        "too_large": "El número es demasiado grande o tiene un formato no compatible.",
        "welcome": "👋 ¡Bienvenido a Numbers to Words Converter!\n\nEnvíame cualquier número y lo convertiré a palabras en {language}.\n\nEjemplo:\n10482 → {example}\n\nEnvía un número para comenzar.",
        "help": "Envía un número como 10482 y lo convertiré a palabras.",
    },
    "fr": {
        "language_menu": "🌐 Choisissez votre langue :",
        "language_changed": "✅ Langue changée en {language}.",
        "invalid_number": "Envoyez un nombre valide, par exemple 10482, -125, 10,482 ou 10.25.",
        "too_large": "Ce nombre est trop grand ou son format n’est pas pris en charge.",
        "welcome": "👋 Bienvenue dans Numbers to Words Converter !\n\nEnvoyez-moi un nombre et je le convertirai en mots en {language}.\n\nExemple :\n10482 → {example}\n\nEnvoyez un nombre pour commencer.",
        "help": "Envoyez un nombre comme 10482 et je le convertirai en mots.",
    },
    "ru": {
        "language_menu": "🌐 Выберите язык:",
        "language_changed": "✅ Язык изменён на: {language}.",
        "invalid_number": "Отправьте корректное число, например 10482, -125, 10,482 или 10.25.",
        "too_large": "Число слишком большое или имеет неподдерживаемый формат.",
        "welcome": "👋 Добро пожаловать в Numbers to Words Converter!\n\nОтправьте любое число, и я запишу его словами на языке: {language}.\n\nПример:\n10482 → {example}\n\nОтправьте число, чтобы начать.",
        "help": "Отправьте число, например 10482, и я запишу его словами.",
    },
}


def normalize_language(code: str | None) -> str:
    if not code:
        return "en"
    short_code = code.lower().replace("_", "-").split("-")[0]
    return short_code if short_code in LANGUAGE_BY_CODE else "en"


def language_name(code: str, display_code: str = "en") -> str:
    language = LANGUAGE_BY_CODE.get(normalize_language(code), LANGUAGE_BY_CODE["en"])
    if display_code == "en":
        return language.label
    return language.label


def text(key: str, locale: str = "en", **values: str) -> str:
    locale = normalize_language(locale)
    template = TEXTS.get(locale, TEXTS["en"]).get(key, TEXTS["en"][key])
    return template.format(**values)


def localized_default_welcome(language: str, example: str) -> str:
    language = normalize_language(language)
    return text(
        "welcome",
        language,
        language=LANGUAGE_BY_CODE[language].label,
        example=example,
    )


def without_default_welcome_decoration(value: str) -> str:
    """Remove the default greeting emoji and example arrow from custom text."""
    value = value.replace("👋 ", "", 1)
    return re.sub(r"\s*→\s*", " ", value, count=1)


def localized_custom_welcome(language: str, example: str) -> str:
    """Localize a customized welcome without default decorative symbols.

    A customized message supplies its own animated emoji. The default
    greeting emoji and example arrow are therefore omitted until the admin
    resets the welcome message.
    """
    return without_default_welcome_decoration(
        localized_default_welcome(language, example)
    )