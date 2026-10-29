from html import escape
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from aiogram.exceptions import TelegramBadRequest

from app.db.models import WelcomeButton
from app.db.repository import DEFAULT_WELCOME
from app.handlers import start as start_handler
from app.services.i18n import LANGUAGES, localized_default_welcome
from app.services.number_converter import number_to_words


@pytest.mark.parametrize("language", [item.code for item in LANGUAGES])
def test_default_welcome_rich_html_preserves_localized_copy(language):
    message_text = localized_default_welcome(
        language,
        number_to_words("10482", language),
    )

    rich_html = start_handler._default_welcome_rich_html(message_text)

    assert rich_html is not None
    assert "<h2>" in rich_html
    assert "<hr/>" in rich_html
    assert "<pre>" in rich_html
    assert "<footer>" in rich_html
    sections = message_text.split("\n\n")
    example_heading, example_value = sections[2].split("\n", 1)
    for value in (sections[0], sections[1], example_heading, example_value, sections[3]):
        assert escape(value) in rich_html


def _welcome_mocks(monkeypatch, welcome_text):
    async def fake_get_setting(_session, key, default=""):
        if key == "welcome_text":
            return welcome_text
        if key == "welcome_entities":
            return "[]"
        return default

    monkeypatch.setattr(start_handler, "get_setting", fake_get_setting)
    monkeypatch.setattr(
        start_handler,
        "list_welcome_buttons",
        AsyncMock(return_value=[WelcomeButton(label="🔗 Share Bot", button_type="share")]),
    )
    message = SimpleNamespace(
        chat=SimpleNamespace(id=12345),
        answer=AsyncMock(),
    )
    return message


async def test_default_welcome_uses_rich_message_and_keeps_inline_buttons(monkeypatch):
    message = _welcome_mocks(monkeypatch, DEFAULT_WELCOME)
    bot = SimpleNamespace(
        get_me=AsyncMock(return_value=SimpleNamespace(username="numbers_bot")),
        send_rich_message=AsyncMock(return_value=object()),
    )

    await start_handler.send_welcome(message, object(), bot, "en")

    bot.send_rich_message.assert_awaited_once()
    message.answer.assert_not_awaited()
    kwargs = bot.send_rich_message.await_args.kwargs
    assert kwargs["chat_id"] == message.chat.id
    assert kwargs["rich_message"].html.startswith("<h2>👋 Welcome")
    assert kwargs["reply_markup"] is not None
    assert len(kwargs["reply_markup"].inline_keyboard) == 1


async def test_custom_welcome_keeps_existing_legacy_rendering(monkeypatch):
    custom_text = "✨ My custom welcome\n\nKeep the current layout unchanged."
    message = _welcome_mocks(monkeypatch, custom_text)
    bot = SimpleNamespace(
        get_me=AsyncMock(return_value=SimpleNamespace(username="numbers_bot")),
        send_rich_message=AsyncMock(return_value=object()),
    )

    await start_handler.send_welcome(message, object(), bot, "en")

    bot.send_rich_message.assert_not_awaited()
    message.answer.assert_awaited_once()
    args = message.answer.await_args.kwargs
    assert args["entities"] is None
    assert "✨ My custom welcome" in message.answer.await_args.args[0]
    assert args["reply_markup"] is not None


async def test_rejected_rich_welcome_falls_back_to_regular_message(monkeypatch):
    message = _welcome_mocks(monkeypatch, DEFAULT_WELCOME)
    bot = SimpleNamespace(
        get_me=AsyncMock(return_value=SimpleNamespace(username="numbers_bot")),
        send_rich_message=AsyncMock(
            side_effect=TelegramBadRequest(
                method=SimpleNamespace(),
                message="Rich messages are unavailable",
            )
        ),
    )

    await start_handler.send_welcome(message, object(), bot, "en")

    bot.send_rich_message.assert_awaited_once()
    message.answer.assert_awaited_once()
    assert message.answer.await_args.args[0] == localized_default_welcome(
        "en",
        number_to_words("10482", "en"),
    )
    assert message.answer.await_args.kwargs["entities"] is None
    assert message.answer.await_args.kwargs["reply_markup"] is not None
