import os

API_KEY = os.environ.get("SEERYNX_API_KEY", "")
API_KEY_NAME = "X-API-Key"
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "https://seerynx.local").split(",")
DISPLAY_TIMEZONE = os.environ.get("DISPLAY_TIMEZONE", "UTC")
PHOTOS_DIR = os.environ.get("PHOTOS_DIR", "/app/photos")
STATIC_DIR = os.environ.get("STATIC_DIR", "/app/static")

if not API_KEY:
    raise RuntimeError("SEERYNX_API_KEY environment variable not set")
