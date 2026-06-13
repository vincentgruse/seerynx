import asyncio
import logging
from datetime import datetime, timedelta, timezone
from fastapi import WebSocket

logger = logging.getLogger(__name__)

OFFLINE_THRESHOLD = timedelta(seconds=45)
MONITOR_INTERVAL = 10

_last_heartbeat: datetime | None = None
_last_broadcast_online: bool | None = None
_connections: set[WebSocket] = set()


def record_heartbeat() -> None:
    global _last_heartbeat
    _last_heartbeat = datetime.now(timezone.utc)


def get_status() -> dict:
    online = (
        _last_heartbeat is not None
        and datetime.now(timezone.utc) - _last_heartbeat < OFFLINE_THRESHOLD
    )
    return {
        "online": online,
        "last_heartbeat": _last_heartbeat.isoformat() if _last_heartbeat else None,
    }


async def register(websocket: WebSocket) -> None:
    _connections.add(websocket)


async def unregister(websocket: WebSocket) -> None:
    _connections.discard(websocket)


async def _broadcast(status: dict) -> None:
    dead = set()
    for ws in _connections:
        try:
            await ws.send_json(status)
        except Exception:
            dead.add(ws)
    _connections.difference_update(dead)


async def monitor_loop() -> None:
    global _last_broadcast_online
    while True:
        await asyncio.sleep(MONITOR_INTERVAL)
        status = get_status()
        if status["online"] != _last_broadcast_online:
            _last_broadcast_online = status["online"]
            logger.info(f"Feeder status changed: online={status['online']}")
            await _broadcast(status)
