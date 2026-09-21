# Numbers to Words Converter

A production-ready Telegram bot that converts numbers to natural American English words:

```text
10482 -> Ten thousand four hundred eighty-two
```

It includes PostgreSQL-ready persistence, an admin panel, customizable welcome content and buttons, automatic Telegram custom-emoji entity storage, controlled broadcasts, a FastAPI health endpoint, and Render webhook support.

## Features

- Integers, comma-separated numbers, negatives, decimals, and arbitrary-precision values.
- `/lang` language selector with American English as the default and Simplified Chinese, Myanmar, Amharic, Afaan Oromo, Spanish, French, and Russian output.
- `/start` welcome flow with a dynamically generated Share Bot URL.
- Admin-only `/admin` and `/ctm` commands authorized by numeric Telegram IDs.
- Database-backed welcome and admin button customization.
- Custom emoji IDs extracted from Telegram message entities; admins never type IDs manually.
- Reset, cancel, preview, pagination, and broadcast confirmation workflows.
- PostgreSQL in production; SQLite is the default local fallback.
- `GET /health`, `GET /ready`, and `POST /telegram/webhook`.

## Language selection

The general Telegram command menu contains `/start` and `/lang`. Press `/lang` and choose a green inline button:

- American English (default)
- Chinese (Simplified)
- Myanmar
- Amharic
- Afaan Oromo
- Spanish
- French
- Russian

The selection is stored per Telegram user in the database and is restored after restarts. The selected language controls the default welcome copy, number conversion output, invalid-input guidance, and the Share Bot button label. An administrator's custom welcome message remains unchanged and is shown as configured.

## Project structure

```text
app/
  bot/          Telegram bot and dispatcher setup
  db/           SQLAlchemy models, database, and repository
  handlers/     Thin Telegram handlers and admin workflows
  keyboards/    Inline keyboard builders
  services/     Number conversion and emoji serialization
  states/       aiogram FSM states
  utils/        Security, formatting, and pagination helpers
  web/          FastAPI health and webhook endpoints
tests/          Unit tests
```

## Environment variables

Copy `.env.example` to `.env` for local development:

| Variable | Required | Description |
| --- | --- | --- |
| `BOT_TOKEN` | Yes | Telegram BotFather token |
| `ADMIN_IDS` | Yes | Comma-separated numeric Telegram user IDs |
| `DATABASE_URL` | Production | `postgresql+asyncpg://...`; SQLite fallback is used locally |
| `WEBHOOK_URL` | Render webhook | Public service URL, for example `https://your-service.onrender.com` |
| `WEBHOOK_SECRET` | Recommended | Telegram webhook secret token using letters, numbers, `_`, or `-` |
| `PORT` | Render-provided | HTTP port; defaults to `10000` locally |
| `POLLING` | Local only | `true` for polling, `false` for webhook mode |
| `LOG_LEVEL` | No | Defaults to `INFO` |

Never commit `.env`, tokens, database passwords, or webhook secrets.

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m pytest
uvicorn app.main:app --host 0.0.0.0 --port 10000
```

Set `POLLING=true` and provide `BOT_TOKEN` for local Telegram testing. The app creates the local SQLite schema automatically. For PostgreSQL, set `DATABASE_URL` to an async SQLAlchemy URL such as:

```text
postgresql+asyncpg://user:password@host:5432/numbers_to_words
```

## Admin usage

Set `ADMIN_IDS` to the numeric Telegram IDs of trusted administrators. `/admin` opens:

- Stats
- Paginated User List
- Broadcast to all registered users or one user
- Customization Center

`/ctm` edits the welcome message, welcome buttons, and admin panel buttons. A message pasted with Telegram custom emoji is stored with its entities and reused. Inline-button custom emoji uses Telegram's `icon_custom_emoji_id` when supported, with a normal Unicode fallback otherwise.

## Render deployment

1. Create a Render Web Service from this repository.
2. Use `pip install -r requirements.txt` as the build command.
3. Use `uvicorn app.main:app --host 0.0.0.0 --port $PORT` as the start command.
4. Attach a managed PostgreSQL database and set `DATABASE_URL`.
5. Set `BOT_TOKEN`, `ADMIN_IDS`, `WEBHOOK_URL`, and `WEBHOOK_SECRET`.
6. Set `POLLING=false`.

`render.yaml` contains the same service configuration and health check path. The app sets the Telegram webhook at startup to:

```text
https://your-service.onrender.com/telegram/webhook
```

The public service URL—not a Render dashboard or log URL—is used for monitoring.

## UptimeRobot

Create an HTTP(s) monitor for:

```text
https://your-service.onrender.com/health
```

The endpoint is public, lightweight, and returns HTTP 200 with `{"status":"ok"}` while the process is healthy. UptimeRobot is only an HTTP monitoring/keep-alive source; it is not a Telegram service.

## Testing and updates

Run `python -m pytest` before deployment. Push code changes, let Render redeploy, and confirm `/health`, then test `/start`, conversion, `/admin`, and `/ctm` in Telegram. Database-backed settings and user data survive restarts and redeploys.

## Telegram compatibility note

Telegram custom emoji button icons depend on Bot API/client/account support. The bot preserves configured IDs and gracefully falls back to the normal label/Unicode icon when Telegram rejects an optional icon or style field. Telegram webhook requests are protected by `X-Telegram-Bot-Api-Secret-Token` when `WEBHOOK_SECRET` is configured.