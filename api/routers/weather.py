from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from slowapi import Limiter
from slowapi.util import get_remote_address
from database import get_db
from dependencies import verify_api_key
from models.requests import WeatherReading
from models.responses import WeatherResponse, WeatherCorrelation

router = APIRouter(tags=["Weather"])
limiter = Limiter(key_func=get_remote_address)


@router.get("/api/weather", response_model=list[WeatherResponse])
@limiter.limit("30/minute")
async def get_weather(
    request: Request,
    db: AsyncSession = Depends(get_db),
    key: str = Depends(verify_api_key),
):
    result = await db.execute(
        text(
            "SELECT * FROM weather WHERE timestamp > NOW() - INTERVAL '1 day' "
            "ORDER BY timestamp DESC LIMIT 288"
        )
    )
    rows = result.mappings().all()
    return [dict(r) for r in rows]


@router.get("/api/weather/correlation", response_model=list[WeatherCorrelation])
@limiter.limit("20/minute")
async def get_weather_correlation(
    request: Request,
    db: AsyncSession = Depends(get_db),
    key: str = Depends(verify_api_key),
):
    result = await db.execute(
        text(
            "SELECT w.temperature_c, w.humidity, COUNT(s.id) AS visit_count "
            "FROM weather w "
            "LEFT JOIN sightings s ON "
            "ABS(EXTRACT(EPOCH FROM (w.timestamp - s.timestamp))) < 1800 "
            "GROUP BY w.id, w.temperature_c, w.humidity "
            "ORDER BY w.timestamp DESC LIMIT 100"
        )
    )
    rows = result.mappings().all()
    return [dict(r) for r in rows]


@router.post("/api/weather", response_model=dict)
@limiter.limit("60/minute")
async def post_weather(
    request: Request,
    reading: WeatherReading,
    db: AsyncSession = Depends(get_db),
    key: str = Depends(verify_api_key),
):
    await db.execute(
        text(
            "INSERT INTO weather (temperature_c, humidity) "
            "VALUES (:temperature_c, :humidity)"
        ),
        {
            "temperature_c": reading.temperature_c,
            "humidity": reading.humidity,
        },
    )
    return {"status": "ok"}
