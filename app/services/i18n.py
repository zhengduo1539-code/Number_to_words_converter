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
    Language("bn", "Bengali / Bangla (বাংলা)", "🇧🇩 Bengali / Bangla (বাংলা)"),
    Language("zh", "Chinese (Simplified)", "🇨🇳 Chinese (Simplified)"),
    Language("my", "Myanmar", "🇲🇲 Myanmar"),
    Language("am", "Amharic", "🇪🇹 Amharic"),
    Language("om", "Afaan Oromo", "🇪🇹 Afaan Oromo"),
    Language("es", "Spanish", "🇪🇸 Spanish"),
    Language("fr", "French", "🇫🇷 French"),
    Language("ru", "Russian", "🇷🇺 Russian"),
    Language("ar", "Arabic", "🇸🇦 Arabic"),
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
        "loading": "⏳ Converting your number, please wait...",
        "request_language_button": "🌐 Request Language",
        "request_language_prompt": "Which language would you like to request? You can write the language you wish to request here and send it.",
        "request_language_empty": "Please write the language you would like to request and send it.",
        "request_language_sent": "✅ Your language request has been sent to the administrators.",
        "request_language_failed": "Sorry, your language request could not be sent right now. Please try again later.",
    },
    "bn": {
        "language_menu": "🌐 আপনার ভাষা নির্বাচন করুন:",
        "language_changed": "✅ ভাষা {language}-এ পরিবর্তন করা হয়েছে।",
        "invalid_number": "10482, -125, 10,482 অথবা 10.25-এর মতো একটি সঠিক সংখ্যা পাঠান।",
        "too_large": "সংখ্যাটি অনেক বড় অথবা এই ফরম্যাট সমর্থিত নয়।",
        "welcome": "👋 Numbers to Words Converter-এ স্বাগতম!\n\nযেকোনো সংখ্যা পাঠান, আমি সেটিকে {language} ভাষায় শব্দে রূপান্তর করব।\n\nউদাহরণ:\n10482 → {example}\n\nশুরু করতে একটি সংখ্যা পাঠান।",
        "help": "10482-এর মতো একটি সংখ্যা পাঠান, আমি সেটিকে শব্দে রূপান্তর করব।",
        "loading": "⏳ আপনার সংখ্যাটি রূপান্তর করা হচ্ছে, অনুগ্রহ করে অপেক্ষা করুন...",
        "request_language_button": "🌐 ভাষার অনুরোধ করুন",
        "request_language_prompt": "আপনি কোন ভাষার অনুরোধ করতে চান? যে ভাষাটি যোগ করতে চান তার নাম এখানে লিখে পাঠান।",
        "request_language_empty": "আপনি যে ভাষার অনুরোধ করতে চান তার নাম লিখে পাঠান।",
        "request_language_sent": "✅ আপনার ভাষার অনুরোধ প্রশাসকদের কাছে পাঠানো হয়েছে।",
        "request_language_failed": "দুঃখিত, এই মুহূর্তে আপনার ভাষার অনুরোধ পাঠানো যায়নি। পরে আবার চেষ্টা করুন।",
    },
    "zh": {
        "language_menu": "🌐 请选择语言：",
        "language_changed": "✅ 语言已更改为{language}。",
        "invalid_number": "请输入有效数字，例如 10482、-125、10,482 或 10.25。",
        "too_large": "数字太大或格式不受支持。",
        "welcome": "👋 欢迎使用数字转文字机器人！\n\n发送任意数字，我会将其转换为{language}。\n\n示例：\n10482 → {example}\n\n发送数字即可开始。",
        "help": "发送数字（例如 10482），我会将它转换成文字。",
        "loading": "⏳ 正在转换您的数字，请稍候……",
        "request_language_button": "🌐 请求语言",
        "request_language_prompt": "您想申请哪种语言？您可以在这里写下您希望添加的语言，然后发送给我。",
        "request_language_empty": "请写下您想申请的语言并发送。",
        "request_language_sent": "✅ 您的语言请求已发送给管理员。",
        "request_language_failed": "抱歉，您的语言请求暂时无法发送，请稍后再试。",
    },
    "my": {
        "language_menu": "🌐 အသုံးပြုလိုသော ဘာသာစကားကို ရွေးပါ။",
        "language_changed": "✅ ဘာသာစကားကို {language} သို့ ပြောင်းပြီးပါပြီ။",
        "invalid_number": "မှန်ကန်သော ဂဏန်းတစ်ခု ပို့ပါ။ ဥပမာ 10482၊ -125၊ 10,482 သို့မဟုတ် 10.25။",
        "too_large": "ဂဏန်းသည် အလွန်ကြီးလွန်းသည် သို့မဟုတ် ပုံစံမထောက်ပံ့ပါ။",
        "welcome": "👋 Numbers to Words Converter မှ ကြိုဆိုပါတယ်။\n\nမည်သည့်ဂဏန်းမဆို ပို့ပါ၊ {language} ဖြင့် စကားလုံးအဖြစ် ပြောင်းပေးပါမယ်။\n\nဥပမာ -\n10482 → {example}\n\nစတင်ရန် ဂဏန်းတစ်ခု ပို့ပါ။",
        "help": "10482 ကဲ့သို့ ဂဏန်းတစ်ခု ပို့ပါ။ စကားလုံးအဖြစ် ပြောင်းပေးပါမယ်။",
        "loading": "⏳ သင့်ဂဏန်းကို ပြောင်းနေပါတယ်။ ခဏစောင့်ပေးပါ...",
        "request_language_button": "🌐 ဘာသာစကားတောင်းဆိုမည်",
        "request_language_prompt": "မည်သည့်ဘာသာစကားကို တောင်းဆိုလိုပါသလဲ။ ထည့်သွင်းလိုသော ဘာသာစကားအမည်ကို ဤနေရာတွင် ရေးပြီး ပို့ပါ။",
        "request_language_empty": "တောင်းဆိုလိုသော ဘာသာစကားအမည်ကို ရေးပြီး ပို့ပါ။",
        "request_language_sent": "✅ သင့်ဘာသာစကားတောင်းဆိုချက်ကို စီမံခန့်ခွဲသူများထံ ပို့ပြီးပါပြီ။",
        "request_language_failed": "တောင်းဆိုချက်ကို ယခုမပို့နိုင်သေးပါ။ နောက်မှ ထပ်ကြိုးစားပါ။",
    },
    "am": {
        "language_menu": "🌐 ቋንቋዎን ይምረጡ፦",
        "language_changed": "✅ ቋንቋው ወደ {language} ተቀይሯል።",
        "invalid_number": "እባክዎ ትክክለኛ ቁጥር ይላኩ፣ ለምሳሌ 10482፣ -125፣ 10,482 ወይም 10.25።",
        "too_large": "ቁጥሩ በጣም ትልቅ ነው ወይም ቅርጹ አይደገፍም።",
        "welcome": "👋 ወደ Numbers to Words Converter እንኳን በደህና መጡ!\n\nማንኛውንም ቁጥር ይላኩ፣ ወደ {language} ቃላት እቀይረዋለሁ።\n\nምሳሌ፦\n10482 → {example}\n\nለመጀመር ቁጥር ይላኩ።",
        "help": "እንደ 10482 ያለ ቁጥር ይላኩ። ወደ ቃላት እቀይረዋለሁ።",
        "loading": "⏳ ቁጥርዎን እየቀየርን ነው፣ እባክዎ ይጠብቁ...",
        "request_language_button": "🌐 ቋንቋ ይጠይቁ",
        "request_language_prompt": "የትኛውን ቋንቋ መጠየቅ ይፈልጋሉ? መጠየቅ የሚፈልጉትን ቋንቋ እዚህ ጻፈው ይላኩ።",
        "request_language_empty": "መጠየቅ የሚፈልጉትን ቋንቋ ጻፈው ይላኩ።",
        "request_language_sent": "✅ የቋንቋ ጥያቄዎ ለአስተዳዳሪዎች ተልኳል።",
        "request_language_failed": "የቋንቋ ጥያቄዎ አሁን ሊላክ አልቻለም። እባክዎ ቆይተው ይሞክሩ።",
    },
    "om": {
        "language_menu": "🌐 Afaan itti fayyadamuu barbaaddu filadhu:",
        "language_changed": "✅ Afaan gara {language} tti jijjiirameera.",
        "invalid_number": "Maaloo lakkoofsa sirrii ergi; fakkeenyaaf 10482, -125, 10,482 ykn 10.25.",
        "too_large": "Lakkoofsi kun baayʼee guddaa dha yookaan bifa hin deeggaramne qaba.",
        "welcome": "👋 Gara Numbers to Words Converter dhuftan!\n\nLakkoofsa kamiyyuu ergi; gara jechoota {language} tti nan jijjiira.\n\nFakkeenya:\n10482 → {example}\n\nJalqabuuf lakkoofsa ergi.",
        "help": "Lakkoofsa akka 10482 ergi; gara jechootaatti nan jijjiira.",
        "loading": "⏳ Lakkoofsa kee jijjiiraa jira, maaloo xiqqoo eegi...",
        "request_language_button": "🌐 Afaan gaafadhu",
        "request_language_prompt": "Afaan kamiin gaafachuu barbaadda? Afaan gaafachuu barbaaddu as irratti barreessii ergi.",
        "request_language_empty": "Maaloo afaan gaafachuu barbaaddu barreessii ergi.",
        "request_language_sent": "✅ Gaaffiin afaanii kee bulchitootatti ergameera.",
        "request_language_failed": "Dhiifama, gaaffiin afaanii kee amma ergamee hin jiru. Mee booda irra deebi'ii yaali.",
    },
    "es": {
        "language_menu": "🌐 Elige tu idioma:",
        "language_changed": "✅ Idioma cambiado a {language}.",
        "invalid_number": "Envía un número válido, por ejemplo 10482, -125, 10,482 o 10.25.",
        "too_large": "El número es demasiado grande o tiene un formato no compatible.",
        "welcome": "👋 ¡Bienvenido a Numbers to Words Converter!\n\nEnvíame cualquier número y lo convertiré a palabras en {language}.\n\nEjemplo:\n10482 → {example}\n\nEnvía un número para comenzar.",
        "help": "Envía un número como 10482 y lo convertiré a palabras.",
        "loading": "⏳ Convirtiendo tu número, espera un momento...",
        "request_language_button": "🌐 Solicitar idioma",
        "request_language_prompt": "¿Qué idioma te gustaría solicitar? Escribe aquí el idioma que deseas solicitar y envíalo.",
        "request_language_empty": "Escribe el idioma que deseas solicitar y envíalo.",
        "request_language_sent": "✅ Tu solicitud de idioma se ha enviado a los administradores.",
        "request_language_failed": "Lo sentimos, tu solicitud de idioma no se pudo enviar ahora. Inténtalo más tarde.",
    },
    "fr": {
        "language_menu": "🌐 Choisissez votre langue :",
        "language_changed": "✅ Langue changée en {language}.",
        "invalid_number": "Envoyez un nombre valide, par exemple 10482, -125, 10,482 ou 10.25.",
        "too_large": "Ce nombre est trop grand ou son format n’est pas pris en charge.",
        "welcome": "👋 Bienvenue dans Numbers to Words Converter !\n\nEnvoyez-moi un nombre et je le convertirai en mots en {language}.\n\nExemple :\n10482 → {example}\n\nEnvoyez un nombre pour commencer.",
        "help": "Envoyez un nombre comme 10482 et je le convertirai en mots.",
        "loading": "⏳ Conversion de votre nombre, veuillez patienter...",
        "request_language_button": "🌐 Demander une langue",
        "request_language_prompt": "Quelle langue souhaitez-vous demander ? Écrivez ici la langue que vous souhaitez demander et envoyez-la.",
        "request_language_empty": "Écrivez la langue que vous souhaitez demander et envoyez-la.",
        "request_language_sent": "✅ Votre demande de langue a été envoyée aux administrateurs.",
        "request_language_failed": "Désolé, votre demande de langue n’a pas pu être envoyée. Veuillez réessayer plus tard.",
    },
    "ru": {
        "language_menu": "🌐 Выберите язык:",
        "language_changed": "✅ Язык изменён на: {language}.",
        "invalid_number": "Отправьте корректное число, например 10482, -125, 10,482 или 10.25.",
        "too_large": "Число слишком большое или имеет неподдерживаемый формат.",
        "welcome": "👋 Добро пожаловать в Numbers to Words Converter!\n\nОтправьте любое число, и я запишу его словами на языке: {language}.\n\nПример:\n10482 → {example}\n\nОтправьте число, чтобы начать.",
        "help": "Отправьте число, например 10482, и я запишу его словами.",
        "loading": "⏳ Преобразую ваше число, пожалуйста, подождите...",
        "request_language_button": "🌐 Запросить язык",
        "request_language_prompt": "Какой язык вы хотели бы запросить? Напишите здесь язык, который хотите добавить, и отправьте сообщение.",
        "request_language_empty": "Напишите язык, который хотите запросить, и отправьте сообщение.",
        "request_language_sent": "✅ Ваш запрос языка отправлен администраторам.",
        "request_language_failed": "Извините, сейчас не удалось отправить ваш запрос. Попробуйте позже.",
    },
    "ar": {
        "language_menu": "🌐 اختر لغتك:",
        "language_changed": "✅ تم تغيير اللغة إلى {language}.",
        "invalid_number": "أرسل رقمًا صحيحًا، مثل 10482 أو -125 أو 10,482 أو 10.25.",
        "too_large": "الرقم كبير جدًا أو تنسيقه غير مدعوم.",
        "welcome": "👋 مرحبًا بك في محول الأرقام إلى كلمات!\n\nأرسل أي رقم وسأحوله إلى كلمات باللغة {language}.\n\nمثال:\n10482 → {example}\n\nأرسل رقمًا للبدء.",
        "help": "أرسل رقمًا مثل 10482 وسأحوله إلى كلمات.",
        "loading": "⏳ جارٍ تحويل الرقم، يرجى الانتظار...",
        "request_language_button": "🌐 طلب لغة",
        "request_language_prompt": "ما اللغة التي تود طلبها؟ يمكنك كتابة اللغة التي ترغب في طلبها هنا وإرسالها.",
        "request_language_empty": "اكتب اللغة التي ترغب في طلبها وأرسلها.",
        "request_language_sent": "✅ تم إرسال طلب اللغة إلى المسؤولين.",
        "request_language_failed": "عذرًا، تعذر إرسال طلب اللغة الآن. يرجى المحاولة لاحقًا.",
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


def without_default_language_decoration(key: str, value: str) -> str:
    """Remove the default leading symbol when a custom message supplies one."""
    symbol = {
        "language_menu": "🌐",
        "language_changed": "✅",
    }.get(key)
    if symbol:
        value = value.replace(f"{symbol} ", "", 1)
    return value


def localized_custom_language_text(
    key: str,
    locale: str,
    custom_text: str,
    **values: str,
) -> str:
    """Return a localized custom language message without default decoration."""
    locale = normalize_language(locale)
    localized = custom_text if locale == "en" else text(key, locale, **values)
    return without_default_language_decoration(key, localized)


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