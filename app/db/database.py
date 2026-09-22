from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from dataclasses import asdict, is_dataclass
from typing import Any, TypeVar
from urllib.parse import urlparse

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING, ReturnDocument

from app.config import Settings
from app.db.models import AdminButton, BotSetting, Broadcast, User, WelcomeButton


T = TypeVar("T")

MODEL_COLLECTIONS: dict[type[Any], str] = {
    User: "users",
    BotSetting: "bot_settings",
    WelcomeButton: "welcome_buttons",
    AdminButton: "admin_buttons",
    Broadcast: "broadcasts",
}


def create_client(settings: Settings) -> AsyncIOMotorClient:
    return AsyncIOMotorClient(settings.mongodb_uri, serverSelectionTimeoutMS=10_000)


def get_database(client: AsyncIOMotorClient, settings: Settings) -> AsyncIOMotorDatabase:
    database_name = urlparse(settings.mongodb_uri).path.strip("/").split("/", 1)[0]
    return client[database_name or "numbers_to_words"]


def _to_document(item: Any) -> dict[str, Any]:
    if not is_dataclass(item):
        raise TypeError(f"Unsupported MongoDB model: {type(item)!r}")
    document = asdict(item)
    document.pop("_id", None)
    return document


def _from_document(model: type[T], document: dict[str, Any] | None) -> T | None:
    if document is None:
        return None
    document = dict(document)
    document.pop("_id", None)
    return model(**document)


class MongoSession:
    """Small async unit-of-work adapter used by handlers and repositories."""

    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database

    async def __aenter__(self) -> MongoSession:
        return self

    async def __aexit__(self, *_exc: object) -> None:
        return None

    def collection_for(self, model: type[Any]):
        return self.database[MODEL_COLLECTIONS[model]]

    async def next_id(self, collection_name: str) -> int:
        counter = await self.database["_counters"].find_one_and_update(
            {"_id": collection_name},
            {"$inc": {"value": 1}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        return int(counter["value"])

    async def add(self, item: Any) -> Any:
        collection = self.collection_for(type(item))
        if not item.id:
            item.id = await self.next_id(MODEL_COLLECTIONS[type(item)])
        document = _to_document(item)
        await collection.replace_one({"id": item.id}, document, upsert=True)
        return item

    async def add_all(self, items: list[Any]) -> None:
        for item in items:
            await self.add(item)

    async def delete(self, item: Any) -> None:
        await self.collection_for(type(item)).delete_one({"id": item.id})

    async def commit(self) -> None:
        return None

    async def refresh(self, item: Any) -> None:
        refreshed = await self.collection_for(type(item)).find_one({"id": item.id})
        loaded = _from_document(type(item), refreshed)
        if loaded:
            for key, value in vars(loaded).items():
                setattr(item, key, value)

    async def get(self, model: type[T], item_id: int) -> T | None:
        document = await self.collection_for(model).find_one({"id": item_id})
        return _from_document(model, document)


def create_session_factory(database: AsyncIOMotorDatabase) -> Callable[[], MongoSession]:
    return lambda: MongoSession(database)


async def init_db(database: AsyncIOMotorDatabase) -> None:
    await database.command("ping")
    await database.users.create_index([("telegram_user_id", ASCENDING)], unique=True)
    await database.users.create_index([("last_seen_at", DESCENDING)])
    await database.users.create_index([("username", ASCENDING)])
    await database.bot_settings.create_index([("key", ASCENDING)], unique=True)
    await database.welcome_buttons.create_index([("sort_order", ASCENDING), ("id", ASCENDING)])
    await database.admin_buttons.create_index([("action", ASCENDING)], unique=True)
    await database.broadcasts.create_index([("started_at", DESCENDING)])


async def session_scope(factory: Callable[[], MongoSession]) -> AsyncIterator[MongoSession]:
    async with factory() as session:
        yield session