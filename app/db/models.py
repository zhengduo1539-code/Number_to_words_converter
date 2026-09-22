from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class User:
    id: int = 0
    telegram_user_id: int = 0
    first_name: str = ""
    last_name: str | None = None
    username: str | None = None
    language_code: str | None = None
    preferred_language: str = "en"
    is_bot: bool = False
    first_seen_at: datetime = field(default_factory=utc_now)
    last_seen_at: datetime = field(default_factory=utc_now)
    start_count: int = 0
    total_conversions: int = 0
    is_blocked: bool = False
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)


@dataclass
class BotSetting:
    id: int = 0
    key: str = ""
    value: str = ""
    updated_at: datetime = field(default_factory=utc_now)


@dataclass
class WelcomeButton:
    id: int = 0
    label: str = ""
    button_type: str = "url"
    url: str | None = None
    callback_action: str | None = None
    style: str = "primary"
    icon_custom_emoji_id: str | None = None
    fallback_emoji: str | None = None
    sort_order: int = 0
    is_active: bool = True
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)


@dataclass
class AdminButton:
    id: int = 0
    action: str = ""
    label: str = ""
    style: str = "primary"
    icon_custom_emoji_id: str | None = None
    fallback_emoji: str | None = None
    sort_order: int = 0
    is_active: bool = True
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)


@dataclass
class Broadcast:
    id: int = 0
    target_type: str = ""
    target_user_id: int | None = None
    message_text: str = ""
    message_entities_json: str | None = None
    total: int = 0
    success_count: int = 0
    failure_count: int = 0
    blocked_count: int = 0
    started_at: datetime = field(default_factory=utc_now)
    finished_at: datetime | None = None
    status: str = "pending"