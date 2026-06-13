import logging
import numpy as np
from PIL import Image
from ai_edge_litert.interpreter import Interpreter
from config import EFFICIENTDET_MODEL, ANIMAL_DETECTION_THRESHOLD, ANIMAL_CLASS_IDS

logger = logging.getLogger(__name__)

_interpreter = None


def get_interpreter() -> Interpreter:
    global _interpreter
    if _interpreter is None:
        logger.info(f"Loading EfficientDet model from {EFFICIENTDET_MODEL}")
        _interpreter = Interpreter(model_path=EFFICIENTDET_MODEL)
        _interpreter.allocate_tensors()
        logger.info("EfficientDet model loaded")
    return _interpreter


def is_animal_present(frame: np.ndarray) -> tuple[bool, float]:
    """Run EfficientDet-Lite0 on an RGB frame to check for an animal class."""
    try:
        interpreter = get_interpreter()
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        image = Image.fromarray(frame).resize((320, 320))
        input_data = np.expand_dims(np.array(image, dtype=np.uint8), axis=0)

        interpreter.set_tensor(input_details[0]["index"], input_data)
        interpreter.invoke()

        classes = interpreter.get_tensor(output_details[1]["index"])[0]
        scores = interpreter.get_tensor(output_details[2]["index"])[0]

        for i, score in enumerate(scores):
            if (
                score >= ANIMAL_DETECTION_THRESHOLD
                and int(classes[i]) in ANIMAL_CLASS_IDS
            ):
                return True, float(score)
        return False, 0.0
    except Exception as e:
        logger.error(f"EfficientDet inference failed: {e}")
        return False, 0.0
