from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Any

from app.db.database import MongoSession, _from_document
from app.db.models import AdminButton, BotSetting, Broadcast, User, WelcomeButton


DEFAULT_WELCOME = (
    "👋 Welcome to Numbers to Words Converter!\n\n"
    "Send me any number and I will convert it into English words.\n\n"
    "Example:\n10482 → Ten thousand four hundred eighty-two\n\n"
    "Just send a number to get started."
)

DEFAULT_WELCOME_BUTTONS = [
    {"label": "🔗 Share Bot", "button_type": "share", "style": "primary", "sort_order": 0, "callback_action": "share"},
]

DEFAULT_ADMIN_BUTTONS = [
    {"action": "stats", "label": "📊 Stats", "style": "primary", "sort_order": 0},
    {"action": "users", "label": "👥 User List", "style": "primary", "sort_order": 1},
    {"action": "broadcast", "label": "📣 Broadcast", "style": "success", "sort_order": 2},
    {"action": "customize", "label": "⚙️ Customize", "style": "primary", "sort_order": 3},
    {"action": "close", "label": "✖️ Close", "style": "danger", "sort_order": 4},
]


async def get_setting(session: MongoSession, key: str, default: str = "") -> str:
    item = await session.database.bot_settings.find_one({"key": key})
    return str(item["value"]) if item else default


async def set_setting(session: MongoSession, key: str, value: str) -> None:
    existing = await session.database.bot_settings.find_one({"key": key})
    now = datetime.now(timezone.utc)
    if existing:
        await session.database.bot_settings.update_one(
            {"key": key},
            {"$set": {"value": value, "updated_at": now}},
        )
    else:
        await session.add(BotSetting(id=await session.next_id("bot_settings"), key=key, value=value, updated_at=now))


async def initialize_defaults(session: MongoSession) -> None:
    if await session.database.bot_settings.count_documents({"key": "welcome_text"}) == 0:
        await set_setting(session, "welcome_text", DEFAULT_WELCOME)
    if await session.database.bot_settings.count_documents({"key": "welcome_entities"}) == 0:
        await set_setting(session, "welcome_entities", "[]")
    if await session.database.welcome_buttons.count_documents({}) == 0:
        await session.add_all([WelcomeButton(**button) for button in DEFAULT_WELCOME_BUTTONS])
    if await session.database.admin_buttons.count_documents({}) == 0:
        await session.add_all([AdminButton(**button) for button in DEFAULT_ADMIN_BUTTONS])


async def upsert_user(session: MongoSession, telegram_user: Any, started: bool = False) -> User:
    existing = await session.database.users.find_one({"telegram_user_id": telegram_user.id})
    now = datetime.now(timezone.utc)
    if existing:
        user = _from_document(User, existing)
        assert user is not None
        user.first_name = telegram_user.first_name or ""
        user.last_name = telegram_user.last_name
        user.username = telegram_user.username
        user.language_code = telegram_user.language_code
        user.last_seen_at = now
        user.updated_at = now
        user.is_blocked = False
        if started:
            user.start_count += 1
    else:
        user = User(
            id=await session.next_id("users"),
            telegram_user_id=telegram_user.id,
            first_name=telegram_user.first_name or "",
            last_name=telegram_user.last_name,
            username=telegram_user.username,
            language_code=telegram_user.language_code,
            preferred_language="en",
            is_bot=telegram_user.is_bot,
            first_seen_at=now,
            last_seen_at=now,
            start_count=1 if started else 0,
            created_at=now,
            updated_at=now,
        )
    await session.add(user)
    return user


async def get_user_by_telegram_id(session: MongoSession, telegram_user_id: int) -> User | None:
    document = await session.database.users.find_one({"telegram_user_id": telegram_user_id})
    return _from_document(User, document)


async def get_user_language(session: MongoSession, telegram_user_id: int) -> str:
    user = await get_user_by_telegram_id(session, telegram_user_id)
    return user.preferred_language if user and user.preferred_language else "en"


async def set_user_language(session: MongoSession, telegram_user_id: int, language: str) -> None:
    await session.database.users.update_one(
        {"telegram_user_id": telegram_user_id},
        {"$set": {"preferred_language": language, "last_seen_at": datetime.now(timezone.utc)}},
    )


async def increment_conversion(session: MongoSession, telegram_user_id: int) -> None:
    await session.database.users.update_one(
        {"telegram_user_id": telegram_user_id},
        {
            "$inc": {"total_conversions": 1},
            "$set": {"last_seen_at": datetime.now(timezone.utc)},
        },
    )


async def list_welcome_buttons(session: MongoSession) -> list[WelcomeButton]:
    documents = await session.database.welcome_buttons.find({"is_active": True}).sort(
        [("sort_order", 1), ("id", 1)]
    ).to_list(length=None)
    return [_from_document(WelcomeButton, document) for document in documents if document]


async def get_welcome_button(session: MongoSession, button_id: int) -> WelcomeButton | None:
    return await session.get(WelcomeButton, button_id)


async def save_welcome_button(session: MongoSession, button: WelcomeButton) -> None:
    await session.add(button)


async def delete_welcome_button(session: MongoSession, button: WelcomeButton) -> None:
    await session.delete(button)


async def list_admin_buttons(session: MongoSession) -> list[AdminButton]:
    documents = await session.database.admin_buttons.find({"is_active": True}).sort(
        [("sort_order", 1), ("id", 1)]
    ).to_list(length=None)
    return [_from_document(AdminButton, document) for document in documents if document]


async def get_admin_button(session: MongoSession, action: str) -> AdminButton | None:
    document = await session.database.admin_buttons.find_one({"action": action})
    return _from_document(AdminButton, document)


async def reset_welcome_buttons(session: MongoSession) -> None:
    await session.database.welcome_buttons.delete_many({})
    await session.add_all([WelcomeButton(**button) for button in DEFAULT_WELCOME_BUTTONS])


async def reset_admin_buttons(session: MongoSession) -> None:
    await session.database.admin_buttons.delete_many({})
    await session.add_all([AdminButton(**button) for button in DEFAULT_ADMIN_BUTTONS])


async def reset_welcome_message(session: MongoSession) -> None:
    await set_setting(session, "welcome_text", DEFAULT_WELCOME)
    await set_setting(session, "welcome_entities", "[]")


async def stats(session: MongoSession) -> dict[str, int]:
    now = datetime.now(timezone.utc)
    users = session.database.users
    total = await users.count_documents({})
    today = await users.count_documents({"last_seen_at": {"$gte": now - timedelta(days=1)}})
    week = await users.count_documents({"last_seen_at": {"$gte": now - timedelta(days=7)}})
    month = await users.count_documents({"last_seen_at": {"$gte": now - timedelta(days=30)}})
    started = await users.count_documents({"start_count": {"$gt": 0}})
    blocked = await users.count_documents({"is_blocked": True})
    aggregation = await users.aggregate(
        [{"$group": {"_id": None, "total": {"$sum": "$total_conversions"}}}]
    ).to_list(length=1)
    conversions = int(aggregation[0]["total"]) if aggregation else 0
    return {
        "total_users": int(total),
        "active_today": int(today),
        "active_7_days": int(week),
        "active_30_days": int(month),
        "total_conversions": conversions,
        "started_users": int(started),
        "blocked_users": int(blocked),
    }


async def list_users(session: MongoSession, page: int, page_size: int = 5) -> tuple[list[User], int]:
    users = session.database.users
    total = await users.count_documents({})
    documents = await users.find({}).sort("last_seen_at", -1).skip(page * page_size).limit(page_size).to_list(
        length=page_size
    )
    return [_from_document(User, document) for document in documents if document], int(total)


async def find_recipients(session: MongoSession, target_user_id: int | None = None) -> list[User]:
    query: dict[str, Any] = {"is_bot": False, "is_blocked": False}
    if target_user_id is not None:
        query["telegram_user_id"] = target_user_id
    documents = await session.database.users.find(query).sort("id", 1).to_list(length=None)
    return [_from_document(User, document) for document in documents if document]


async def mark_blocked(session: MongoSession, telegram_user_id: int) -> None:
    await session.database.users.update_one(
        {"telegram_user_id": telegram_user_id},
        {"$set": {"is_blocked": True, "updated_at": datetime.now(timezone.utc)}},
    )


async def create_broadcast(session: MongoSession, **values: Any) -> Broadcast:
    item = Broadcast(id=await session.next_id("broadcasts"), **values)
    await session.add(item)
    return item


async def update_broadcast(session: MongoSession, item: Broadcast, **values: Any) -> None:
    for key, value in values.items():
        setattr(item, key, value)
    await session.add(item)


def entities_json(entities: list[dict[str, Any]]) -> str:
    return json.dumps(entities, ensure_ascii=False)