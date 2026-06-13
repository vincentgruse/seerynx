import logging
import threading
import time
import paho.mqtt.client as mqtt
from config import MQTT_HOST, MQTT_PORT, MQTT_USER, MQTT_PASSWORD
from camera import run_camera
from audio import run_audio
from weather import run_weather
from heartbeat import run_heartbeat

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)


def create_mqtt_client():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.username_pw_set(MQTT_USER, MQTT_PASSWORD)

    def on_connect(client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            logger.info("Connected to MQTT broker")
        else:
            logger.error(f"MQTT connection failed: {reason_code}")

    def on_disconnect(client, userdata, flags, reason_code, properties):
        logger.warning("Disconnected from MQTT broker, reconnecting...")
        while True:
            try:
                client.reconnect()
                break
            except Exception:
                time.sleep(5)

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
    client.loop_start()
    return client


def main():
    logger.info("Starting bird feeder sensor node")

    mqtt_client = create_mqtt_client()
    time.sleep(2)  # wait for connection

    threads = [
        threading.Thread(
            target=run_camera, args=(mqtt_client,), daemon=True, name="camera"
        ),
        threading.Thread(
            target=run_audio, args=(mqtt_client,), daemon=True, name="audio"
        ),
        threading.Thread(
            target=run_weather, args=(mqtt_client,), daemon=True, name="weather"
        ),
        threading.Thread(
            target=run_heartbeat, args=(mqtt_client,), daemon=True, name="heartbeat"
        ),
    ]

    for t in threads:
        t.start()
        logger.info(f"Started {t.name} thread")

    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down")
        mqtt_client.loop_stop()
        mqtt_client.disconnect()


if __name__ == "__main__":
    main()
