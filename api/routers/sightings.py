import os
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import Optional
from config import PHOTOS_DIR, DISPLAY_TIMEZONE
from database import get_db
from dependencies import verify_api_key
from models.requests import Sighting, DeleteSightingsRequest, DeleteSpeciesRequest
from models.responses import (
    SightingResponse,
    HeatmapEntry,
    StreakResponse,
    LifeListEntry,
    CalendarEntry,
)

router = APIRouter(tags=["Sightings"])
limiter = Limiter(key_func=get_remote_address)


@router.get("/api/sightings", response_model=list[SightingResponse])
@limiter.limit("60/minute")
async def get_sightings(
    request: Request,
    limit: int = 50,
    date: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    key: str = Depends(verify_api_key),
):
    limit = min(limit, 200)
    if date:
        result = await db.execute(
            text(
                "SELECT s.*, si.photo_path AS species_photo_path FROM sightings s "
                "LEFT JOIN species_info si ON s.common_name = si.common_name "
                "WHERE DATE(s.timestamp) = :date "
                "ORDER BY s.timestamp DESC LIMIT :limit"
            ),
            {"date": date, "limit": limit},
        )
    else:
        result = await db.execute(
            text(
                "SELECT s.*, si.photo_path AS species_photo_path FROM sightings s "
                "LEFT JOIN species_info si ON s.common_name = si.common_name "
                "ORDER BY s.timestamp DESC LIMIT :limit"
            ),
            {"limit": limit},
        )
    rows = result.mappings().all()
    return [dict(r) for r in rows]


@router.get("/api/sightings/today", response_model=list[SightingResponse])
@limiter.limit("60/minute")
async def get_today_feeder(
    request: Request,
    db: AsyncSession = Depends(get_db),
    key: str = Depends(verify_api_key),
):
    result = await db.execute(
        text(
            "SELECT s.*, si.photo_path AS species_photo_path FROM sightings s "
            "LEFT JOIN species_info si ON s.common_name = si.common_name "
            "WHERE DATE(s.timestamp AT TIME ZONE :tz) = DATE(now() AT TIME ZONE :tz) "
            "AND s.source = 'vision' ORDER BY s.timestamp DESC"
        ),
        {"tz": DISPLAY_TIMEZONE},
    )
    rows = result.mappings().all()
    return [dict(r) for r in rows]


@router.get("/api/sightings/nearby", response_model=list[SightingResponse])
@limiter.limit("60/minute")
async def get_nearby(
    request: Request,
    db: AsyncSession = Depends(get_db),
    key: str = Depends(verify_api_key),
):
    result = await db.execute(
        text(
            "SELECT s.*, si.photo_path AS species_photo_path FROM sightings s "
            "LEFT JOIN species_info si ON s.common_name = si.common_name "
            "WHERE DATE(s.timestamp AT TIME ZONE :tz) = DATE(now() AT TIME ZONE :tz) "
            "AND s.source = 'audio' ORDER BY s.timestamp DESC"
        ),
        {"tz": DISPLAY_TIMEZONE},
    )
    rows = result.mappings().all()
    return [dict(r) for r in rows]


@router.get("/api/sightings/heatmap", response_model=list[HeatmapEntry])
@limiter.limit("30/minute")
async def get_heatmap(
    request: Request,
    db: AsyncSession = Depends(get_db),
    key: str = Depends(verify_api_key),
):
    result = await db.execute(
        text(
            "SELECT EXTRACT(HOUR FROM timestamp)::int AS hour, source, COUNT(*) AS count "
            "FROM sightings GROUP BY hour, source ORDER BY hour"
        )
    )
    rows = result.mappings().all()
    counts: dict[str, dict[str, int]] = {
        str(h).zfill(2): {"audio_count": 0, "vision_count": 0} for h in range(24)
    }
    for r in rows:
        hour = str(r["hour"]).zfill(2)
        if r["source"] == "audio":
            counts[hour]["audio_count"] = r["count"]
        elif r["source"] == "vision":
            counts[hour]["vision_count"] = r["count"]
    return [{"hour": hour, **c} for hour, c in counts.items()]


@router.get("/api/sightings/streak", response_model=StreakResponse)
@limiter.limit("30/minute")
async def get_streak(
    request: Request,
    db: AsyncSession = Depends(get_db),
    key: str = Depends(verify_api_key),
):
    result = await db.execute(
        text(
            "SELECT DISTINCT DATE(timestamp AT TIME ZONE :tz) AS day FROM sightings "
            "ORDER BY day DESC"
        ),
        {"tz": DISPLAY_TIMEZONE},
    )
    rows = result.fetchall()

    if not rows:
        return {"streak": 0}

    streak = 1
    days = [r[0] for r in rows]
    for i in range(1, len(days)):
        if (days[i - 1] - days[i]).days == 1:
            streak += 1
        else:
            break
    return {"streak": streak}


@router.get("/api/sightings/first", response_model=list[LifeListEntry])
@limiter.limit("30/minute")
async def get_life_list(
    request: Request,
    db: AsyncSession = Depends(get_db),
    key: str = Depends(verify_api_key),
):
    result = await db.execute(
        text(
            "SELECT s.common_name, s.scientific_name, MIN(s.timestamp) AS first_seen, "
            "si.photo_path AS species_photo_path "
            "FROM sightings s "
            "LEFT JOIN species_info si ON s.common_name = si.common_name "
            "GROUP BY s.common_name, s.scientific_name, si.photo_path "
            "ORDER BY first_seen DESC"
        )
    )
    rows = result.mappings().all()
    return [dict(r) for r in rows]


@router.get("/api/sightings/calendar", response_model=list[CalendarEntry])
@limiter.limit("30/minute")
async def get_calendar(
    request: Request,
    db: AsyncSession = Depends(get_db),
    key: str = Depends(verify_api_key),
):
    result = await db.execute(
        text(
            "SELECT DATE(timestamp AT TIME ZONE :tz) AS day, COUNT(*) AS count "
            "FROM sightings WHERE source = 'vision' "
            "GROUP BY day ORDER BY day"
        ),
        {"tz": DISPLAY_TIMEZONE},
    )
    rows = result.mappings().all()
    return [{"day": str(r["day"]), "count": r["count"]} for r in rows]


@router.delete("/api/sightings", response_model=dict)
@limiter.limit("30/minute")
async def delete_sightings(
    request: Request,
    payload: DeleteSightingsRequest,
    db: AsyncSession = Depends(get_db),
    key: str = Depends(verify_api_key),
):
    result = await db.execute(
        text(
            "SELECT photo_path FROM sightings "
            "WHERE id = ANY(:ids) AND photo_path IS NOT NULL"
        ),
        {"ids": payload.ids},
    )
    photo_paths = [row[0] for row in result.fetchall()]

    delete_result = await db.execute(
        text("DELETE FROM sightings WHERE id = ANY(:ids)"),
        {"ids": payload.ids},
    )

    for photo_path in photo_paths:
        photo_file = os.path.join(PHOTOS_DIR, photo_path)
        if os.path.exists(photo_file):
            os.remove(photo_file)

    return {"deleted": delete_result.rowcount}


@router.delete("/api/sightings/species", response_model=dict)
@limiter.limit("30/minute")
async def delete_species(
    request: Request,
    payload: DeleteSpeciesRequest,
    db: AsyncSession = Depends(get_db),
    key: str = Depends(verify_api_key),
):
    result = await db.execute(
        text(
            "SELECT photo_path FROM sightings "
            "WHERE common_name = ANY(:common_names) AND photo_path IS NOT NULL"
        ),
        {"common_names": payload.common_names},
    )
    photo_paths = [row[0] for row in result.fetchall()]

    delete_result = await db.execute(
        text("DELETE FROM sightings WHERE common_name = ANY(:common_names)"),
        {"common_names": payload.common_names},
    )

    for photo_path in photo_paths:
        photo_file = os.path.join(PHOTOS_DIR, photo_path)
        if os.path.exists(photo_file):
            os.remove(photo_file)

    return {"deleted": delete_result.rowcount}


@router.post("/api/sightings", response_model=dict)
@limiter.limit("60/minute")
async def post_sighting(
    request: Request,
    sighting: Sighting,
    db: AsyncSession = Depends(get_db),
    key: str = Depends(verify_api_key),
):
    await db.execute(
        text(
            "INSERT INTO sightings "
            "(common_name, scientific_name, confidence, source, photo_path, lat, lon) "
            "VALUES (:common_name, :scientific_name, :confidence, :source, :photo_path, :lat, :lon)"
        ),
        {
            "common_name": sighting.common_name,
            "scientific_name": sighting.scientific_name,
            "confidence": sighting.confidence,
            "source": sighting.source,
            "photo_path": sighting.photo_path,
            "lat": sighting.lat,
            "lon": sighting.lon,
        },
    )
    return {"status": "ok"}
