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

# Camera
CAMERA_WIDTH = int(os.environ.get("CAMERA_WIDTH", "1920"))
CAMERA_HEIGHT = int(os.environ.get("CAMERA_HEIGHT", "1080"))
CAMERA_RESOLUTION = (CAMERA_WIDTH, CAMERA_HEIGHT)
CAMERA_FRAMERATE = int(os.environ.get("CAMERA_FRAMERATE", "10"))
MOTION_THRESHOLD = int(os.environ.get("MOTION_THRESHOLD", "25"))
MOTION_MIN_AREA = int(os.environ.get("MOTION_MIN_AREA", "1500"))
MOTION_SUSTAIN_FRAMES = int(os.environ.get("MOTION_SUSTAIN_FRAMES", "3"))
BURST_COUNT = int(os.environ.get("BURST_COUNT", "3"))
MOTION_COOLDOWN = int(os.environ.get("MOTION_COOLDOWN", "10"))

# Animal pre-check (EfficientDet-Lite0)
MODELS_DIR = os.environ.get("MODELS_DIR", "./models")
EFFICIENTDET_MODEL = f"{MODELS_DIR}/efficientdet_lite0.tflite"
ANIMAL_DETECTION_THRESHOLD = float(os.environ.get("ANIMAL_DETECTION_THRESHOLD", "0.5"))
# COCO class IDs: bird, cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe
ANIMAL_CLASS_IDS = {16, 17, 18, 19, 20, 21, 22, 23, 24, 25}

# Audio
AUDIO_DEVICE = os.environ.get("AUDIO_DEVICE", "hw:2,0")
AUDIO_SAMPLE_RATE = 48000
AUDIO_CHANNELS = 1
AUDIO_CHUNK_SECONDS = 3

# Weather
WEATHER_PIN = int(os.environ.get("WEATHER_PIN", "17"))
WEATHER_INTERVAL = int(os.environ.get("WEATHER_INTERVAL", "300"))

# Heartbeat
HEARTBEAT_INTERVAL = int(os.environ.get("HEARTBEAT_INTERVAL", "15"))
