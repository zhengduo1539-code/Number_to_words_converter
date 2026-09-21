from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup

from app.keyboards.buttons import compatible_button


def admin_menu_markup() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [compatible_button("📊 Stats", callback_data="admin:stats", style="primary"),
         compatible_button("👥 User List", callback_data="admin:users", style="primary")],
        [compatible_button("📣 Broadcast", callback_data="admin:broadcast", style="success"),
         compatible_button("⚙️ Customize", callback_data="admin:customize", style="primary")],
        [compatible_button("✖️ Close", callback_data="admin:close", style="danger")],
    ])


def stats_markup() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [compatible_button("🔄 Refresh", callback_data="admin:stats", style="primary"),
         compatible_button("⬅️ Back", callback_data="admin:back", style="primary")],
    ])


def users_markup(page: int, pages: int) -> InlineKeyboardMarkup:
    row = []
    if page > 0:
        row.append(compatible_button("⬅️ Prev", callback_data=f"admin:users:{page - 1}", style="primary"))
    row.append(compatible_button(f"Page {page + 1}/{pages}", callback_data="noop", style="primary"))
    if page + 1 < pages:
        row.append(compatible_button("Next ➡️", callback_data=f"admin:users:{page + 1}", style="primary"))
    return InlineKeyboardMarkup(inline_keyboard=[row, [compatible_button("⬅️ Back", callback_data="admin:back", style="primary")]])


def broadcast_markup() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [compatible_button("📣 Broadcast to All", callback_data="broadcast:all", style="success")],
        [compatible_button("👤 Send to One User", callback_data="broadcast:one", style="primary")],
        [compatible_button("✖️ Cancel", callback_data="admin:back", style="danger")],
    ])
