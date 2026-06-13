import io
import time
import logging
import numpy as np
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput
import paho.mqtt.client as mqtt
from config import (
    MQTT_HOST,
    MQTT_PORT,
    MQTT_USER,
    MQTT_PASSWORD,
    TOPIC_CAMERA,
    CAMERA_RESOLUTION,
    MOTION_THRESHOLD,
    MOTION_MIN_AREA,
    MOTION_SUSTAIN_FRAMES,
    MOTION_COOLDOWN,
    BURST_COUNT,
)
from vision import is_animal_present

logger = logging.getLogger(__name__)


def run_camera(mqtt_client: mqtt.Client):
    logger.info("Starting camera pipeline")

    picam = Picamera2()
    config = picam.create_video_configuration(
        main={"size": CAMERA_RESOLUTION, "format": "RGB888"},
        lores={"size": (320, 240), "format": "YUV420"},
    )
    picam.configure(config)
    picam.start()
    time.sleep(2)  # warm up

    prev_frame = None
    motion_streak = 0
    logger.info("Camera running, watching for motion")

    while True:
        # Grab low-res frame for motion detection
        lores = picam.capture_array("lores")
        gray = lores[:240, :320]  # Y channel from YUV420

        if prev_frame is not None:
            diff = np.abs(gray.astype(np.int16) - prev_frame.astype(np.int16))
            motion_pixels = np.sum(diff > MOTION_THRESHOLD)

            if motion_pixels > MOTION_MIN_AREA:
                motion_streak += 1
            else:
                motion_streak = 0

            if motion_streak >= MOTION_SUSTAIN_FRAMES:
                logger.info(
                    f"Sustained motion detected ({motion_pixels} pixels), checking for animal"
                )
                frame = picam.capture_array("main")
                animal_present, score = is_animal_present(frame)

                if animal_present:
                    logger.info(
                        f"Animal confirmed (score={score:.2f}), capturing burst"
                    )
                    for i in range(BURST_COUNT):
                        buf = io.BytesIO()
                        picam.capture_file(buf, format="jpeg")
                        jpeg_bytes = buf.getvalue()
                        mqtt_client.publish(TOPIC_CAMERA, jpeg_bytes, qos=1)
                        logger.info(
                            f"Published frame {i+1}/{BURST_COUNT} ({len(jpeg_bytes)} bytes)"
                        )
                        time.sleep(0.5)

                    # cooldown to avoid re-triggering
                    time.sleep(MOTION_COOLDOWN)
                else:
                    logger.info("No animal detected, skipping burst")

                prev_frame = None
                motion_streak = 0
                continue

        prev_frame = gray.copy()
        time.sleep(0.1)
