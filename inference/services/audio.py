import logging
import tempfile
import os
from pathlib import Path
from birdnet import load as load_birdnet
from config import BIRDNET_THRESHOLD

logger = logging.getLogger(__name__)

_model = None


def get_model():
    global _model
    if _model is None:
        logger.info("Loading BirdNET model...")
        try:
            _model = load_birdnet("acoustic", "2.4", "tf")
            logger.info(f"BirdNET model loaded — {_model.n_species} species")
        except Exception as e:
            logger.error(f"Failed to load BirdNET model: {e}")
            raise
    return _model


def process_audio_chunk(wav_bytes: bytes) -> list[dict]:
    if not wav_bytes or len(wav_bytes) < 44:  # WAV header is 44 bytes minimum
        logger.warning("Audio chunk too small, skipping")
        return []

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False,
            dir="/tmp",
        ) as f:
            f.write(wav_bytes)
            tmp_path = f.name

        model = get_model()
        result = model.predict(
            tmp_path,
            default_confidence_threshold=BIRDNET_THRESHOLD,
            top_k=5,
        )

        df = result.to_dataframe()
        detections = []

        for _, row in df.iterrows():
            label = str(row["species_name"])
            if "_" in label:
                scientific_name, common_name = label.split("_", 1)
            else:
                common_name = label
                scientific_name = None

            # Sanitize species names
            common_name = common_name.strip()[:255]
            if scientific_name:
                scientific_name = scientific_name.strip()[:255]

            detections.append(
                {
                    "common_name": common_name,
                    "scientific_name": scientific_name,
                    "confidence": round(float(row["confidence"]), 4),
                    "source": "audio",
                    "photo_path": None,
                }
            )

        if detections:
            logger.info(f"BirdNET detected {len(detections)} species")

        return detections

    except Exception as e:
        logger.error(f"BirdNET inference failed: {e}")
        return []
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except Exception as e:
                logger.warning(f"Failed to clean up temp file {tmp_path}: {e}")
