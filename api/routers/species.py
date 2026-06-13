from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from slowapi import Limiter
from slowapi.util import get_remote_address
from database import get_db
from dependencies import verify_api_key
from models.responses import SpeciesInfoResponse

router = APIRouter(tags=["Species"])
limiter = Limiter(key_func=get_remote_address)


@router.get(
    "/api/species/by-scientific-name/{scientific_name}",
    response_model=SpeciesInfoResponse,
)
@limiter.limit("60/minute")
async def get_species_by_scientific_name(
    request: Request,
    scientific_name: str,
    db: AsyncSession = Depends(get_db),
    key: str = Depends(verify_api_key),
):
    result = await db.execute(
        text("SELECT * FROM species_info WHERE scientific_name = :scientific_name"),
        {"scientific_name": scientific_name},
    )
    row = result.mappings().fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Species not found")
    return dict(row)


@router.get("/api/species/{common_name}", response_model=SpeciesInfoResponse)
@limiter.limit("60/minute")
async def get_species(
    request: Request,
    common_name: str,
    db: AsyncSession = Depends(get_db),
    key: str = Depends(verify_api_key),
):
    result = await db.execute(
        text("SELECT * FROM species_info WHERE common_name = :common_name"),
        {"common_name": common_name},
    )
    row = result.mappings().fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Species not found")
    return dict(row)
