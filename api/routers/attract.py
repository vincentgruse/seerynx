from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from slowapi import Limiter
from slowapi.util import get_remote_address
from config import DISPLAY_TIMEZONE
from database import get_db
from dependencies import verify_api_key
from models.responses import AttractSuggestion

router = APIRouter(tags=["Attract"])
limiter = Limiter(key_func=get_remote_address)


@router.get("/api/attract", response_model=list[AttractSuggestion])
@limiter.limit("30/minute")
async def get_attract(
    request: Request,
    db: AsyncSession = Depends(get_db),
    key: str = Depends(verify_api_key),
):
    audio_result = await db.execute(
        text(
            "SELECT DISTINCT common_name FROM sightings "
            "WHERE DATE(timestamp AT TIME ZONE :tz) = DATE(now() AT TIME ZONE :tz) "
            "AND source = 'audio'"
        ),
        {"tz": DISPLAY_TIMEZONE},
    )
    feeder_result = await db.execute(
        text(
            "SELECT DISTINCT common_name FROM sightings "
            "WHERE DATE(timestamp AT TIME ZONE :tz) = DATE(now() AT TIME ZONE :tz) "
            "AND source = 'vision'"
        ),
        {"tz": DISPLAY_TIMEZONE},
    )

    audio_names = {r[0] for r in audio_result.fetchall()}
    feeder_names = {r[0] for r in feeder_result.fetchall()}
    nearby_only = audio_names - feeder_names

    suggestions = []
    for name in nearby_only:
        info_result = await db.execute(
            text("SELECT * FROM species_info WHERE common_name = :name"),
            {"name": name},
        )
        row = info_result.mappings().fetchone()
        if row:
            suggestions.append(
                {
                    "common_name": name,
                    "food": row["food"],
                    "feeder_types": row["feeder_types"],
                }
            )

    return suggestions
