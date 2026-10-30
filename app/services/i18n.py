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
    Language("am_latn", "Amharic (Latin)", "🇪🇹 Amharic (Latin)"),
    Language("si", "Sinhala (සිංහල)", "🇱🇰 Sinhala (සිංහල)"),
    Language("ta", "Tamil (தமிழ்)", "🇮🇳 Tamil (தமிழ்)"),
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
    "am_latn": {
        "language_menu": "🌐 Qwanqwaown yimeritu:",
        "language_changed": "✅ Qwanqaw we-de {language} teqeyirwal.",
        "invalid_number": "Ibakwo tikiklegna tiqur yelaku, lemesale 10482, -125, 10,482 weym 10.25.",
        "too_large": "Tiqur-u betam tilik new weym qirts-u ayidegimim.",
        "welcome": "👋 We-de Numbers to Words Converter enqwan dehna metu!\n\nManinyawim tiqur yisaku, we-de {language} qalat e-keyiralehu.\n\nMisema:\n10482 → {example}\n\nLe-mejemer tiqur yisaku.",
        "help": "Ende 10482 yale tiqur yisaku, we-de qalat e-keyiralehu.",
        "loading": "⏳ Tiqurwon e-keyirn new, ibakwo yitebeku...",
        "request_language_button": "🌐 Qwanqwa yiqu",
        "request_language_prompt": "Min aynet qwanqwa meteyek felgale? Ezi yemitayekutn qwanqwa sim yikef.",
        "request_language_empty": "Yemitayekutn qwanqwa sim yikef ena yisak.",
        "request_language_sent": "✅ Yeqwanqwa tekiqaw le-areditoroch tesetwal.",
        "request_language_failed": "Yikirta, yeqwanqwa tekiqaw bemitayekut gize mayiset alchalkum. Kezi behwala yimokeru.",
    },
    "si": {
        "language_menu": "🌐 ඔබේ භාෂාව තෝරන්න:",
        "language_changed": "✅ භාෂාව {language} ලෙස වෙනස් කළා.",
        "invalid_number": "කරුණාකර 10482, -125, 10,482 හෝ 10.25 වැනි නිවැරදි අංකයක් යවන්න.",
        "too_large": "එම අංකය ඉතා විශාලයි හෝ මෙම ආකෘතිය සහාය නොදක්වයි.",
        "welcome": "👋 Numbers to Words Converter වෙත සාදරයෙන් පිළිගනිමු!\n\nඕනෑම අංකයක් එවන්න. එය {language} වචනවලට පරිවර්තනය කර දෙන්නම්.\n\nඋදාහරණය:\n10482 → {example}\n\nආරම්භ කිරීමට අංකයක් යවන්න.",
        "help": "10482 වැනි අංකයක් යවන්න. එය වචනවලට පරිවර්තනය කර දෙන්නම්.",
        "loading": "⏳ ඔබේ අංකය පරිවර්තනය කරමින් පවතී. කරුණාකර රැඳී සිටින්න...",
        "request_language_button": "🌐 භාෂාවක් ඉල්ලන්න",
        "request_language_prompt": "ඔබ ඉල්ලා සිටීමට කැමති භාෂාව කුමක්ද? එක් කිරීමට අවශ්‍ය භාෂාවේ නම මෙහි ලියා යවන්න.",
        "request_language_empty": "කරුණාකර ඉල්ලා සිටීමට අවශ්‍ය භාෂාවේ නම ලියා යවන්න.",
        "request_language_sent": "✅ ඔබේ භාෂා ඉල්ලීම පරිපාලකයන්ට යවා ඇත.",
        "request_language_failed": "සමාවන්න, මේ මොහොතේ ඔබේ භාෂා ඉල්ලීම යැවිය නොහැක. පසුව නැවත උත්සාහ කරන්න.",
    },
    "ta": {
        "language_menu": "🌐 உங்கள் மொழியைத் தேர்ந்தெடுக்கவும்:",
        "language_changed": "✅ மொழி {language} ஆக மாற்றப்பட்டது.",
        "invalid_number": "10482, -125, 10,482 அல்லது 10.25 போன்ற சரியான எண்ணை அனுப்பவும்.",
        "too_large": "அந்த எண் மிகவும் பெரியது அல்லது ஆதரிக்கப்படாத வடிவத்தில் உள்ளது.",
        "welcome": "👋 Numbers to Words Converter-க்கு வரவேற்கிறோம்!\n\nஎந்த எண்ணையும் அனுப்புங்கள்; அதை {language} சொற்களாக மாற்றித் தருகிறேன்.\n\nஎடுத்துக்காட்டு:\n10482 → {example}\n\nதொடங்க ஓர் எண்ணை அனுப்புங்கள்.",
        "help": "10482 போன்ற எண்ணை அனுப்புங்கள்; அதைச் சொற்களாக மாற்றித் தருகிறேன்.",
        "loading": "⏳ உங்கள் எண்ணை வார்த்தைகளாக மாற்றுகிறேன். தயவுசெய்து காத்திருக்கவும்...",
        "request_language_button": "🌐 மொழியைக் கோருங்கள்",
        "request_language_prompt": "நீங்கள் எந்த மொழியைக் கோர விரும்புகிறீர்கள்? சேர்க்க விரும்பும் மொழியின் பெயரை இங்கே எழுதி அனுப்புங்கள்.",
        "request_language_empty": "கோர விரும்பும் மொழியின் பெயரை எழுதி அனுப்புங்கள்.",
        "request_language_sent": "✅ உங்கள் மொழி கோரிக்கை நிர்வாகிகளுக்கு அனுப்பப்பட்டது.",
        "request_language_failed": "மன்னிக்கவும், இப்போது உங்கள் மொழி கோரிக்கையை அனுப்ப முடியவில்லை. பின்னர் மீண்டும் முயற்சிக்கவும்.",
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


# Reminder messages are kept separate from the main UI catalogue so this
# feature can be added without changing existing translations.
REMINDER_TEXTS: dict[str, dict[str, str]] = {
    "en": {
        "inactive_reminder": "🥺 It's been a while! We miss having you around.\n\nNeed to convert a number into English words? Your Number To Words Converter is always here to help! ✨\n\nWhether it's a small number or a large one, just send it over and get the written form instantly.\n\n💡 Come back anytime and make number conversion effortless!\n\n🔢 Send a number to get started.",
        "reminder_settings": "🔔 Inactive reminders: {status}\n\nIf you don't use the bot for 7 days, I'll send one friendly reminder. You can change this setting anytime.",
        "reminder_status_on": "ON",
        "reminder_status_off": "OFF",
        "reminder_turn_on": "🔔 Turn reminders on",
        "reminder_turn_off": "🔕 Turn reminders off",
        "reminder_private_only": "Please use /reminder in a private chat with the bot.",
    },
    "bn": {
        "inactive_reminder": "🥺 অনেক দিন হলো! আপনাকে এখানে না দেখে আমাদেরও খারাপ লাগছে।\n\nকোনো সংখ্যাকে ইংরেজি শব্দে রূপান্তর করতে হবে? আপনার Number To Words Converter সবসময় সাহায্যের জন্য প্রস্তুত! ✨\n\nছোট বা বড়—যেকোনো সংখ্যা পাঠান, মুহূর্তেই তার কথায় লেখা রূপ পেয়ে যাবেন।\n\n💡 যেকোনো সময় ফিরে আসুন এবং সহজেই সংখ্যা রূপান্তর করুন!\n\n🔢 শুরু করতে একটি সংখ্যা পাঠান।",
        "reminder_settings": "🔔 নিষ্ক্রিয়তার রিমাইন্ডার: {status}\n\nআপনি টানা ৭ দিন বট ব্যবহার না করলে একটি বন্ধুত্বপূর্ণ রিমাইন্ডার পাঠানো হবে। আপনি যেকোনো সময় এই সেটিং পরিবর্তন করতে পারেন।",
        "reminder_status_on": "চালু",
        "reminder_status_off": "বন্ধ",
        "reminder_turn_on": "🔔 রিমাইন্ডার চালু করুন",
        "reminder_turn_off": "🔕 রিমাইন্ডার বন্ধ করুন",
        "reminder_private_only": "অনুগ্রহ করে বটের সঙ্গে ব্যক্তিগত চ্যাটে /reminder ব্যবহার করুন।",
    },
    "zh": {
        "inactive_reminder": "🥺 好久不见！我们很想念您。\n\n需要把数字转换成英文单词吗？您的 Number To Words Converter 随时为您提供帮助！✨\n\n无论数字大小，只需发送数字，即可立即获得英文拼写。\n\n💡 欢迎随时回来，让数字转换变得轻松简单！\n\n🔢 发送一个数字即可开始。",
        "reminder_settings": "🔔 闲置提醒：{status}\n\n如果您连续 7 天没有使用机器人，我们会发送一条友好的提醒。您可以随时更改此设置。",
        "reminder_status_on": "开启",
        "reminder_status_off": "关闭",
        "reminder_turn_on": "🔔 开启提醒",
        "reminder_turn_off": "🔕 关闭提醒",
        "reminder_private_only": "请在与机器人的私聊中使用 /reminder。",
    },
    "my": {
        "inactive_reminder": "🥺 မတွေ့ရတာ ကြာပြီနော်။ သင့်ကို ပြန်တွေ့ရဖို့ မျှော်လင့်နေပါတယ်။\n\nဂဏန်းတစ်ခုကို English စကားလုံးအဖြစ် ပြောင်းချင်ပါသလား။ သင့် Number To Words Converter က အမြဲကူညီဖို့ အသင့်ရှိပါတယ်။ ✨\n\nဂဏန်းသေးသေးလေးဖြစ်စေ၊ ဂဏန်းကြီးကြီးဖြစ်စေ ပို့လိုက်ရုံနဲ့ အင်္ဂလိပ်စာလုံးဖြင့် ရေးသားထားသည့်ပုံစံကို ချက်ချင်းရရှိနိုင်ပါတယ်။\n\n💡 အချိန်မရွေး ပြန်လာပြီး ဂဏန်းပြောင်းလဲခြင်းကို လွယ်ကူစွာ လုပ်ဆောင်လိုက်ပါ။\n\n🔢 စတင်ရန် ဂဏန်းတစ်ခု ပို့လိုက်ပါ။",
        "reminder_settings": "🔔 အသုံးမပြုသည့်အချိန် Reminder: {status}\n\nBot ကို ၇ ရက်ဆက်တိုက် အသုံးမပြုပါက သတိပေးစာတစ်စောင် ပို့ပေးပါမယ်။ ဒီ setting ကို အချိန်မရွေး ပြောင်းလဲနိုင်ပါတယ်။",
        "reminder_status_on": "ဖွင့်ထားသည်",
        "reminder_status_off": "ပိတ်ထားသည်",
        "reminder_turn_on": "🔔 Reminder ဖွင့်မည်",
        "reminder_turn_off": "🔕 Reminder ပိတ်မည်",
        "reminder_private_only": "Bot နှင့် Private Chat ထဲတွင် /reminder ကို အသုံးပြုပေးပါ။",
    },
    "am": {
        "inactive_reminder": "🥺 ቆይተናል! እዚህ እንደገና ብንገናኝ ደስ ይለናል።\n\nቁጥርን ወደ እንግሊዝኛ ቃላት መቀየር ይፈልጋሉ? የእርስዎ Number To Words Converter ሁልጊዜ ሊረዳዎ ዝግጁ ነው! ✨\n\nትንሽም ሆነ ትልቅ ቁጥር ብቻ ይላኩ፤ በቅጽበት በቃላት የተጻፈውን ቅጽ ያገኛሉ።\n\n💡 በማንኛውም ጊዜ ይመለሱና ቁጥሮችን በቀላሉ ይቀይሩ!\n\n🔢 ለመጀመር ቁጥር ይላኩ።",
        "reminder_settings": "🔔 የእንቅስቃሴ ማስታወሻ፦ {status}\n\nቦቱን ለ7 ቀናት ካልተጠቀሙ አንድ ወዳጃዊ ማስታወሻ እንልካለን። ይህን ቅንብር በማንኛውም ጊዜ መቀየር ይችላሉ።",
        "reminder_status_on": "በርቷል",
        "reminder_status_off": "ጠፍቷል",
        "reminder_turn_on": "🔔 ማስታወሻዎችን አብራ",
        "reminder_turn_off": "🔕 ማስታወሻዎችን አጥፋ",
        "reminder_private_only": "እባክዎ /reminder ን ከቦቱ ጋር በግል ውይይት ይጠቀሙ።",
    },
    "am_latn": {
        "inactive_reminder": "🥺 Zare gize gize tebkew new! Yedegnineten madreg enwedalen.\n\nTiqur be-English qalat lemafek yetifelgal? Yene Number To Words Converter be-gizew lay yemiyadergawen megbar yichilal! ✨\n\nTinishim honé tilik tiqur yisaku; be-qitshet be-qalat yemiteqeterewun tikikil yegagnalu.\n\n💡 Betamen gize deji yetebequt; tiqurochen be-qelalu yikebdu!\n\n🔢 Lemijemer tiqur yisaku.",
        "reminder_settings": "🔔 Ye-inekasiseke masteyawesha: {status}\n\nBotun le-7 qenat kalte-semetu, and wedajawi masteyawesha enilakel. Yihen qenqen be-manchawm gize mekeyer yichilalu.",
        "reminder_status_on": "Belitwal",
        "reminder_status_off": "Tefital",
        "reminder_turn_on": "🔔 Masteyaweshawochin abera",
        "reminder_turn_off": "🔕 Masteyaweshawochin atfa",
        "reminder_private_only": "Ibakwo /reminder-n be-private chat ke-bot gar yiteku.",
    },
    "si": {
        "inactive_reminder": "🥺 ඔබව දැකලා කාලයක් ගතවුණා! ඔබ නැවත එනතුරු අපි බලා සිටියා.\n\nඔබට අංකයක් ඉංග්‍රීසි වචනවලට පරිවර්තනය කරගන්න අවශ්‍යද? ඔබේ Number To Words Converter උදව් කිරීමට සැමවිටම සූදානම්! ✨\n\nකුඩා හෝ විශාල ඕනෑම අංකයක් එවන්න. එහි වචන ආකාරය ක්ෂණිකව ලබාගන්න.\n\n💡 ඕනෑම වේලාවක නැවත පැමිණ අංක පරිවර්තනය පහසු කරගන්න!\n\n🔢 ආරම්භ කිරීමට අංකයක් එවන්න.",
        "reminder_settings": "🔔 අක්‍රියතා මතක් කිරීම: {status}\n\nඔබ දින 7ක් බොට් භාවිතා නොකළහොත් එක් මිත්‍රශීලී මතක් කිරීමක් එවන්නෙමු. මෙම සැකසුම ඕනෑම වේලාවක වෙනස් කළ හැකිය.",
        "reminder_status_on": "ක්‍රියාත්මකයි",
        "reminder_status_off": "අක්‍රියයි",
        "reminder_turn_on": "🔔 මතක් කිරීම් ක්‍රියාත්මක කරන්න",
        "reminder_turn_off": "🔕 මතක් කිරීම් අක්‍රිය කරන්න",
        "reminder_private_only": "කරුණාකර බොට් සමඟ පෞද්ගලික කතාබහකදී /reminder භාවිතා කරන්න.",
    },
    "ta": {
        "inactive_reminder": "🥺 நீண்ட நாட்களாக உங்களைப் பார்க்கவில்லை! நீங்கள் மீண்டும் வருவது எங்களுக்கு மகிழ்ச்சி.\n\nஒரு எண்ணை ஆங்கிலச் சொற்களாக மாற்ற வேண்டுமா? உங்கள் Number To Words Converter எப்போதும் உதவத் தயாராக உள்ளது! ✨\n\nசிறிய எண்ணாக இருந்தாலும் பெரிய எண்ணாக இருந்தாலும், அதை அனுப்புங்கள்; உடனே சொற்களாக எழுதப்பட்ட வடிவத்தைப் பெறுங்கள்.\n\n💡 எப்போது வேண்டுமானாலும் திரும்பி வந்து எண்ணை எளிதாக மாற்றுங்கள்!\n\n🔢 தொடங்க ஒரு எண்ணை அனுப்புங்கள்.",
        "reminder_settings": "🔔 செயலற்ற நினைவூட்டல்கள்: {status}\n\nநீங்கள் 7 நாட்கள் இந்த bot-ஐப் பயன்படுத்தாவிட்டால் ஒரு நட்பான நினைவூட்டலை அனுப்புவோம். இந்த அமைப்பை எப்போது வேண்டுமானாலும் மாற்றலாம்.",
        "reminder_status_on": "இயக்கம்",
        "reminder_status_off": "முடக்கம்",
        "reminder_turn_on": "🔔 நினைவூட்டல்களை இயக்கு",
        "reminder_turn_off": "🔕 நினைவூட்டல்களை முடக்கு",
        "reminder_private_only": "Bot உடனான தனிப்பட்ட உரையாடலில் /reminder பயன்படுத்தவும்.",
    },
    "om": {
        "inactive_reminder": "🥺 Yeroo dheeraa si hin argine! Deebitee dhufuun kee nu gammachiisa.\n\nLakkoofsa tokko gara jechoota Afaan Ingiliziitti jijjiiruu barbaaddaa? Number To Words Converter kee yeroo hunda si gargaaruuf qophaaʼaa dha! ✨\n\nLakkoofsi xiqqaa yookaan guddaan, ergi qofa; bifa jechootaan barreeffame battalumatti argatta.\n\n💡 Yeroo barbaadde deebiʼi; jijjiirraan lakkoofsaa salphaa dha!\n\n🔢 Jalqabuuf lakkoofsa ergi.",
        "reminder_settings": "🔔 Yaadachiisa yeroo hin fayyadamne: {status}\n\nGuyyaa 7f bot kana yoo hin fayyadamne, yaadachiisa michummaa tokko siif ergina. Qindaa'ina kana yeroo barbaadde jijjiiruu dandeessa.",
        "reminder_status_on": "Banaa",
        "reminder_status_off": "Cufaa",
        "reminder_turn_on": "🔔 Yaadachiisa banuu",
        "reminder_turn_off": "🔕 Yaadachiisa cufuu",
        "reminder_private_only": "Maaloo /reminder haasawa dhuunfaa bot waliin jiru keessatti fayyadami.",
    },
    "es": {
        "inactive_reminder": "🥺 ¡Hace tiempo que no hablamos! Nos alegra tenerte de vuelta.\n\n¿Necesitas convertir un número a palabras en inglés? ¡Tu Number To Words Converter está siempre listo para ayudarte! ✨\n\nYa sea un número pequeño o grande, solo envíalo y recibirás su forma escrita al instante.\n\n💡 Vuelve cuando quieras y convierte números sin esfuerzo.\n\n🔢 Envía un número para comenzar.",
        "reminder_settings": "🔔 Recordatorios por inactividad: {status}\n\nSi no usas el bot durante 7 días, te enviaremos un recordatorio amistoso. Puedes cambiar esta opción cuando quieras.",
        "reminder_status_on": "ACTIVADOS",
        "reminder_status_off": "DESACTIVADOS",
        "reminder_turn_on": "🔔 Activar recordatorios",
        "reminder_turn_off": "🔕 Desactivar recordatorios",
        "reminder_private_only": "Usa /reminder en un chat privado con el bot.",
    },
    "fr": {
        "inactive_reminder": "🥺 Cela fait un moment ! Votre présence nous manque.\n\nBesoin d’écrire un nombre en toutes lettres en anglais ? Votre Number To Words Converter est toujours là pour vous aider ! ✨\n\nPetit ou grand, envoyez simplement votre nombre et obtenez immédiatement sa forme écrite.\n\n💡 Revenez quand vous voulez et convertissez vos nombres en toute simplicité !\n\n🔢 Envoyez un nombre pour commencer.",
        "reminder_settings": "🔔 Rappels d’inactivité : {status}\n\nSi vous n’utilisez pas le bot pendant 7 jours, nous vous enverrons un rappel amical. Vous pouvez modifier ce réglage à tout moment.",
        "reminder_status_on": "ACTIVÉS",
        "reminder_status_off": "DÉSACTIVÉS",
        "reminder_turn_on": "🔔 Activer les rappels",
        "reminder_turn_off": "🔕 Désactiver les rappels",
        "reminder_private_only": "Utilisez /reminder dans une conversation privée avec le bot.",
    },
    "ru": {
        "inactive_reminder": "🥺 Давно не виделись! Нам не хватает вашего присутствия.\n\nНужно записать число английскими словами? Ваш Number To Words Converter всегда готов помочь! ✨\n\nОтправьте любое число — маленькое или большое — и мгновенно получите его запись словами.\n\n💡 Возвращайтесь в любое время и переводите числа без лишних усилий!\n\n🔢 Отправьте число, чтобы начать.",
        "reminder_settings": "🔔 Напоминания о неактивности: {status}\n\nЕсли вы не будете пользоваться ботом 7 дней, мы отправим одно дружеское напоминание. Вы можете изменить эту настройку в любое время.",
        "reminder_status_on": "ВКЛЮЧЕНЫ",
        "reminder_status_off": "ВЫКЛЮЧЕНЫ",
        "reminder_turn_on": "🔔 Включить напоминания",
        "reminder_turn_off": "🔕 Выключить напоминания",
        "reminder_private_only": "Используйте /reminder в личном чате с ботом.",
    },
    "ar": {
        "inactive_reminder": "🥺 مضى وقت طويل! نفتقد وجودك معنا.\n\nهل تحتاج إلى كتابة رقم بالكلمات الإنجليزية؟ إن Number To Words Converter جاهز دائمًا لمساعدتك! ✨\n\nسواء كان الرقم صغيرًا أم كبيرًا، أرسله فقط واحصل فورًا على كتابته بالكلمات.\n\n💡 عُد في أي وقت واجعل تحويل الأرقام أمرًا سهلًا!\n\n🔢 أرسل رقمًا للبدء.",
        "reminder_settings": "🔔 تذكيرات عدم النشاط: {status}\n\nإذا لم تستخدم البوت لمدة 7 أيام، فسنرسل إليك تذكيرًا وديًا واحدًا. يمكنك تغيير هذا الإعداد في أي وقت.",
        "reminder_status_on": "مفعّلة",
        "reminder_status_off": "متوقفة",
        "reminder_turn_on": "🔔 تفعيل التذكيرات",
        "reminder_turn_off": "🔕 إيقاف التذكيرات",
        "reminder_private_only": "يرجى استخدام /reminder في محادثة خاصة مع البوت.",
    },
}

for _locale, _messages in REMINDER_TEXTS.items():
    TEXTS[_locale].update(_messages)



def normalize_language(code: str | None) -> str:
    if not code:
        return "en"
    normalized_code = code.lower().replace("_", "-")
    if normalized_code == "am-latn":
        return "am_latn"
    short_code = normalized_code.split("-")[0]
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
        "loading": "⏳",
        "request_language_sent": "✅",
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