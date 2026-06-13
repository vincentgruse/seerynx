from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from config import API_KEY, API_KEY_NAME
import secrets

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)


async def verify_api_key(key: str = Security(api_key_header)) -> str:
    if not secrets.compare_digest(key, API_KEY):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )
    return key
