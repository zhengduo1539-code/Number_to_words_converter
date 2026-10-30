import json
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, call

import pytest
from aiogram.types import MessageEntity

from app.services.i18n import LANGUAGES, text
from app.services.reminder_messages import (
    get_reminder_message,
    reminder_entities_setting_key,
    reminder_text_setting_key,
)
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

    async def to_list(self, length=None):
        return self.documents[:length]


class FakeSettings:
    def __init__(self, documents=None):
        self.documents = documents or []

    async def find_one(self, query):
        return next(
            (item for item in self.documents if item.get("key") == query.get("key")),
            None,
        )

    def find(self, query):
        keys = set(query["key"]["$in"])
        return FakeCursor([item for item in self.documents if item.get("key") in keys])


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
    def __init__(self, documents, settings=None):
        self.users = FakeUsers(documents)
        self.bot_settings = FakeSettings(settings)


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


@pytest.mark.asyncio
async def test_custom_reminder_overrides_only_its_selected_language():
    custom = "A custom English reminder."
    database = FakeDatabase([], [
        {"key": reminder_text_setting_key("en"), "value": custom},
        {"key": reminder_entities_setting_key("en"), "value": "[]"},
    ])

    english, english_entities = await get_reminder_message(database, "en")
    myanmar, myanmar_entities = await get_reminder_message(database, "my")

    assert english == custom
    assert english_entities == []
    assert myanmar == text("inactive_reminder", "my")
    assert myanmar_entities == []


@pytest.mark.asyncio
async def test_custom_reminder_entities_are_loaded_for_preview_and_delivery():
    entity = MessageEntity(
        type="custom_emoji",
        offset=0,
        length=2,
        custom_emoji_id="123456789",
    )
    database = FakeDatabase([], [
        {"key": reminder_text_setting_key("en"), "value": "🎉 Come back!"},
        {
            "key": reminder_entities_setting_key("en"),
            "value": json.dumps([entity.model_dump(exclude_none=True)]),
        },
    ])

    message_text, entities = await get_reminder_message(database, "en")

    assert message_text == "🎉 Come back!"
    assert len(entities) == 1
    assert entities[0].custom_emoji_id == "123456789"


@pytest.mark.asyncio
async def test_scheduler_sends_localized_or_custom_message_once_and_marks_it_sent(monkeypatch):
    stale = datetime.now(timezone.utc) - timedelta(days=8)
    users = [
        {
            "telegram_user_id": 101,
            "is_bot": False,
            "is_blocked": False,
            "reminders_enabled": False,
            "last_seen_at": stale,
            "last_reminder_at": None,
            "preferred_language": "my",
        },
        {
            "telegram_user_id": 202,
            "is_bot": False,
            "is_blocked": False,
            "last_seen_at": stale,
            "last_reminder_at": None,
            "preferred_language": "en",
        },
    ]
    custom = "Admin-customized English reminder."
    database = FakeDatabase(users, [
        {"key": reminder_text_setting_key("en"), "value": custom},
        {"key": reminder_entities_setting_key("en"), "value": "[]"},
    ])
    bot = AsyncMock()
    monkeypatch.setattr("app.services.reminder_scheduler.asyncio.sleep", AsyncMock())

    sent = await send_due_reminders(bot, database)

    assert sent == 2
    assert bot.send_message.await_args_list == [
        call(101, text("inactive_reminder", "my")),
        call(202, custom),
    ]
    assert all(user["last_reminder_at"] is not None for user in users)
    assert "reminders_enabled" not in database.users.query
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
            "last_seen_at": recent,
            "last_reminder_at": None,
            "preferred_language": "en",
        },
        {
            "telegram_user_id": 404,
            "is_bot": False,
            "is_blocked": False,
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

    database = FakeDatabase([
        {"telegram_user_id": 505, "is_blocked": False},
    ])

    await _mark_unreachable(database, 505, RuntimeError("chat not found"))

    assert database.users.documents[0]["is_blocked"] is True
    assert len(database.users.updates) == 1
