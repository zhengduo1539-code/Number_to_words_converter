from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

ONES = ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine")
TEENS = ("ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen")
TENS = ("", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety")
SCALES = ("", "thousand", "million", "billion", "trillion", "quadrillion", "quintillion", "sextillion", "septillion", "octillion", "nonillion", "decillion", "undecillion", "duodecillion", "tredecillion", "quattuordecillion", "quindecillion", "sexdecillion", "septendecillion", "octodecillion", "novemdecillion", "vigintillion")
NUMBER_RE = re.compile(r"^[+-]?(?:(?:\d{1,3}(?:,\d{3})+)|\d+)(?:\.\d+)?$")


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
            words = _under_thousand(group)
            if scale >= len(SCALES):
                raise ValueError("Number is too large for the configured English scale names")
            if SCALES[scale]:
                words = f"{words} {SCALES[scale]}"
            groups.append(words)
        scale += 1
    return " ".join(reversed(groups)).capitalize()


def parse_number(value: str) -> tuple[int, str | None]:
    normalized = value.strip().replace(",", "")
    if not NUMBER_RE.fullmatch(value.strip()):
        raise ValueError("Input is not a valid number")
    if "." in normalized:
        integer, fractional = normalized.split(".", 1)
        if not fractional:
            raise ValueError("Decimal part is empty")
        return int(integer), fractional
    return int(normalized), None


def number_to_words(value: str) -> str:
    integer, fractional = parse_number(value)
    result = integer_to_words(integer)
    if fractional is not None:
        prefix = "Negative " if integer < 0 else ""
        integer_words = integer_to_words(abs(integer)).lower()
        result = prefix + integer_words + " point " + " ".join(ONES[int(digit)] for digit in fractional)
        result = result.capitalize()
    return result


def is_number(value: str) -> bool:
    return bool(NUMBER_RE.fullmatch(value.strip()))
