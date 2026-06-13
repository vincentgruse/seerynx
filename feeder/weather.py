import time
import json
import logging
import board
import adafruit_dht
import paho.mqtt.client as mqtt
from config import TOPIC_WEATHER, WEATHER_INTERVAL

logger = logging.getLogger(__name__)


def run_weather(mqtt_client: mqtt.Client):
    logger.info("Weather service started — DHT22 on GPIO17")
    dht = adafruit_dht.DHT22(board.D17)

    while True:
        try:
            payload = {
                "temperature_c": dht.temperature,
                "humidity": dht.humidity,
            }
            mqtt_client.publish(TOPIC_WEATHER, json.dumps(payload), qos=0)
            logger.info(f"Weather: {payload}")
        except RuntimeError as e:
            logger.warning(f"DHT22 read error: {e}")
        time.sleep(WEATHER_INTERVAL)
