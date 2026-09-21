from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

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


async def get_setting(session: AsyncSession, key: str, default: str = "") -> str:
    item = await session.scalar(select(BotSetting).where(BotSetting.key == key))
    return item.value if item else default


async def set_setting(session: AsyncSession, key: str, value: str) -> None:
    item = await session.scalar(select(BotSetting).where(BotSetting.key == key))
    if item:
        item.value = value
    else:
        session.add(BotSetting(key=key, value=value))
    await session.commit()


async def initialize_defaults(session: AsyncSession) -> None:
    if await session.scalar(select(BotSetting).where(BotSetting.key == "welcome_text")) is None:
        session.add(BotSetting(key="welcome_text", value=DEFAULT_WELCOME))
    if await session.scalar(select(BotSetting).where(BotSetting.key == "welcome_entities")) is None:
        session.add(BotSetting(key="welcome_entities", value="[]"))
    if not (await session.scalars(select(WelcomeButton))).first():
        session.add_all([WelcomeButton(**button) for button in DEFAULT_WELCOME_BUTTONS])
    if not (await session.scalars(select(AdminButton))).first():
        session.add_all([AdminButton(**button) for button in DEFAULT_ADMIN_BUTTONS])
    await session.commit()


async def upsert_user(session: AsyncSession, telegram_user: Any, started: bool = False) -> User:
    user = await session.scalar(select(User).where(User.telegram_user_id == telegram_user.id))
    now = datetime.now(timezone.utc)
    if user is None:
        user = User(
            telegram_user_id=telegram_user.id,
            first_name=telegram_user.first_name or "",
            last_name=telegram_user.last_name,
            username=telegram_user.username,
            language_code=telegram_user.language_code,
            is_bot=telegram_user.is_bot,
            first_seen_at=now,
            last_seen_at=now,
            start_count=1 if started else 0,
        )
        session.add(user)
    else:
        user.first_name = telegram_user.first_name or ""
        user.last_name = telegram_user.last_name
        user.username = telegram_user.username
        user.language_code = telegram_user.language_code
        user.last_seen_at = now
        user.is_blocked = False
        if started:
            user.start_count += 1
    await session.commit()
    await session.refresh(user)
    return user


async def increment_conversion(session: AsyncSession, telegram_user_id: int) -> None:
    await session.execute(
        update(User)
        .where(User.telegram_user_id == telegram_user_id)
        .values(total_conversions=User.total_conversions + 1, last_seen_at=datetime.now(timezone.utc))
    )
    await session.commit()


async def list_welcome_buttons(session: AsyncSession) -> list[WelcomeButton]:
    return list((await session.scalars(
        select(WelcomeButton).where(WelcomeButton.is_active.is_(True)).order_by(WelcomeButton.sort_order, WelcomeButton.id)
    )).all())


async def get_welcome_button(session: AsyncSession, button_id: int) -> WelcomeButton | None:
    return await session.get(WelcomeButton, button_id)


async def save_welcome_button(session: AsyncSession, button: WelcomeButton) -> None:
    session.add(button)
    await session.commit()


async def delete_welcome_button(session: AsyncSession, button: WelcomeButton) -> None:
    await session.delete(button)
    await session.commit()


async def list_admin_buttons(session: AsyncSession) -> list[AdminButton]:
    return list((await session.scalars(
        select(AdminButton).where(AdminButton.is_active.is_(True)).order_by(AdminButton.sort_order, AdminButton.id)
    )).all())


async def get_admin_button(session: AsyncSession, action: str) -> AdminButton | None:
    return await session.scalar(select(AdminButton).where(AdminButton.action == action))


async def reset_welcome_buttons(session: AsyncSession) -> None:
    await session.execute(WelcomeButton.__table__.delete())
    session.add_all([WelcomeButton(**button) for button in DEFAULT_WELCOME_BUTTONS])
    await session.commit()


async def reset_admin_buttons(session: AsyncSession) -> None:
    await session.execute(AdminButton.__table__.delete())
    session.add_all([AdminButton(**button) for button in DEFAULT_ADMIN_BUTTONS])
    await session.commit()


async def reset_welcome_message(session: AsyncSession) -> None:
    await set_setting(session, "welcome_text", DEFAULT_WELCOME)
    await set_setting(session, "welcome_entities", "[]")


async def stats(session: AsyncSession) -> dict[str, int]:
    now = datetime.now(timezone.utc)
    count = lambda condition=None: session.scalar(select(func.count(User.id)).where(condition) if condition is not None else select(func.count(User.id)))
    total = await count()
    today = await count(User.last_seen_at >= now - timedelta(days=1))
    week = await count(User.last_seen_at >= now - timedelta(days=7))
    month = await count(User.last_seen_at >= now - timedelta(days=30))
    conversions = await session.scalar(select(func.coalesce(func.sum(User.total_conversions), 0)))
    started = await count(User.start_count > 0)
    blocked = await count(User.is_blocked.is_(True))
    return {
        "total_users": int(total or 0),
        "active_today": int(today or 0),
        "active_7_days": int(week or 0),
        "active_30_days": int(month or 0),
        "total_conversions": int(conversions or 0),
        "started_users": int(started or 0),
        "blocked_users": int(blocked or 0),
    }


async def list_users(session: AsyncSession, page: int, page_size: int = 5) -> tuple[list[User], int]:
    total = int(await session.scalar(select(func.count(User.id))) or 0)
    rows = list((await session.scalars(
        select(User).order_by(User.last_seen_at.desc()).offset(page * page_size).limit(page_size)
    )).all())
    return rows, total


async def find_recipients(session: AsyncSession, target_user_id: int | None = None) -> list[User]:
    query = select(User).where(User.is_bot.is_(False), User.is_blocked.is_(False))
    if target_user_id is not None:
        query = query.where(User.telegram_user_id == target_user_id)
    return list((await session.scalars(query.order_by(User.id))).all())


async def mark_blocked(session: AsyncSession, telegram_user_id: int) -> None:
    await session.execute(update(User).where(User.telegram_user_id == telegram_user_id).values(is_blocked=True))
    await session.commit()


async def create_broadcast(session: AsyncSession, **values: Any) -> Broadcast:
    item = Broadcast(**values)
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


async def update_broadcast(session: AsyncSession, item: Broadcast, **values: Any) -> None:
    for key, value in values.items():
        setattr(item, key, value)
    await session.commit()


def entities_json(entities: list[dict[str, Any]]) -> str:
    return json.dumps(entities, ensure_ascii=False)
