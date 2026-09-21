from __future__ import annotations

from aiogram.types import CallbackQuery, User

from app.config import Settings


def is_admin(user: User | None, settings: Settings) -> bool:
    return bool(user and user.id in settings.admin_ids)


async def require_admin_callback(callback: CallbackQuery, settings: Settings) -> bool:
    if not is_admin(callback.from_user, settings):
        await callback.answer("Unauthorized", show_alert=True)
        return False
    return True
