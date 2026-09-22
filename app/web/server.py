from __future__ import annotations

import hmac
import logging

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse, Response

from app.config import Settings

logger = logging.getLogger(__name__)


def create_web_app(settings: Settings, bot, dispatcher) -> FastAPI:
    web_app = FastAPI(title="Numbers to Words Converter")

    @web_app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @web_app.head("/health")
    async def health_head() -> Response:
        return Response(status_code=200)

    @web_app.get("/healthz")
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @web_app.head("/healthz")
    async def healthz_head() -> Response:
        return Response(status_code=200)

    @web_app.get("/ready")
    async def ready() -> dict[str, str]:
        return {"status": "ready"}

    @web_app.head("/ready")
    async def ready_head() -> Response:
        return Response(status_code=200)

    @web_app.post("/telegram/webhook")
    async def telegram_webhook(request: Request, x_telegram_bot_api_secret_token: str | None = Header(default=None)) -> JSONResponse:
        if settings.webhook_secret and not hmac.compare_digest(
            x_telegram_bot_api_secret_token or "", settings.webhook_secret
        ):
            raise HTTPException(status_code=403, detail="Invalid webhook secret")
        from aiogram.types import Update

        update = Update.model_validate(await request.json(), context={"bot": bot})
        await dispatcher.feed_update(bot, update)
        return JSONResponse({"ok": True})

    return web_app
