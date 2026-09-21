from types import SimpleNamespace

import pytest

from app.config import Settings
from app.db.database import create_engine, create_session_factory, init_db
from app.db.repository import (
    DEFAULT_WELCOME,
    initialize_defaults,
    list_admin_buttons,
    list_welcome_buttons,
    reset_welcome_buttons,
    upsert_user,
)


@pytest.mark.asyncio
async def test_defaults_reset_and_user_registration(tmp_path):
    settings = Settings(
        BOT_TOKEN="test",
        ADMIN_IDS="1",
        DATABASE_URL=f"sqlite+aiosqlite:///{tmp_path}/test.db",
    )
    engine = create_engine(settings)
    factory = create_session_factory(engine)
    await init_db(engine)
    async with factory() as session:
        await initialize_defaults(session)
        assert (await list_welcome_buttons(session))[0].button_type == "share"
        assert len(await list_admin_buttons(session)) == 5
        user = SimpleNamespace(
            id=900719925474099,
            first_name="Test",
            last_name=None,
            username="tester",
            language_code="en",
            is_bot=False,
        )
        first = await upsert_user(session, user, started=True)
        second = await upsert_user(session, user, started=False)
        assert first.id == second.id
        assert second.start_count == 1
        await reset_welcome_buttons(session)
        assert (await list_welcome_buttons(session))[0].button_type == "share"
        from app.db.repository import get_setting
        assert await get_setting(session, "welcome_text") == DEFAULT_WELCOME
    await engine.dispose()