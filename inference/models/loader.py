import os
import csv
import logging
import httpx
from urllib.parse import quote
from ai_edge_litert.interpreter import Interpreter
from config import (
    BIRDS_V1_MODEL,
    EFFICIENTDET_MODEL,
    BIRDS_LABELS_PATH,
    API_BASE_URL,
    API_KEY,
)

logger = logging.getLogger(__name__)

_birds_interpreter = None
_efficientdet_interpreter = None
_labels = None

HEADERS = {
    "X-API-Key": API_KEY,
}


def load_labels() -> dict:
    if not os.path.exists(BIRDS_LABELS_PATH):
        raise FileNotFoundError(f"Label file not found: {BIRDS_LABELS_PATH}")

    scientific_names = {}
    with open(BIRDS_LABELS_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                idx = int(row["id"])
                scientific_names[idx] = row["name"].strip()
            except (ValueError, KeyError) as e:
                logger.warning(f"Skipping malformed label row: {row} — {e}")

    logger.info(f"Loaded {len(scientific_names)} scientific names from label file")
    return scientific_names


def get_labels() -> dict:
    global _labels
    if _labels is None:
        _labels = load_labels()
    return _labels


async def resolve_common_name(scientific_name: str) -> str:
    """Query the Seerynx API to resolve scientific name to common name."""
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(3.0)) as client:
            r = await client.get(
                f"{API_BASE_URL}/api/species/by-scientific-name/{quote(scientific_name, safe='')}",
                headers=HEADERS,
            )
            if r.status_code == 200:
                data = r.json()
                return data.get("common_name", scientific_name)
            return scientific_name
    except Exception as e:
        logger.debug(f"Could not resolve common name for {scientific_name}: {e}")
        return scientific_name


def get_birds_interpreter() -> Interpreter:
    global _birds_interpreter
    if _birds_interpreter is None:
        if not os.path.exists(BIRDS_V1_MODEL):
            raise FileNotFoundError(f"Birds V1 model not found: {BIRDS_V1_MODEL}")
        logger.info(f"Loading AIY Birds V1 model from {BIRDS_V1_MODEL}")
        _birds_interpreter = Interpreter(model_path=BIRDS_V1_MODEL)
        _birds_interpreter.allocate_tensors()
        logger.info("AIY Birds V1 model loaded")
    return _birds_interpreter


def get_efficientdet_interpreter() -> Interpreter:
    global _efficientdet_interpreter
    if _efficientdet_interpreter is None:
        if not os.path.exists(EFFICIENTDET_MODEL):
            raise FileNotFoundError(
                f"EfficientDet model not found: {EFFICIENTDET_MODEL}"
            )
        logger.info(f"Loading EfficientDet model from {EFFICIENTDET_MODEL}")
        _efficientdet_interpreter = Interpreter(model_path=EFFICIENTDET_MODEL)
        _efficientdet_interpreter.allocate_tensors()
        logger.info("EfficientDet model loaded")
    return _efficientdet_interpreter


def models_loaded() -> dict:
    return {
        "birds_v1": os.path.exists(BIRDS_V1_MODEL),
        "efficientdet_lite0": os.path.exists(EFFICIENTDET_MODEL),
    }
