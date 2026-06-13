import os

# MQTT
MQTT_HOST = os.environ.get("MQTT_HOST", "")
MQTT_PORT = int(os.environ.get("MQTT_PORT", "1883"))
MQTT_USER = os.environ.get("MQTT_USER", "seerynx")
MQTT_PASSWORD = os.environ.get("MQTT_PASSWORD", "")

if not MQTT_HOST:
    raise RuntimeError("MQTT_HOST environment variable not set")
if not MQTT_PASSWORD:
    raise RuntimeError("MQTT_PASSWORD environment variable not set")

# MQTT Topics
TOPIC_CAMERA = "feeder/camera/frame"
TOPIC_AUDIO = "feeder/audio/chunk"
TOPIC_WEATHER = "feeder/weather"
TOPIC_HEARTBEAT = "feeder/status/heartbeat"

# API
API_BASE_URL = os.environ.get("API_BASE_URL", "")
API_KEY = os.environ.get("SEERYNX_API_KEY", "")

if not API_BASE_URL:
    raise RuntimeError("API_BASE_URL environment variable not set")
if not API_KEY:
    raise RuntimeError("SEERYNX_API_KEY environment variable not set")

# Models
MODELS_DIR = os.environ.get("MODELS_DIR", "/app/models")
BIRDS_V1_MODEL = f"{MODELS_DIR}/birds_v1.tflite"
EFFICIENTDET_MODEL = f"{MODELS_DIR}/efficientdet_lite0.tflite"
BIRDS_LABELS_PATH = f"{MODELS_DIR}/aiy_birds_V1_labelmap.csv"

# Photos
PHOTOS_DIR = os.environ.get("PHOTOS_DIR", "/app/photos")

# Inference thresholds
DETECTION_THRESHOLD = float(os.environ.get("DETECTION_THRESHOLD", "0.5"))
CLASSIFICATION_THRESHOLD = float(os.environ.get("CLASSIFICATION_THRESHOLD", "0.3"))
BIRDNET_THRESHOLD = float(os.environ.get("BIRDNET_THRESHOLD", "0.7"))

# Health server
HEALTH_PORT = int(os.environ.get("HEALTH_PORT", "8001"))
