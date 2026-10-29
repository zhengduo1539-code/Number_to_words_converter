import pytest

from app.services.number_converter import integer_to_words, is_number, number_to_words


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("10482", "Ten thousand four hundred eighty-two"),
        ("21", "Twenty-one"),
        ("48", "Forty-eight"),
        ("101", "One hundred one"),
        ("482", "Four hundred eighty-two"),
        ("1001", "One thousand one"),
        ("1205", "One thousand two hundred five"),
        ("1000000", "One million"),
        ("0", "Zero"),
        ("-125", "Negative one hundred twenty-five"),
        ("10,482", "Ten thousand four hundred eighty-two"),
        ("10.25", "Ten point two five"),
    ],
)
def test_number_to_words(value, expected):
    assert number_to_words(value) == expected
    assert " and " not in number_to_words(value).lower()


def test_large_integer():
    assert integer_to_words(10**21) == "One sextillion"


def test_sinhala_number_forms():
    assert number_to_words("0", "si") == "බිංදුව"
    assert number_to_words("21", "si") == "විසි එක"
    assert number_to_words("10482", "si") == "දහය දහස් හාරසිය අසූ දෙක"
    assert number_to_words("-10.25", "si") == "ඍණ දහය දශම දෙක පහ"


def test_tamil_number_forms():
    assert number_to_words("0", "ta") == "சுழியம்"
    assert number_to_words("21", "ta") == "இருபத்து ஒன்று"
    assert number_to_words("10482", "ta") == "பத்து ஆயிரம் நானூற்று எண்பத்து இரண்டு"
    assert number_to_words("-10.25", "ta") == "எதிர்மறை பத்து புள்ளி இரண்டு ஐந்து"


def test_bengali_number_forms():
    assert number_to_words("21", "bn") == "একুশ"
    assert number_to_words("10482", "bn") == "দশ হাজার চারশ বিরাশি"
    assert number_to_words("-10.25", "bn") == "ঋণাত্মক দশ দশমিক দুই পাঁচ"


@pytest.mark.parametrize("value", ["hello", "1,23", "1.", "--5", ""])
def test_invalid_values(value):
    assert not is_number(value)
