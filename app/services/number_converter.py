from __future__ import annotations

import re

ONES = (
    "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
)
TEENS = (
    "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
    "seventeen", "eighteen", "nineteen",
)
TENS = ("", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety")
SCALES = (
    "", "thousand", "million", "billion", "trillion", "quadrillion", "quintillion",
    "sextillion", "septillion", "octillion", "nonillion", "decillion",
    "undecillion", "duodecillion", "tredecillion", "quattuordecillion",
    "quindecillion", "sexdecillion", "septendecillion", "octodecillion",
    "novemdecillion", "vigintillion",
)
NUMBER_RE = re.compile(r"^[+-]?(?:(?:\d{1,3}(?:,\d{3})+)|\d+)(?:\.\d+)?$")
SUPPORTED_LANGUAGE_CODES = frozenset({"en", "bn", "zh", "my", "am", "om", "es", "fr", "ru", "ar"})


def _under_thousand(number: int) -> str:
    parts: list[str] = []
    hundreds, remainder = divmod(number, 100)
    if hundreds:
        parts.extend((ONES[hundreds], "hundred"))
    if remainder:
        if remainder < 10:
            parts.append(ONES[remainder])
        elif remainder < 20:
            parts.append(TEENS[remainder - 10])
        else:
            tens, ones = divmod(remainder, 10)
            parts.append(TENS[tens] + (f"-{ONES[ones]}" if ones else ""))
    return " ".join(parts)


def integer_to_words(number: int) -> str:
    if number == 0:
        return "Zero"
    if number < 0:
        return f"Negative {integer_to_words(-number).lower()}"
    groups: list[str] = []
    scale = 0
    while number:
        number, group = divmod(number, 1000)
        if group:
            if scale >= len(SCALES):
                raise ValueError("Number is too large for the configured English scale names")
            words = _under_thousand(group)
            if SCALES[scale]:
                words = f"{words} {SCALES[scale]}"
            groups.append(words)
        scale += 1
    return " ".join(reversed(groups)).capitalize()


def _parse_number(value: str) -> tuple[int, str | None]:
    normalized = value.strip().replace(",", "")
    if not NUMBER_RE.fullmatch(value.strip()):
        raise ValueError("Input is not a valid number")
    if "." in normalized:
        integer, fractional = normalized.split(".", 1)
        return int(integer), fractional
    return int(normalized), None


def parse_number(value: str) -> tuple[int, str | None]:
    """Public parser retained for callers that need normalized numeric parts."""
    return _parse_number(value)


def _zh_section(number: int) -> str:
    digits = "零一二三四五六七八九"
    units = ("", "十", "百", "千")
    result: list[str] = []
    zero_pending = False
    for position in range(3, -1, -1):
        digit = (number // 10**position) % 10
        if digit:
            if zero_pending and result:
                result.append("零")
            if not (position == 1 and digit == 1 and not result):
                result.append(digits[digit])
            result.append(units[position])
            zero_pending = False
        elif result and position:
            zero_pending = True
    return "".join(result)


def _chinese_integer(number: int) -> str:
    if number == 0:
        return "零"
    if number < 0:
        return f"负{_chinese_integer(-number)}"
    units = ("", "万", "亿", "兆", "京")
    groups: list[int] = []
    while number:
        number, group = divmod(number, 10000)
        groups.append(group)
    result = ""
    zero_between = False
    for index in range(len(groups) - 1, -1, -1):
        group = groups[index]
        if not group:
            if result:
                zero_between = True
            continue
        if result and (zero_between or group < 1000):
            result += "零"
        result += _zh_section(group) + units[index]
        zero_between = False
    return result


def _spanish_under_thousand(number: int) -> str:
    ones = ("cero", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve")
    teens = ("diez", "once", "doce", "trece", "catorce", "quince", "dieciséis", "diecisiete", "dieciocho", "diecinueve")
    tens = ("", "", "veinte", "treinta", "cuarenta", "cincuenta", "sesenta", "setenta", "ochenta", "noventa")
    hundreds = ("", "ciento", "doscientos", "trescientos", "cuatrocientos", "quinientos", "seiscientos", "setecientos", "ochocientos", "novecientos")
    if number < 10:
        return ones[number]
    if number < 20:
        return teens[number - 10]
    if number < 30:
        special = ("veinte", "veintiuno", "veintidós", "veintitrés", "veinticuatro", "veinticinco", "veintiséis", "veintisiete", "veintiocho", "veintinueve")
        return special[number - 20]
    if number < 100:
        ten, one = divmod(number, 10)
        return tens[ten] + (f" y {ones[one]}" if one else "")
    hundred, remainder = divmod(number, 100)
    if number == 100:
        return "cien"
    return hundreds[hundred] + (f" {_spanish_under_thousand(remainder)}" if remainder else "")


def _spanish_integer(number: int) -> str:
    if number == 0:
        return "cero"
    if number < 0:
        return f"menos {_spanish_integer(-number)}"
    scales = (("", ""), ("mil", "mil"), ("millón", "millones"), ("mil millones", "mil millones"), ("billón", "billones"), ("mil billones", "mil billones"))
    groups: list[int] = []
    while number:
        number, group = divmod(number, 1000)
        groups.append(group)
    if len(groups) > len(scales):
        raise ValueError("Number is too large for Spanish scale names")
    parts: list[str] = []
    for index in range(len(groups) - 1, -1, -1):
        group = groups[index]
        if not group:
            continue
        if index == 1:
            parts.append("mil" if group == 1 else _spanish_under_thousand(group) + " mil")
        elif index >= 2:
            name = scales[index][0 if group == 1 else 1]
            prefix = "" if group == 1 else _spanish_under_thousand(group) + " "
            parts.append(prefix + name)
        else:
            parts.append(_spanish_under_thousand(group))
    return " ".join(parts)


def _french_under_thousand(number: int) -> str:
    ones = ("zéro", "un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf")
    teens = ("dix", "onze", "douze", "treize", "quatorze", "quinze", "seize", "dix-sept", "dix-huit", "dix-neuf")
    tens = ("", "", "vingt", "trente", "quarante", "cinquante", "soixante")
    if number < 10:
        return ones[number]
    if number < 20:
        return teens[number - 10]
    if number < 70:
        ten, one = divmod(number, 10)
        return tens[ten] + ((" et un" if one == 1 else f"-{ones[one]}") if one else "")
    if number < 80:
        return "soixante" + (" et onze" if number == 71 else f"-{teens[number - 70]}")
    if number < 100:
        remainder = number - 80
        return "quatre-vingts" if remainder == 0 else "quatre-vingt-" + (ones[remainder] if remainder < 10 else teens[remainder - 10])
    hundred, remainder = divmod(number, 100)
    prefix = "cent" if hundred == 1 else f"{ones[hundred]} cent"
    if not remainder:
        return prefix + ("s" if hundred > 1 else "")
    return f"{prefix} {_french_under_thousand(remainder)}"


def _french_integer(number: int) -> str:
    if number == 0:
        return "zéro"
    if number < 0:
        return f"moins {_french_integer(-number)}"
    groups: list[int] = []
    while number:
        number, group = divmod(number, 1000)
        groups.append(group)
    scales = ("", "mille", "million", "milliard", "billion", "billiard", "trillion")
    parts: list[str] = []
    for index in range(len(groups) - 1, -1, -1):
        group = groups[index]
        if not group:
            continue
        if index == 1:
            parts.append("mille" if group == 1 else f"{_french_under_thousand(group)} mille")
        elif index >= 2:
            parts.append(f"{_french_under_thousand(group)} {scales[index]}{'s' if group > 1 else ''}")
        else:
            parts.append(_french_under_thousand(group))
    return " ".join(parts)


def _russian_under_thousand(number: int, feminine: bool = False) -> str:
    ones_m = ("ноль", "один", "два", "три", "четыре", "пять", "шесть", "семь", "восемь", "девять")
    ones_f = ("ноль", "одна", "две", "три", "четыре", "пять", "шесть", "семь", "восемь", "девять")
    teens = ("десять", "одиннадцать", "двенадцать", "тринадцать", "четырнадцать", "пятнадцать", "шестнадцать", "семнадцать", "восемнадцать", "девятнадцать")
    tens = ("", "", "двадцать", "тридцать", "сорок", "пятьдесят", "шестьдесят", "семьдесят", "восемьдесят", "девяносто")
    hundreds = ("", "сто", "двести", "триста", "четыреста", "пятьсот", "шестьсот", "семьсот", "восемьсот", "девятьсот")
    if number < 10:
        return (ones_f if feminine else ones_m)[number]
    if number < 20:
        return teens[number - 10]
    hundred, remainder = divmod(number, 100)
    parts = [hundreds[hundred]] if hundred else []
    if remainder >= 20:
        ten, one = divmod(remainder, 10)
        parts.append(tens[ten])
        if one:
            parts.append((ones_f if feminine else ones_m)[one])
    elif remainder:
        parts.append(teens[remainder - 10] if remainder >= 10 else (ones_f if feminine else ones_m)[remainder])
    return " ".join(parts)


def _russian_integer(number: int) -> str:
    if number == 0:
        return "ноль"
    if number < 0:
        return f"минус {_russian_integer(-number)}"
    scales = (
        ("", "", "", False),
        ("тысяча", "тысячи", "тысяч", True),
        ("миллион", "миллиона", "миллионов", False),
        ("миллиард", "миллиарда", "миллиардов", False),
        ("триллион", "триллиона", "триллионов", False),
        ("квадриллион", "квадриллиона", "квадриллионов", False),
    )
    groups: list[int] = []
    while number:
        number, group = divmod(number, 1000)
        groups.append(group)
    if len(groups) > len(scales):
        raise ValueError("Number is too large for Russian scale names")
    parts: list[str] = []
    for index in range(len(groups) - 1, -1, -1):
        group = groups[index]
        if not group:
            continue
        if index == 0:
            parts.append(_russian_under_thousand(group))
        else:
            parts.append(_russian_under_thousand(group, scales[index][2]))
            last_two = group % 100
            singular = group % 10 == 1 and last_two != 11
            plural = group % 10 in {2, 3, 4} and not 12 <= last_two <= 14
            parts.append(scales[index][0] if singular else scales[index][1] if plural else scales[index][2])
    return " ".join(parts)


def _amharic_under_thousand(number: int) -> str:
    ones = ("ዜሮ", "አንድ", "ሁለት", "ሶስት", "አራት", "አምስት", "ስድስት", "ሰባት", "ስምንት", "ዘጠኝ")
    tens = ("", "", "ሃያ", "ሰላሳ", "አርባ", "ሃምሳ", "ስልሳ", "ሰባ", "ሰማንያ", "ዘጠና")
    if number < 10:
        return ones[number]
    if number < 20:
        return "አስር" if number == 10 else "አስራ " + ones[number - 10]
    if number < 100:
        ten, one = divmod(number, 10)
        return tens[ten] + (f" {ones[one]}" if one else "")
    hundred, remainder = divmod(number, 100)
    prefix = "መቶ" if hundred == 1 else f"{ones[hundred]} መቶ"
    return prefix + (f" { _amharic_under_thousand(remainder)}" if remainder else "")


def _amharic_integer(number: int) -> str:
    if number == 0:
        return "ዜሮ"
    if number < 0:
        return f"አሉታዊ {_amharic_integer(-number)}"
    scales = ("", "ሺህ", "ሚሊዮን", "ቢሊዮን", "ትሪሊዮን")
    groups: list[int] = []
    while number:
        number, group = divmod(number, 1000)
        groups.append(group)
    if len(groups) > len(scales):
        raise ValueError("Number is too large for Amharic scale names")
    parts: list[str] = []
    for index in range(len(groups) - 1, -1, -1):
        if not groups[index]:
            continue
        if index == 0:
            parts.append(_amharic_under_thousand(groups[index]))
        else:
            prefix = "" if groups[index] == 1 else _amharic_under_thousand(groups[index]) + " "
            parts.append(prefix + scales[index])
    return " ".join(parts)


def _oromo_under_thousand(number: int) -> str:
    ones = ("zeero", "tokko", "lama", "sadii", "afur", "shan", "ja'a", "torba", "saddeet", "sagal")
    tens = ("", "", "digdama", "soddoma", "afurtama", "shantama", "jaatama", "torbaatama", "saddeetama", "sagaltama")
    if number < 10:
        return ones[number]
    if number < 20:
        return "kudhan" if number == 10 else "kudha " + ones[number - 10]
    if number < 100:
        ten, one = divmod(number, 10)
        return tens[ten] + (f" fi {ones[one]}" if one else "")
    hundred, remainder = divmod(number, 100)
    prefix = "dhibba tokko" if hundred == 1 else f"{ones[hundred]} dhibba"
    return prefix + (f" fi {_oromo_under_thousand(remainder)}" if remainder else "")


def _oromo_integer(number: int) -> str:
    if number == 0:
        return "zeero"
    if number < 0:
        return f"negatiivii {_oromo_integer(-number)}"
    scales = ("", "kuma", "miliyoona", "biliyoona", "tiriliyoona")
    groups: list[int] = []
    while number:
        number, group = divmod(number, 1000)
        groups.append(group)
    if len(groups) > len(scales):
        raise ValueError("Number is too large for Afaan Oromo scale names")
    parts: list[str] = []
    for index in range(len(groups) - 1, -1, -1):
        if not groups[index]:
            continue
        if index == 0:
            parts.append(_oromo_under_thousand(groups[index]))
        else:
            prefix = "" if groups[index] == 1 else _oromo_under_thousand(groups[index]) + " "
            parts.append(prefix + scales[index])
    return " fi ".join(parts)


def _arabic_join(parts: list[str]) -> str:
    """Join Arabic number groups with the conjunction attached to the next word."""
    return " و".join(part for part in parts if part)


def _arabic_under_hundred(number: int) -> str:
    ones = (
        "صفر", "واحد", "اثنان", "ثلاثة", "أربعة",
        "خمسة", "ستة", "سبعة", "ثمانية", "تسعة",
    )
    teens = (
        "عشرة", "أحد عشر", "اثنا عشر", "ثلاثة عشر", "أربعة عشر",
        "خمسة عشر", "ستة عشر", "سبعة عشر", "ثمانية عشر", "تسعة عشر",
    )
    tens = (
        "", "", "عشرون", "ثلاثون", "أربعون", "خمسون",
        "ستون", "سبعون", "ثمانون", "تسعون",
    )
    if number < 10:
        return ones[number]
    if number < 20:
        return teens[number - 10]
    ten, one = divmod(number, 10)
    return _arabic_join([ones[one], tens[ten]]) if one else tens[ten]


def _arabic_under_thousand(number: int) -> str:
    if number < 100:
        return _arabic_under_hundred(number)
    hundreds = (
        "", "مائة", "مائتان", "ثلاثمائة", "أربعمائة",
        "خمسمائة", "ستمائة", "سبعمائة", "ثمانمائة", "تسعمائة",
    )
    hundred, remainder = divmod(number, 100)
    prefix = hundreds[hundred]
    return _arabic_join([prefix, _arabic_under_hundred(remainder)]) if remainder else prefix


def _arabic_integer(number: int) -> str:
    if number == 0:
        return "صفر"
    if number < 0:
        return f"سالب {_arabic_integer(-number)}"

    scales = (
        ("", "", ""),
        ("ألف", "ألفان", "آلاف"),
        ("مليون", "مليونان", "ملايين"),
        ("مليار", "ملياران", "مليارات"),
        ("تريليون", "تريليونان", "تريليونات"),
        ("كوادريليون", "كوادريليونان", "كوادريليونات"),
    )
    groups: list[int] = []
    while number:
        number, group = divmod(number, 1000)
        groups.append(group)
    if len(groups) > len(scales):
        raise ValueError("Number is too large for Arabic scale names")

    parts: list[str] = []
    for index in range(len(groups) - 1, -1, -1):
        group = groups[index]
        if not group:
            continue
        if index == 0:
            parts.append(_arabic_under_thousand(group))
            continue

        singular, dual, plural = scales[index]
        if group == 1:
            parts.append(singular)
        elif group == 2:
            parts.append(dual)
        elif group < 11:
            parts.append(f"{_arabic_under_thousand(group)} {plural}")
        else:
            parts.append(f"{_arabic_under_thousand(group)} {singular}ًا")
    return _arabic_join(parts)


_BENGALI_ONES = (
    "শূন্য", "এক", "দুই", "তিন", "চার", "পাঁচ", "ছয়", "সাত", "আট", "নয়",
)
_BENGALI_TEENS = (
    "দশ", "এগারো", "বারো", "তেরো", "চৌদ্দ", "পনেরো",
    "ষোলো", "সতেরো", "আঠারো", "উনিশ",
)
_BENGALI_TENS = ("", "", "বিশ", "ত্রিশ", "চল্লিশ", "পঞ্চাশ", "ষাট", "সত্তর", "আশি", "নব্বই")
_BENGALI_COMPOUND_NUMBERS = {
    21: "একুশ", 22: "বাইশ", 23: "তেইশ", 24: "চব্বিশ", 25: "পঁচিশ",
    26: "ছাব্বিশ", 27: "সাতাশ", 28: "আটাশ", 29: "উনত্রিশ",
    31: "একত্রিশ", 32: "বত্রিশ", 33: "তেত্রিশ", 34: "চৌত্রিশ",
    35: "পঁয়ত্রিশ", 36: "ছত্রিশ", 37: "সাঁইত্রিশ", 38: "আটত্রিশ", 39: "উনচল্লিশ",
    41: "একচল্লিশ", 42: "বিয়াল্লিশ", 43: "তেতাল্লিশ", 44: "চুয়াল্লিশ",
    45: "পঁয়তাল্লিশ", 46: "ছেচল্লিশ", 47: "সাতচল্লিশ", 48: "আটচল্লিশ", 49: "উনপঞ্চাশ",
    51: "একান্ন", 52: "বাহান্ন", 53: "তিপ্পান্ন", 54: "চুয়ান্ন",
    55: "পঞ্চান্ন", 56: "ছাপ্পান্ন", 57: "সাতান্ন", 58: "আটান্ন", 59: "উনষাট",
    61: "একষট্টি", 62: "বাষট্টি", 63: "তেষট্টি", 64: "চৌষট্টি",
    65: "পঁয়ষট্টি", 66: "ছেষট্টি", 67: "সাতষট্টি", 68: "আটষট্টি", 69: "উনসত্তর",
    71: "একাত্তর", 72: "বাহাত্তর", 73: "তিয়াত্তর", 74: "চুয়াত্তর",
    75: "পঁচাত্তর", 76: "ছিয়াত্তর", 77: "সাতাত্তর", 78: "আটাত্তর", 79: "উনআশি",
    81: "একাশি", 82: "বিরাশি", 83: "তিরাশি", 84: "চুরাশি",
    85: "পঁচাশি", 86: "ছিয়াশি", 87: "সাতাশি", 88: "আটাশি", 89: "উননব্বই",
    91: "একানব্বই", 92: "বিরানব্বই", 93: "তিরানব্বই", 94: "চুরানব্বই",
    95: "পঁচানব্বই", 96: "ছিয়ানব্বই", 97: "সাতানব্বই", 98: "আটানব্বই", 99: "নিরানব্বই",
}
_BENGALI_HUNDREDS = ("", "একশ", "দুইশ", "তিনশ", "চারশ", "পাঁচশ", "ছয়শ", "সাতশ", "আটশ", "নয়শ")


def _bengali_under_hundred(number: int) -> str:
    if number < 10:
        return _BENGALI_ONES[number]
    if number < 20:
        return _BENGALI_TEENS[number - 10]
    return _BENGALI_COMPOUND_NUMBERS.get(
        number,
        _BENGALI_TENS[number // 10] + f" {_BENGALI_ONES[number % 10]}",
    )


def _bengali_under_thousand(number: int) -> str:
    if number < 100:
        return _bengali_under_hundred(number)
    hundreds, remainder = divmod(number, 100)
    result = _BENGALI_HUNDREDS[hundreds]
    return f"{result} {_bengali_under_hundred(remainder)}" if remainder else result


def _bengali_integer(number: int) -> str:
    if number == 0:
        return _BENGALI_ONES[0]
    if number < 0:
        return f"ঋণাত্মক {_bengali_integer(-number)}"

    parts: list[str] = []
    remainder = number
    for unit, name in ((10**7, "কোটি"), (10**5, "লাখ"), (10**3, "হাজার")):
        if remainder >= unit:
            quotient, remainder = divmod(remainder, unit)
            parts.append(f"{_bengali_integer(quotient)} {name}")
    if remainder:
        parts.append(_bengali_under_thousand(remainder))
    return " ".join(parts)


def _integer_in_language(number: int, language: str) -> str:
    if language == "en":
        return integer_to_words(number)
    if language == "bn":
        return _bengali_integer(number)
    if language == "zh":
        return _chinese_integer(number)
    if language == "my":
        return _myanmar_integer(number)
    if language == "am":
        return _amharic_integer(number)
    if language == "om":
        return _oromo_integer(number)
    if language == "es":
        return _spanish_integer(number)
    if language == "fr":
        return _french_integer(number)
    if language == "ru":
        return _russian_integer(number)
    if language == "ar":
        return _arabic_integer(number)
    return integer_to_words(number)


def _myanmar_under_thousand(number: int) -> str:
    ones = ("သုည", "တစ်", "နှစ်", "သုံး", "လေး", "ငါး", "ခြောက်", "ခုနစ်", "ရှစ်", "ကိုး")
    if number == 0:
        return ones[0]
    parts: list[str] = []
    hundreds, remainder = divmod(number, 100)
    if hundreds:
        parts.append(f"{ones[hundreds]}ရာ")
    if remainder:
        tens, one = divmod(remainder, 10)
        if tens:
            parts.append("ဆယ်" if tens == 1 else f"{ones[tens]}ဆယ်")
            if one:
                parts[-1] += f"့{ones[one]}"
        elif one:
            parts.append(ones[one])
    return " ".join(parts)


def _myanmar_integer(number: int) -> str:
    if number == 0:
        return "သုည"
    if number < 0:
        return f"အနုတ် {_myanmar_integer(-number)}"
    if number < 1000:
        return _myanmar_under_thousand(number)
    scales = (
        (10**12, "ထရီလီယံ"),
        (10**9, "ဘီလီယံ"),
        (10**6, "သန်း"),
        (10**5, "သိန်း"),
        (10**4, "သောင်း"),
        (10**3, "ထောင်"),
    )
    parts: list[str] = []
    remainder = number
    for unit, name in scales:
        if remainder >= unit:
            quotient, remainder = divmod(remainder, unit)
            parts.append(f"{_myanmar_under_thousand(quotient)}{name}")
    if remainder:
        parts.append(_myanmar_under_thousand(remainder))
    return " ".join(parts)


def _decimal_digits(fractional: str, language: str) -> str:
    digit_names = {
        "en": ONES,
        "bn": _BENGALI_ONES,
        "zh": tuple("零一二三四五六七八九"),
        "my": ("သုည", "တစ်", "နှစ်", "သုံး", "လေး", "ငါး", "ခြောက်", "ခုနစ်", "ရှစ်", "ကိုး"),
        "am": ("ዜሮ", "አንድ", "ሁለት", "ሶስት", "አራት", "አምስት", "ስድስት", "ሰባት", "ስምንት", "ዘጠኝ"),
        "om": ("zeero", "tokko", "lama", "sadii", "afur", "shan", "ja'a", "torba", "saddeet", "sagal"),
        "es": ("cero", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve"),
        "fr": ("zéro", "un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf"),
        "ru": ("ноль", "один", "два", "три", "четыре", "пять", "шесть", "семь", "восемь", "девять"),
        "ar": ("صفر", "واحد", "اثنان", "ثلاثة", "أربعة", "خمسة", "ستة", "سبعة", "ثمانية", "تسعة"),
    }
    return " ".join(digit_names.get(language, ONES)[int(digit)] for digit in fractional)


def number_to_words(value: str, language: str = "en") -> str:
    integer, fractional = _parse_number(value)
    language = language if language in SUPPORTED_LANGUAGE_CODES else "en"
    if fractional is None:
        result = _integer_in_language(integer, language)
        return result if language in {"zh", "my", "am", "om", "es", "fr", "ru"} else result
    negative = integer < 0
    magnitude = _integer_in_language(abs(integer), language)
    prefixes = {"en": "Negative", "bn": "ঋণাত্মক", "zh": "负", "my": "အနုတ်", "am": "አሉታዊ", "om": "negatiivii", "es": "menos", "fr": "moins", "ru": "минус", "ar": "سالب"}
    separators = {"en": "point", "bn": "দশমিক", "zh": "点", "my": "ဒသမ", "am": "ነጥብ", "om": "tuqaa", "es": "coma", "fr": "virgule", "ru": "целых", "ar": "فاصلة"}
    prefix = f"{prefixes[language]} " if negative else ""
    return f"{prefix}{magnitude} {separators[language]} {_decimal_digits(fractional, language)}"


def is_number(value: str) -> bool:
    return bool(NUMBER_RE.fullmatch(value.strip()))