"""U-Net wrinkle segmentation model.

Preprocess → ONNX infer → parse mask → regional severity score.
Implemented in Slice 5.
"""

import numpy as np


def segment_wrinkles(image_array: np.ndarray) -> dict:
    """Return {score: float, mask_summary: dict}. Implemented in Slice 5."""
    raise NotImplementedError("Wrinkle segmentation implemented in Slice 5")
