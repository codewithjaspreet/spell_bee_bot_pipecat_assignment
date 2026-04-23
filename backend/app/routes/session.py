import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.bot.pipeline import create_spellbee_pipeline
from app.bot.stats_hub import stats_hub
from app.bot.state import get_game_state

router = APIRouter()

_current_task: asyncio.Task | None = None


@router.post("/new-session")
async def start_session():
    global _current_task

    if _current_task and not _current_task.done():
        _current_task.cancel()

    get_game_state().reset()

    _current_task = asyncio.create_task(create_spellbee_pipeline())

    return {"message": "Session started"}


@router.get("/game-stats")
async def get_game_stats():
    return get_game_state().get_stats()


@router.websocket("/game-stats/ws")
async def game_stats_ws(websocket: WebSocket):
    await websocket.accept()
    stats_hub.add(websocket)
    try:
        await websocket.send_json(get_game_state().get_stats())
        while True:
            message = await websocket.receive()
            if message.get("type") == "websocket.disconnect":
                break
    except WebSocketDisconnect:
        pass
    finally:
        stats_hub.remove(websocket)