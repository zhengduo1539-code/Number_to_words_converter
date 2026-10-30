from app.keyboards.customization import (
    customization_markup,
    reminder_language_markup,
    reminder_languages_markup,
)
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.bot.setup import configure_commands
from app.services.i18n import LANGUAGES


def _callbacks(markup):
    return {
        button.callback_data
        for row in markup.inline_keyboard
        for button in row
    }


def test_ctm_has_a_separate_inactivity_reminder_customizer():
    assert "ctm:reminder" in _callbacks(customization_markup())


def test_reminder_language_menu_exposes_every_supported_locale():
    markup = reminder_languages_markup({"en", "my"})
    callbacks = _callbacks(markup)

    assert callbacks == {
        *(f"ctm:reminder_language:{language.code}" for language in LANGUAGES),
        "ctm:home",
    }
    english_button = next(
        button
        for row in markup.inline_keyboard
        for button in row
        if button.callback_data == "ctm:reminder_language:en"
    )
    assert english_button.text.startswith("✅ ")


def test_selected_language_has_edit_preview_reset_and_back_actions():
    callbacks = _callbacks(reminder_language_markup("en"))

    assert callbacks == {
        "ctm:reminder_edit:en",
        "ctm:reminder_preview:en",
        "ctm:reminder_reset:en",
        "ctm:reminder",
    }


@pytest.mark.asyncio
async def test_user_command_menu_no_longer_registers_reminder():
    bot = AsyncMock()

    await configure_commands(bot, SimpleNamespace(admin_ids=[]))

    commands = bot.set_my_commands.await_args.args[0]
    assert [command.command for command in commands] == ["start", "lang"]
