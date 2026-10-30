from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError, TelegramRetryAfter

from app.services.i18n import normalize_language, text

logger = logging.getLogger(__name__)

INACTIVITY_PERIOD = timedelta(days=7)
REMINDER_SCAN_INTERVAL_SECONDS = 60 * 60


async def _mark_unreachable(database: Any, telegram_user_id: int, error: Exception) -> None:
    """Stop retrying recipients Telegram says cannot receive private messages."""
    await database.users.update_one(
        {"telegram_user_id": telegram_user_id},
        {"$set": {
            "is_blocked": True,
            "updated_at": datetime.now(timezone.utc),
        }},
    )
    logger.info(
        "Skipped future inactivity reminders for unreachable Telegram user %s: %s",
        telegram_user_id,
        error,
    )


async def send_due_reminders(bot: Bot, database: Any) -> int:
    """Send at most one reminder for each inactive period.

    A new private interaction clears last_reminder_at, allowing one reminder
    after the next seven-day period. Legacy user documents without the new
    preference fields keep reminders enabled by default.
    """
    now = datetime.now(timezone.utc)
    cutoff = now - INACTIVITY_PERIOD
    query = {
        "is_bot": False,
        "is_blocked": {"$ne": True},
        "reminders_enabled": {"$ne": False},
        "last_seen_at": {"$lte": cutoff},
        "last_reminder_at": None,
    }
    cursor = database.users.find(query).sort("last_seen_at", 1)
    sent = 0

    async for user in cursor:
        telegram_user_id = user.get("telegram_user_id")
        last_seen_at = user.get("last_seen_at")
        if not telegram_user_id or last_seen_at is None:
            continue

        locale = normalize_language(user.get("preferred_language"))
        message_text = text("inactive_reminder", locale)
        try:
            await bot.send_message(telegram_user_id, message_text)
        except TelegramRetryAfter as error:
            await asyncio.sleep(max(0.0, float(error.retry_after)))
            try:
                await bot.send_message(telegram_user_id, message_text)
            except (TelegramForbiddenError, TelegramBadRequest) as delivery_error:
                await _mark_unreachable(database, telegram_user_id, delivery_error)
                continue
            except Exception:
                logger.exception(
                    "Retry failed for inactivity reminder to Telegram user %s",
                    telegram_user_id,
                )
                continue
        except (TelegramForbiddenError, TelegramBadRequest) as delivery_error:
            await _mark_unreachable(database, telegram_user_id, delivery_error)
            continue
        except Exception:
            logger.exception(
                "Could not send inactivity reminder to Telegram user %s",
                telegram_user_id,
            )
            continue

        sent_at = datetime.now(timezone.utc)
        await database.users.update_one(
            {
                "telegram_user_id": telegram_user_id,
                "last_seen_at": last_seen_at,
            },
            {"$set": {"last_reminder_at": sent_at, "updated_at": sent_at}},
        )
        sent += 1
        await asyncio.sleep(0.05)

    if sent:
        logger.info("Sent %s seven-day inactivity reminder(s)", sent)
    return sent


async def run_reminder_scheduler(bot: Bot, database: Any) -> None:
    """Run an immediate catch-up scan, then check for due users hourly."""
    while True:
        try:
            await send_due_reminders(bot, database)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Inactivity reminder scan failed")
        await asyncio.sleep(REMINDER_SCAN_INTERVAL_SECONDS)
