import time
import logging
import subprocess
import paho.mqtt.client as mqtt
from config import (
    TOPIC_AUDIO,
    AUDIO_DEVICE,
    AUDIO_SAMPLE_RATE,
    AUDIO_CHANNELS,
    AUDIO_CHUNK_SECONDS,
)

logger = logging.getLogger(__name__)


def find_audio_device() -> str:
    """Auto-detect first USB audio capture device, fall back to config."""
    try:
        result = subprocess.run(["arecord", "-l"], capture_output=True, text=True)
        for line in result.stdout.split("\n"):
            if any(k in line.lower() for k in ["usb", "uac", "mic", "audio"]):
                parts = line.split(":")[0].split()
                if len(parts) >= 2 and parts[-1].isdigit():
                    device = f"hw:{parts[-1]},0"
                    logger.info(
                        f"Auto-detected audio device: {device} ({line.strip()})"
                    )
                    return device
    except Exception as e:
        logger.warning(f"Audio device auto-detect failed: {e}")
    logger.info(f"Falling back to configured audio device: {AUDIO_DEVICE}")
    return AUDIO_DEVICE


def record_chunk(device: str) -> bytes | None:
    """Record a WAV chunk using arecord and return bytes."""
    cmd = [
        "arecord",
        "-D",
        device,
        "-f",
        "S16_LE",
        "-r",
        str(AUDIO_SAMPLE_RATE),
        "-c",
        str(AUDIO_CHANNELS),
        "-d",
        str(AUDIO_CHUNK_SECONDS),
        "--quiet",
        "-t",
        "wav",
        "/dev/stdout",
    ]
    try:
        result = subprocess.run(
            cmd, capture_output=True, timeout=AUDIO_CHUNK_SECONDS + 2
        )
        return result.stdout if result.stdout else None
    except subprocess.TimeoutExpired:
        logger.error("arecord timed out")
        return None
    except Exception as e:
        logger.error(f"arecord failed: {e}")
        return None


def run_audio(mqtt_client: mqtt.Client):
    device = find_audio_device()
    logger.info(f"Starting audio pipeline on {device} at {AUDIO_SAMPLE_RATE}Hz")

    while True:
        wav_bytes = record_chunk(device)
        if wav_bytes and len(wav_bytes) > 44:  # WAV header is 44 bytes minimum
            mqtt_client.publish(TOPIC_AUDIO, wav_bytes, qos=0)
            logger.debug(f"Published audio chunk ({len(wav_bytes)} bytes)")
        else:
            logger.warning("Empty audio chunk, retrying in 1s")
            # Re-detect device in case it changed
            device = find_audio_device()
            time.sleep(1)
