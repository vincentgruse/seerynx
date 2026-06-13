import secrets
from fastapi import APIRouter, Depends, Request, WebSocket, WebSocketDisconnect
from slowapi import Limiter
from slowapi.util import get_remote_address
from config import API_KEY, API_KEY_NAME
from dependencies import verify_api_key
from services import feeder_status

router = APIRouter(tags=["Devices"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/api/devices/feeder/heartbeat")
@limiter.limit("60/minute")
async def feeder_heartbeat(
    request: Request,
    key: str = Depends(verify_api_key),
):
    feeder_status.record_heartbeat()
    return {"status": "ok"}


@router.websocket("/api/devices/feeder/ws")
async def feeder_status_ws(websocket: WebSocket):
    key = websocket.headers.get(API_KEY_NAME, "")
    if not secrets.compare_digest(key, API_KEY):
        await websocket.close(code=1008)
        return

    await websocket.accept()
    await feeder_status.register(websocket)
    try:
        await websocket.send_json(feeder_status.get_status())
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        await feeder_status.unregister(websocket)
