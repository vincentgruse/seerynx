import asyncio
import json
import logging
import threading
import queue
from aiomqtt import Client as MQTTClient, MqttError
from services.vision import process_frame
from services.audio import process_audio_chunk
from services.poster import (
    post_sighting,
    post_weather,
    post_heartbeat,
    is_known_species,
)
from http_server import run_health_server
from config import (
    MQTT_HOST,
    MQTT_PORT,
    MQTT_USER,
    MQTT_PASSWORD,
    TOPIC_CAMERA,
    TOPIC_AUDIO,
    TOPIC_WEATHER,
    TOPIC_HEARTBEAT,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

vision_queue: queue.Queue = queue.Queue(maxsize=10)
audio_queue: queue.Queue = queue.Queue(maxsize=20)


def vision_worker() -> None:
    logger.info("Vision worker started")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    while True:
        jpeg_bytes = vision_queue.get()
        try:
            result = loop.run_until_complete(process_frame(jpeg_bytes))
            if result:
                loop.run_until_complete(post_sighting(**result))
        except Exception as e:
            logger.error(f"Vision worker error: {e}")
        finally:
            vision_queue.task_done()


def audio_worker() -> None:
    logger.info("Audio worker started")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    while True:
        wav_bytes = audio_queue.get()
        try:
            detections = process_audio_chunk(wav_bytes)
            for detection in detections:
                if not loop.run_until_complete(
                    is_known_species(detection["common_name"])
                ):
                    logger.debug(
                        f"Ignoring non-bird detection: {detection['common_name']}"
                    )
                    continue
                loop.run_until_complete(post_sighting(**detection))
        except Exception as e:
            logger.error(f"Audio worker error: {e}")
        finally:
            audio_queue.task_done()


async def mqtt_listener() -> None:
    logger.info(f"Connecting to MQTT broker at {MQTT_HOST}:{MQTT_PORT}")
    reconnect_interval = 5

    while True:
        try:
            async with MQTTClient(
                hostname=MQTT_HOST,
                port=MQTT_PORT,
                username=MQTT_USER,
                password=MQTT_PASSWORD,
            ) as client:
                await client.subscribe(TOPIC_CAMERA)
                await client.subscribe(TOPIC_AUDIO)
                await client.subscribe(TOPIC_WEATHER)
                await client.subscribe(TOPIC_HEARTBEAT)
                logger.info("Subscribed to MQTT topics")

                async for message in client.messages:
                    topic = str(message.topic)
                    payload = bytes(message.payload)

                    if not payload:
                        logger.warning(f"Empty payload on topic {topic}, skipping")
                        continue

                    if topic == TOPIC_CAMERA:
                        if not vision_queue.full():
                            vision_queue.put(payload)
                        else:
                            logger.warning("Vision queue full, dropping frame")

                    elif topic == TOPIC_AUDIO:
                        if not audio_queue.full():
                            audio_queue.put(payload)
                        else:
                            logger.warning("Audio queue full, dropping chunk")

                    elif topic == TOPIC_WEATHER:
                        try:
                            data = json.loads(payload)
                            await post_weather(
                                temperature_c=data["temperature_c"],
                                humidity=data["humidity"],
                            )
                        except (json.JSONDecodeError, KeyError) as e:
                            logger.error(f"Invalid weather payload: {e}")

                    elif topic == TOPIC_HEARTBEAT:
                        await post_heartbeat()

        except MqttError as e:
            logger.error(
                f"MQTT connection lost: {e} — reconnecting in {reconnect_interval}s"
            )
            await asyncio.sleep(reconnect_interval)
        except Exception as e:
            logger.error(
                f"Unexpected MQTT error: {e} — reconnecting in {reconnect_interval}s"
            )
            await asyncio.sleep(reconnect_interval)


def main() -> None:
    # Start health server in background thread
    health_thread = threading.Thread(
        target=run_health_server,
        daemon=True,
        name="health-server",
    )
    health_thread.start()

    # Start vision worker thread with its own event loop
    vision_thread = threading.Thread(
        target=vision_worker,
        daemon=True,
        name="vision-worker",
    )
    vision_thread.start()

    # Start audio worker thread with its own event loop
    audio_thread = threading.Thread(
        target=audio_worker,
        daemon=True,
        name="audio-worker",
    )
    audio_thread.start()

    logger.info("All workers started, listening for MQTT messages")

    # Run MQTT listener as main async loop
    asyncio.run(mqtt_listener())


if __name__ == "__main__":
    main()
