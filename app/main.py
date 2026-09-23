from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import Response

from app.bot.setup import configure_commands, create_bot, create_dispatcher
from app.config import get_settings
from app.db.database import create_client, create_session_factory, get_database, init_db
from app.db.repository import initialize_defaults
from app.web.server import create_web_app

settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)
mongo_client = create_client(settings)
database = get_database(mongo_client, settings)
session_factory = create_session_factory(database)
bot = create_bot(settings) if settings.bot_token else None
dispatcher = create_dispatcher(session_factory, settings) if bot else None


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db(database)
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
        else:
            if not settings.polling:
                logger.warning(
                    "POLLING is disabled but WEBHOOK_URL is not configured; "
                    "falling back to polling so Telegram updates are not dropped"
                )
            # Polling and a Telegram webhook cannot consume updates at the
            # same time. A previous deployment may have left a webhook
            # configured even after switching back to polling, which makes
            # every command appear unresponsive. Keep pending updates and
            # explicitly clear that stale webhook before getUpdates starts.
            await bot.delete_webhook(drop_pending_updates=False)
            polling_task = asyncio.create_task(dispatcher.start_polling(bot))
            logger.info("Telegram polling started")
    yield
    if polling_task:
        polling_task.cancel()
        await asyncio.gather(polling_task, return_exceptions=True)
    if bot:
        await bot.session.close()
    mongo_client.close()


if bot and dispatcher:
    app = create_web_app(settings, bot, dispatcher)
    app.router.lifespan_context = lifespan
else:
    app = FastAPI(title="Numbers to Words Converter", lifespan=lifespan)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.head("/health")
    async def health_head() -> Response:
        return Response(status_code=200)

    @app.get("/healthz")
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.head("/healthz")
    async def healthz_head() -> Response:
        return Response(status_code=200)

    @app.get("/ready")
    async def ready() -> dict[str, str]:
        return {"status": "ready"}

    @app.head("/ready")
    async def ready_head() -> Response:
        return Response(status_code=200)
