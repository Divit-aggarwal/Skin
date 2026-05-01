"""U-Net wrinkle segmentation.

Expected ONNX I/O:
  Input:  [batch_size, 3, 384, 384]  float32   (normalised 0–1, RGB, NCHW)
  Output: [batch_size, 1, 384, 384]  float32   (logits or sigmoid probabilities)
"""

import cv2
import numpy as np

from models.loader import get_wrinkle_session

_INPUT_SIZE = 384
_MASK_THRESHOLD = 0.5


def _preprocess(image_rgb: np.ndarray) -> np.ndarray:
    resized = cv2.resize(image_rgb, (_INPUT_SIZE, _INPUT_SIZE), interpolation=cv2.INTER_LINEAR)
    tensor = resized.astype(np.float32) / 255.0
    return np.transpose(tensor, (2, 0, 1))[np.newaxis]  # [1, 3, 384, 384]


def segment_wrinkles(image_array: np.ndarray) -> dict:
    """Return {score: float, mask_density: float}.

    score is 0–100 based on fraction of pixels classified as wrinkled.
    """
    tensor = _preprocess(image_array)
    session = get_wrinkle_session()
    input_name = session.get_inputs()[0].name
    raw = session.run(None, {input_name: tensor})[0]  # [1, 1, 384, 384]

    probs = 1.0 / (1.0 + np.exp(-raw[0, 0]))  # sigmoid
    mask = (probs >= _MASK_THRESHOLD).astype(np.float32)
    mask_density = float(mask.mean())
    score = float(np.clip(mask_density * 100.0, 0.0, 100.0))
    return {"score": score, "mask_density": mask_density}
