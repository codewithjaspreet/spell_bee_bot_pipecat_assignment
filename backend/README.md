# Spell Bee Bot (backend)

FastAPI API plus Pipecat voice pipeline (Daily, Deepgram STT/TTS).

## Requirements

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommended) or another tool to install dependencies from `pyproject.toml`

## Setup

1. From this directory, create `.env` with:

   | Variable | Purpose |
   |----------|---------|
   | `DEEPGRAM_API_KEY` | Deepgram speech API |
   | `DAILY_API_KEY` | Daily REST API |
   | `DAILY_SAMPLE_ROOM_URL` | Daily room URL the bot joins (same room the frontend uses) |

2. Install and sync (optional: pin Python for uv):

   ```bash
   UV_PYTHON=/opt/homebrew/bin/python3.11 uv sync
   ```

3. Run the API:

   ```bash
   UV_PYTHON=/opt/homebrew/bin/python3.11 uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   Or, with dependencies already installed:

   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   Run this from the `backend` directory so `app` resolves correctly.

## API (quick reference)

- `POST /api/new-session` – reset game state and start the voice pipeline task
- `GET /api/game-stats` – current `rounds` and `score` (JSON)
- `WebSocket /api/game-stats/ws` – same stats pushed when state changes

## Notes

- First Pipecat run may download VAD / turn-detection model weights; allow network access.
- Ensure `DAILY_SAMPLE_ROOM_URL` matches the room URL configured in the frontend.
