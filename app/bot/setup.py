from __future__ import annotations

import logging

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeChat, BotCommandScopeDefault
from app.config import Settings
from app.handlers import admin, converter, language, start
from app.handlers.common import RegisterUserMiddleware

logger = logging.getLogger(__name__)


def create_bot(settings: Settings) -> Bot:
    # Do not set a global parse mode: welcome/broadcast messages may use raw
    # Telegram entities, which must not be combined with parse_mode.
    return Bot(token=settings.bot_token)


def create_dispatcher(session_factory, settings: Settings) -> Dispatcher:
    dispatcher = Dispatcher(storage=MemoryStorage())
    dispatcher["session_factory"] = session_factory
    dispatcher["settings"] = settings

    async def session_middleware(handler, event, data):
        async with session_factory() as session:
            data["session"] = session
            return await handler(event, data)

    dispatcher.message.middleware(session_middleware)
    dispatcher.callback_query.middleware(session_middleware)
    dispatcher.message.middleware(RegisterUserMiddleware())
    dispatcher.include_router(start.router)
    dispatcher.include_router(language.router)
    dispatcher.include_router(admin.router)
    dispatcher.include_router(converter.router)
    return dispatcher


async def configure_commands(bot: Bot, settings: Settings) -> None:
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Start the converter"),
            BotCommand(command="lang", description="Change language"),
        ],
        scope=BotCommandScopeDefault(),
    )
    for admin_id in settings.admin_ids:
        try:
            await bot.set_my_commands(
                [
                    BotCommand(command="start", description="Start the converter"),
                    BotCommand(command="lang", description="Change language"),
                    BotCommand(command="admin", description="Open admin panel"),
                    BotCommand(command="ctm", description="Customize the bot"),
                ],
                scope=BotCommandScopeChat(chat_id=admin_id),
            )
        except TelegramBadRequest as error:
            # A configured admin may not have opened the bot yet, may be a
            # stale ID, or may belong to a chat Telegram cannot resolve.
            # Do not prevent polling/webhook startup for one bad chat scope.
            logger.warning(
                "Could not set admin commands for Telegram ID %s; skipping: %s",
                admin_id,
                error,
            )
