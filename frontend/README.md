# Spell Bee Bot (frontend)

Next.js UI: join a Daily room, start a session against the backend, and show live score/rounds via WebSocket.

## Requirements

- Node.js 18+ (20+ recommended)
- npm (or pnpm/yarn if you adapt commands)

## Setup

1. From this directory:

   ```bash
   npm install
   ```

2. Optional: create `.env.local` if defaults are wrong for your machine:

   | Variable | Purpose |
   |----------|---------|
   | `NEXT_PUBLIC_DAILY_ROOM_URL` | Daily room the player joins (must match backend bot room) |
   | `NEXT_PUBLIC_API_WS` | WebSocket origin for stats, e.g. `ws://localhost:8000` (no trailing slash). Defaults to `ws://localhost:8000` |
   | `NEXT_PUBLIC_GAME_STATS_WS_URL` | Full stats WebSocket URL; overrides the URL built from `NEXT_PUBLIC_API_WS` |

   The app calls the HTTP API at `http://localhost:8000/api` by default. To change that, edit `API_BASE` in `app/page.tsx` or add a `NEXT_PUBLIC_*` variable and wire it in code.

3. Start the dev server:

   ```bash
   npm run dev
   ```

   Open [http://localhost:3000](http://localhost:3000).

## Run order

1. Start the **backend** (see `backend/README.md`).
2. Start this frontend.
3. Click **Start Game** so the backend spawns the bot and you join the Daily room.

## Production

Use `npm run build` then `npm run start`. Use `wss://` for `NEXT_PUBLIC_API_WS` (or the full stats URL) when the site is served over HTTPS.
