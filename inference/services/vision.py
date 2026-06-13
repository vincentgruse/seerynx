import io
import os
import logging
import numpy as np
from PIL import Image
from datetime import datetime, timezone
from models.loader import (
    get_birds_interpreter,
    get_efficientdet_interpreter,
    get_labels,
    resolve_common_name,
)
from config import DETECTION_THRESHOLD, CLASSIFICATION_THRESHOLD, PHOTOS_DIR

logger = logging.getLogger(__name__)

BIRD_CLASS_ID = 16  # COCO class ID for "bird"


def preprocess_for_efficientdet(image: Image.Image) -> np.ndarray:
    img = image.convert("RGB").resize((320, 320))
    return np.expand_dims(np.array(img, dtype=np.uint8), axis=0)


def preprocess_for_birds_v1(image: Image.Image) -> np.ndarray:
    img = image.convert("RGB").resize((224, 224))
    arr = np.array(img, dtype=np.float32) / 127.5 - 1.0
    return np.expand_dims(arr, axis=0)


def detect_bird(image: Image.Image) -> tuple[bool, float]:
    try:
        interpreter = get_efficientdet_interpreter()
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        input_data = preprocess_for_efficientdet(image)
        interpreter.set_tensor(input_details[0]["index"], input_data)
        interpreter.invoke()

        classes = interpreter.get_tensor(output_details[1]["index"])[0]
        scores = interpreter.get_tensor(output_details[2]["index"])[0]

        for i, score in enumerate(scores):
            if score >= DETECTION_THRESHOLD and int(classes[i]) == BIRD_CLASS_ID:
                return True, float(score)
        return False, 0.0
    except Exception as e:
        logger.error(f"EfficientDet inference failed: {e}")
        return False, 0.0


async def classify_bird(image: Image.Image) -> tuple[str, str | None, float]:
    try:
        interpreter = get_birds_interpreter()
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        input_data = preprocess_for_birds_v1(image)
        interpreter.set_tensor(input_details[0]["index"], input_data)
        interpreter.invoke()

        output = interpreter.get_tensor(output_details[0]["index"])[0]
        top_idx = int(np.argmax(output))
        confidence = float(output[top_idx])

        labels = get_labels()
        scientific_name = labels.get(top_idx, "Unknown")
        common_name = await resolve_common_name(scientific_name)

        return common_name, scientific_name, confidence
    except Exception as e:
        logger.error(f"AIY Birds V1 inference failed: {e}")
        return "Unknown", None, 0.0


def save_photo(image: Image.Image, common_name: str) -> str | None:
    try:
        os.makedirs(PHOTOS_DIR, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        safe_name = (
            common_name.replace(" ", "_").replace("/", "-").replace("..", "").strip(".")
        )
        filename = f"{timestamp}_{safe_name}.jpg"
        path = os.path.join(PHOTOS_DIR, filename)
        image.save(path, "JPEG", quality=85)
        return filename
    except Exception as e:
        logger.error(f"Failed to save photo: {e}")
        return None


async def process_frame(jpeg_bytes: bytes) -> dict | None:
    try:
        image = Image.open(io.BytesIO(jpeg_bytes))
    except Exception as e:
        logger.error(f"Failed to decode image: {e}")
        return None

    bird_detected, detection_score = detect_bird(image)
    if not bird_detected:
        logger.debug("No bird detected")
        return None

    logger.info(f"Bird detected (score={detection_score:.2f}), classifying...")

    common_name, scientific_name, confidence = await classify_bird(image)

    if confidence < CLASSIFICATION_THRESHOLD:
        logger.info(f"Classification confidence too low: {confidence:.2f}")
        return None

    photo_filename = save_photo(image, common_name)

    return {
        "common_name": common_name,
        "scientific_name": scientific_name,
        "confidence": confidence,
        "source": "vision",
        "photo_path": photo_filename,
    }
