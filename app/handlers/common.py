from __future__ import annotations

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.db.repository import upsert_user


class RegisterUserMiddleware(BaseMiddleware):
    """Register every private-chat user before a handler runs."""

    async def __call__(self, handler, event: TelegramObject, data: dict):
        session = data.get("session")
        user = getattr(event, "from_user", None)
        if session is not None and user is not None:
            await upsert_user(session, user, started=False)
        return await handler(event, data)
