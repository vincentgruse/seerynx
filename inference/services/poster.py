import httpx
import logging
from urllib.parse import quote
from config import API_BASE_URL, API_KEY

logger = logging.getLogger(__name__)

HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json",
}


async def is_known_species(common_name: str) -> bool:
    """Check whether common_name exists in the species_info table, to filter
    out non-bird BirdNET detections (e.g. Human, Dog, Engine, Siren, Noise)."""
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(3.0)) as client:
            r = await client.get(
                f"{API_BASE_URL}/api/species/{quote(common_name, safe='')}",
                headers=HEADERS,
            )
            return r.status_code == 200
    except Exception as e:
        logger.debug(f"Could not verify species {common_name}: {e}")
        return True


async def post_sighting(
    common_name: str,
    scientific_name: str | None,
    confidence: float,
    source: str,
    photo_path: str | None = None,
):
    payload = {
        "common_name": common_name,
        "scientific_name": scientific_name,
        "confidence": round(confidence, 4),
        "source": source,
        "photo_path": photo_path,
    }
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(5.0)) as client:
            r = await client.post(
                f"{API_BASE_URL}/api/sightings",
                json=payload,
                headers=HEADERS,
            )
            r.raise_for_status()
            logger.info(
                f"Posted sighting: {common_name} ({source}) confidence={confidence:.2f}"
            )
    except httpx.HTTPStatusError as e:
        logger.error(
            f"API rejected sighting: {e.response.status_code} - {e.response.text}"
        )
    except httpx.RequestError as e:
        logger.error(f"Failed to reach API: {e}")
    except Exception as e:
        logger.error(f"Unexpected error posting sighting: {e}")


async def post_heartbeat():
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(5.0)) as client:
            r = await client.post(
                f"{API_BASE_URL}/api/devices/feeder/heartbeat",
                headers=HEADERS,
            )
            r.raise_for_status()
    except httpx.HTTPStatusError as e:
        logger.error(
            f"API rejected heartbeat: {e.response.status_code} - {e.response.text}"
        )
    except httpx.RequestError as e:
        logger.error(f"Failed to reach API: {e}")
    except Exception as e:
        logger.error(f"Unexpected error posting heartbeat: {e}")


async def post_weather(temperature_c: float, humidity: float):
    payload = {
        "temperature_c": temperature_c,
        "humidity": humidity,
    }
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(5.0)) as client:
            r = await client.post(
                f"{API_BASE_URL}/api/weather",
                json=payload,
                headers=HEADERS,
            )
            r.raise_for_status()
            logger.info(f"Posted weather: {payload}")
    except httpx.HTTPStatusError as e:
        logger.error(
            f"API rejected weather: {e.response.status_code} - {e.response.text}"
        )
    except httpx.RequestError as e:
        logger.error(f"Failed to reach API: {e}")
    except Exception as e:
        logger.error(f"Unexpected error posting weather: {e}")
