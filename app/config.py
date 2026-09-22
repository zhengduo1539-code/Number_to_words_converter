from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-backed application configuration."""

    # pydantic-settings normally JSON-decodes complex environment values
    # before validators run. ADMIN_IDS is documented as comma-separated in
    # .env.example, so keep decoding disabled and parse that value ourselves.
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        enable_decoding=False,
        extra="ignore",
    )

    bot_token: str = Field(default="", alias="BOT_TOKEN")
    admin_ids: list[int] = Field(default_factory=list, alias="ADMIN_IDS")
    mongodb_uri: str = Field(
        default="mongodb://localhost:27017/numbers_to_words",
        alias="MONGODB_URI",
    )
    webhook_url: str = Field(default="", alias="WEBHOOK_URL")
    webhook_secret: str = Field(default="", alias="WEBHOOK_SECRET")
    port: int = Field(default=10000, alias="PORT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    polling: bool = Field(default=True, alias="POLLING")

    @field_validator("admin_ids", mode="before")
    @classmethod
    def parse_admin_ids(cls, value: Any) -> list[int]:
        if value is None or value == "":
            return []
        if isinstance(value, str):
            raw_value = value.strip()
            if not raw_value:
                return []
            if raw_value.startswith("["):
                try:
                    values = json.loads(raw_value)
                except json.JSONDecodeError:
                    values = raw_value.split(",")
            else:
                values = raw_value.split(",")
        else:
            values = value
        result: list[int] = []
        for item in values:
            try:
                result.append(int(str(item).strip()))
            except (TypeError, ValueError):
                continue
        return result

@lru_cache
def get_settings() -> Settings:
    return Settings()
