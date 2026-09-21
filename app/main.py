from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.bot.setup import configure_commands, create_bot, create_dispatcher
from app.config import get_settings
from app.db.database import create_engine, create_session_factory, init_db
from app.db.repository import initialize_defaults
from app.web.server import create_web_app

settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)
engine = create_engine(settings)
session_factory = create_session_factory(engine)
bot = create_bot(settings) if settings.bot_token else None
dispatcher = create_dispatcher(session_factory) if bot else None


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db(engine)
    async with session_factory() as session:
        await initialize_defaults(session)
    polling_task = None
    if bot and dispatcher:
        await configure_commands(bot, settings)
        if settings.webhook_url and not settings.polling:
            await bot.set_webhook(
                url=f"{settings.webhook_url.rstrip('/')}/telegram/webhook",
                secret_token=settings.webhook_secret or None,
                drop_pending_updates=False,
            )
            logger.info("Telegram webhook configured")
        elif settings.polling:
            polling_task = asyncio.create_task(dispatcher.start_polling(bot))
            logger.info("Telegram polling started")
    yield
    if polling_task:
        polling_task.cancel()
        await asyncio.gather(polling_task, return_exceptions=True)
    if bot:
        await bot.session.close()
    await engine.dispose()


if bot and dispatcher:
    app = create_web_app(settings, bot, dispatcher)
    app.router.lifespan_context = lifespan
else:
    app = FastAPI(title="Numbers to Words Converter", lifespan=lifespan)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/ready")
    async def ready() -> dict[str, str]:
        return {"status": "ready"}
