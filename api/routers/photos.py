import os
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from config import PHOTOS_DIR

router = APIRouter(tags=["Photos"])
limiter = Limiter(key_func=get_remote_address)


@router.get("/api/photos/{path:path}")
@limiter.limit("120/minute")
async def get_photo(request: Request, path: str):
    full_path = os.path.realpath(os.path.join(PHOTOS_DIR, path))
    photos_root = os.path.realpath(PHOTOS_DIR)
    if os.path.commonpath([full_path, photos_root]) != photos_root:
        raise HTTPException(status_code=404, detail="Photo not found")
    if not os.path.isfile(full_path):
        raise HTTPException(status_code=404, detail="Photo not found")
    return FileResponse(full_path)
