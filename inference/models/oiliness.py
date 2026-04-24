"""Oiliness heuristic using OpenCV HSV T-zone saturation.

No ONNX model — pure OpenCV heuristic. Implemented in Slice 5.
"""

import numpy as np


def estimate_oiliness(image_array: np.ndarray) -> float:
    """Return oiliness score 0.0–100.0. Implemented in Slice 5."""
    raise NotImplementedError("Oiliness heuristic implemented in Slice 5")
