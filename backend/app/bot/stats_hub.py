"""Broadcast ``get_stats()`` payloads to connected WebSocket clients (push, not poll)."""

from __future__ import annotations

import asyncio
from typing import Set

from fastapi import WebSocket
from loguru import logger


class StatsHub:
    def __init__(self) -> None:
        self._clients: Set[WebSocket] = set()

    def add(self, websocket: WebSocket) -> None:
        self._clients.add(websocket)

    def remove(self, websocket: WebSocket) -> None:
        self._clients.discard(websocket)

    async def broadcast(self, payload: dict) -> None:
        if not self._clients:
            return
        stale: list[WebSocket] = []
        for ws in list(self._clients):
            try:
                await ws.send_json(payload)
            except Exception as exc:
                logger.debug("Stats WebSocket send failed, dropping client: {}", exc)
                stale.append(ws)
        for ws in stale:
            self.remove(ws)

    def emit_stats(self, payload: dict) -> None:
        """Schedule a broadcast from sync or async code when an event loop is running."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return
        loop.create_task(self.broadcast(payload))


stats_hub = StatsHub()
