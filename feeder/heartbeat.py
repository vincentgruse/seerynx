import time
import json
import logging
import paho.mqtt.client as mqtt
from config import TOPIC_HEARTBEAT, HEARTBEAT_INTERVAL

logger = logging.getLogger(__name__)


def run_heartbeat(mqtt_client: mqtt.Client):
    logger.info("Heartbeat service started")

    while True:
        mqtt_client.publish(TOPIC_HEARTBEAT, json.dumps({"status": "online"}), qos=0)
        time.sleep(HEARTBEAT_INTERVAL)
