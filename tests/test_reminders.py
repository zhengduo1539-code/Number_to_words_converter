from app.keyboards.reminder import reminder_settings_markup
from app.services.i18n import LANGUAGES, text


def test_inactivity_reminder_is_localized_for_every_supported_language():
    rendered = {
        language.code: text("inactive_reminder", language.code)
        for language in LANGUAGES
    }

    assert set(rendered) == {language.code for language in LANGUAGES}
    assert all(message.startswith("🥺") for message in rendered.values())
    assert rendered["en"].startswith("🥺 It's been a while!")
    assert rendered["my"] != rendered["en"]
    assert rendered["zh"] != rendered["en"]


def test_reminder_settings_text_supports_localized_status_values():
    for language in LANGUAGES:
        message = text(
            "reminder_settings",
            language.code,
            status=text("reminder_status_on", language.code),
        )
        assert "{status}" not in message
        assert message


def test_reminder_keyboard_offers_the_opposite_action():
    enabled = reminder_settings_markup(True, "my")
    disabled = reminder_settings_markup(False, "my")

    enabled_button = enabled.inline_keyboard[0][0]
    disabled_button = disabled.inline_keyboard[0][0]

    assert enabled_button.callback_data == "reminder:off"
    assert disabled_button.callback_data == "reminder:on"


from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, call

import pytest

from app.services.reminder_scheduler import send_due_reminders


class FakeCursor:
    def __init__(self, documents):
        self.documents = documents

    def sort(self, *_args):
        return self

    def __aiter__(self):
        self._index = 0
        return self

    async def __anext__(self):
        if self._index >= len(self.documents):
            raise StopAsyncIteration
        document = self.documents[self._index]
        self._index += 1
        return document


class FakeUsers:
    def __init__(self, documents):
        self.documents = documents
        self.query = None
        self.updates = []

    def find(self, query):
        self.query = query
        cutoff = query["last_seen_at"]["$lte"]
        eligible = [
            item for item in self.documents
            if item.get("is_bot") is False
            and item.get("is_blocked") is not True
            and item.get("reminders_enabled") is not False
            and item.get("last_seen_at") <= cutoff
            and item.get("last_reminder_at") is None
        ]
        return FakeCursor(eligible)

    async def update_one(self, selector, update):
        self.updates.append((selector, update))
        for item in self.documents:
            if (
                item.get("telegram_user_id") == selector.get("telegram_user_id")
                and item.get("last_seen_at") == selector.get("last_seen_at")
            ):
                item.update(update["$set"])
                break


class FakeDatabase:
    def __init__(self, documents):
        self.users = FakeUsers(documents)


@pytest.mark.asyncio
async def test_scheduler_sends_localized_message_once_and_marks_it_sent(monkeypatch):
    stale = datetime.now(timezone.utc) - timedelta(days=8)
    users = [
        {
            "telegram_user_id": 101,
            "is_bot": False,
            "is_blocked": False,
            "reminders_enabled": True,
            "last_seen_at": stale,
            "last_reminder_at": None,
            "preferred_language": "my",
        },
        {
            "telegram_user_id": 202,
            "is_bot": False,
            "is_blocked": False,
            "reminders_enabled": True,
            "last_seen_at": stale,
            "last_reminder_at": None,
            "preferred_language": "en",
        },
    ]
    database = FakeDatabase(users)
    bot = AsyncMock()
    monkeypatch.setattr("app.services.reminder_scheduler.asyncio.sleep", AsyncMock())

    sent = await send_due_reminders(bot, database)

    assert sent == 2
    assert bot.send_message.await_args_list == [
        call(101, text("inactive_reminder", "my")),
        call(202, text("inactive_reminder", "en")),
    ]
    assert all(user["last_reminder_at"] is not None for user in users)
    assert database.users.query["reminders_enabled"] == {"$ne": False}
    assert database.users.query["is_blocked"] == {"$ne": True}
    assert database.users.query["last_reminder_at"] is None


@pytest.mark.asyncio
async def test_scheduler_does_not_select_recent_or_already_reminded_users(monkeypatch):
    recent = datetime.now(timezone.utc) - timedelta(days=2)
    stale_but_reminded = datetime.now(timezone.utc) - timedelta(days=9)
    users = [
        {
            "telegram_user_id": 303,
            "is_bot": False,
            "is_blocked": False,
            "reminders_enabled": True,
            "last_seen_at": recent,
            "last_reminder_at": None,
            "preferred_language": "en",
        },
        {
            "telegram_user_id": 404,
            "is_bot": False,
            "is_blocked": False,
            "reminders_enabled": True,
            "last_seen_at": stale_but_reminded,
            "last_reminder_at": datetime.now(timezone.utc),
            "preferred_language": "en",
        },
    ]
    database = FakeDatabase(users)
    bot = AsyncMock()
    monkeypatch.setattr("app.services.reminder_scheduler.asyncio.sleep", AsyncMock())

    sent = await send_due_reminders(bot, database)

    assert sent == 0
    bot.send_message.assert_not_awaited()



@pytest.mark.asyncio
async def test_unreachable_user_is_marked_blocked_to_avoid_retries():
    from app.services.reminder_scheduler import _mark_unreachable

    users = FakeUsers([
        {"telegram_user_id": 505, "is_blocked": False},
    ])
    database = FakeDatabase(users.documents)

    await _mark_unreachable(database, 505, RuntimeError("chat not found"))

    assert users.documents[0]["is_blocked"] is True
    assert len(users.updates) == 1
