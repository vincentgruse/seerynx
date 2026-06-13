import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from routers import (
    health,
    sightings,
    species,
    weather,
    attract,
    summary,
    photos,
    devices,
)
from services.feeder_status import monitor_loop
from config import ALLOWED_ORIGINS, STATIC_DIR
import os
import logging

logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Seerynx API starting up")
    monitor_task = asyncio.create_task(monitor_loop())
    yield
    monitor_task.cancel()
    logger.info("Seerynx API shutting down")


app = FastAPI(
    title="Seerynx API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Security middleware
env_hosts = os.environ.get("ALLOWED_HOSTS", "seerynx.local")
allowed_hosts = [host.strip() for host in env_hosts.split(",") if host.strip()]

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=allowed_hosts,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["X-API-Key", "Content-Type"],
    allow_credentials=False,
)


# Security headers middleware
@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


app.include_router(health.router)
app.include_router(sightings.router)
app.include_router(species.router)
app.include_router(weather.router)
app.include_router(attract.router)
app.include_router(summary.router)
app.include_router(photos.router)
app.include_router(devices.router)

if os.path.exists(STATIC_DIR):
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
