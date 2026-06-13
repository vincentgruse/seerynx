from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from slowapi import Limiter
from slowapi.util import get_remote_address
from database import get_db
from dependencies import verify_api_key
from models.responses import WeeklyEntry

router = APIRouter(tags=["Summary"])
limiter = Limiter(key_func=get_remote_address)


@router.get("/api/summary/weekly", response_model=list[WeeklyEntry])
@limiter.limit("30/minute")
async def get_weekly_summary(
    request: Request,
    db: AsyncSession = Depends(get_db),
    key: str = Depends(verify_api_key),
):
    result = await db.execute(
        text(
            "SELECT TO_CHAR(timestamp, 'IYYY-IW') AS week, "
            "COUNT(*) AS visits, "
            "COUNT(DISTINCT common_name) AS species_count "
            "FROM sightings WHERE source = 'vision' "
            "GROUP BY week ORDER BY week DESC LIMIT 8"
        )
    )
    rows = result.mappings().all()
    return [dict(r) for r in rows]
