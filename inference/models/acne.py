"""YOLOv11n acne detection.

Expected ONNX I/O (Ultralytics export format, single-class model):
  Input:  [1, 3, 640, 640]  float32   (normalised 0–1, RGB, NCHW)
  Output: [1, 5, 8400]       float32   (cx, cy, w, h, conf) in 640-px space
"""

import numpy as np

from models.loader import get_acne_session
from zone_mapper import map_bbox_to_zone

_INPUT_SIZE = 640


def _preprocess(image_rgb: np.ndarray) -> tuple[np.ndarray, float, float, int, int]:
    """Resize + normalise image to [1, 3, 640, 640].

    Returns (tensor, scale_x, scale_y, pad_x, pad_y).
    Uses letterbox padding to preserve aspect ratio.
    """
    h, w = image_rgb.shape[:2]
    scale = min(_INPUT_SIZE / w, _INPUT_SIZE / h)
    new_w, new_h = int(w * scale), int(h * scale)
    pad_x = (_INPUT_SIZE - new_w) // 2
    pad_y = (_INPUT_SIZE - new_h) // 2

    import cv2
    resized = cv2.resize(image_rgb, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
    canvas = np.full((_INPUT_SIZE, _INPUT_SIZE, 3), 114, dtype=np.uint8)
    canvas[pad_y:pad_y + new_h, pad_x:pad_x + new_w] = resized

    tensor = canvas.astype(np.float32) / 255.0
    tensor = np.transpose(tensor, (2, 0, 1))[np.newaxis]  # NHWC → NCHW
    return tensor, scale, scale, pad_x, pad_y


def _postprocess(
    raw: np.ndarray,
    conf_threshold: float,
    scale_x: float,
    scale_y: float,
    pad_x: int,
    pad_y: int,
    orig_w: int,
    orig_h: int,
) -> list[dict]:
    """Parse YOLO output to detection list.

    raw shape: [1, 5, 8400]  — (cx, cy, w, h, conf) in 640-px letterboxed space.
    Returns list of {bbox: [cx, cy, w, h], confidence: float, zone: str}
    where bbox is in original image pixel space.
    """
    preds = raw[0]  # [5, 8400]
    if preds.shape[0] == 5:
        preds = preds.T  # [8400, 5]
    # preds: [8400, 5]  columns: cx, cy, w, h, conf
    mask = preds[:, 4] >= conf_threshold
    preds = preds[mask]
    if len(preds) == 0:
        return []

    # Convert from letterboxed 640-space back to original image space
    cx = (preds[:, 0] - pad_x) / scale_x
    cy = (preds[:, 1] - pad_y) / scale_y
    bw = preds[:, 2] / scale_x
    bh = preds[:, 3] / scale_y
    confs = preds[:, 4]

    # Clip to image bounds
    cx = np.clip(cx, 0, orig_w)
    cy = np.clip(cy, 0, orig_h)

    detections = []
    for i in range(len(preds)):
        bbox = [float(cx[i]), float(cy[i]), float(bw[i]), float(bh[i])]
        zone = map_bbox_to_zone(bbox, orig_w, orig_h)
        detections.append({"bbox": bbox, "confidence": float(confs[i]), "zone": zone})
    return detections


def detect_acne(image_array: np.ndarray, conf_threshold: float = 0.4) -> list[dict]:
    """Return list of {bbox, confidence, zone} dicts for detected acne lesions."""
    orig_h, orig_w = image_array.shape[:2]
    tensor, sx, sy, px, py = _preprocess(image_array)
    session = get_acne_session()
    input_name = session.get_inputs()[0].name
    raw = session.run(None, {input_name: tensor})[0]
    return _postprocess(raw, conf_threshold, sx, sy, px, py, orig_w, orig_h)
