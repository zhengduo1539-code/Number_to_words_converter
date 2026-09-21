from __future__ import annotations

from app.db.models import User


def user_label(user: User) -> str:
    username = f"@{user.username}" if user.username else "no username"
    return f"{user.first_name or 'Unnamed'} ({username})\nID: {user.telegram_user_id}\nConversions: {user.total_conversions}"
