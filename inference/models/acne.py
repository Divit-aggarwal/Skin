"""YOLOv11n acne detection model.

Preprocess → ONNX infer → parse detections → zone-labeled scores.
Implemented in Slice 5.
"""

import numpy as np


def detect_acne(image_array: np.ndarray) -> list[dict]:
    """Return list of {bbox, confidence, zone} dicts. Implemented in Slice 5."""
    raise NotImplementedError("Acne detection implemented in Slice 5")
