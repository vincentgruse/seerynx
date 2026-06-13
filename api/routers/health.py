from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from slowapi import Limiter
from slowapi.util import get_remote_address
from datetime import datetime, timezone
from database import get_db
from dependencies import verify_api_key
from models.responses import HealthResponse, HealthModelsResponse, ModelStatus
import httpx
import os

router = APIRouter(tags=["Health"])
limiter = Limiter(key_func=get_remote_address)

INFERENCE_URL = os.environ.get("INFERENCE_SERVICE_URL", "http://seerynx-inference:8001")


@router.get("/api/health", response_model=HealthResponse)
@limiter.limit("30/minute")
async def health(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        text("SELECT timestamp FROM sightings ORDER BY timestamp DESC LIMIT 1")
    )
    row = result.fetchone()
    return {
        "status": "ok",
        "last_sighting": row[0].isoformat() if row else None,
        "uptime": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/api/health/models", response_model=HealthModelsResponse)
@limiter.limit("10/minute")
async def health_models(request: Request, key: str = Depends(verify_api_key)):
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{INFERENCE_URL}/health",
                timeout=3,
            )
            r.raise_for_status()
            data = r.json()
            return {
                "status": "ok",
                "models": ModelStatus(
                    birds_v1=data.get("birds_v1", False),
                    efficientdet_lite0=data.get("efficientdet_lite0", False),
                ),
            }
    except Exception:
        return {
            "status": "degraded",
            "models": ModelStatus(birds_v1=False, efficientdet_lite0=False),
        }
