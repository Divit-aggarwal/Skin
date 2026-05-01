"""YOLOv11n acne detection.

Expected ONNX I/O (Ultralytics export format, single-class model):
  Input:  [1, 3, 640, 640]  float32   (normalised 0–1, RGB, NCHW)
  Output: [1, 84, 8400]      float32   (cx, cy, w, h, 80 class scores) in 640-px space
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

    raw shape: [1, 84, 8400]  — (cx, cy, w, h, 80 class scores) in 640-px letterboxed space.
    Returns list of {bbox: [cx, cy, w, h], confidence: float, zone: str}
    where bbox is in original image pixel space.
    """
    import cv2

    preds = raw[0].T  # [8400, 84]
    # confidence = max class score across columns 4:84
    confs = np.max(preds[:, 4:], axis=1)
    mask = confs >= conf_threshold
    preds = preds[mask]
    confs = confs[mask]
    if len(preds) == 0:
        return []

    # Letterbox uses one uniform scale; scale_x == scale_y
    scale = scale_x
    cx = (preds[:, 0] - pad_x) / scale
    cy = (preds[:, 1] - pad_y) / scale
    bw = preds[:, 2] / scale
    bh = preds[:, 3] / scale

    cx = np.clip(cx, 0, orig_w)
    cy = np.clip(cy, 0, orig_h)

    # NMS: OpenCV expects (x1, y1, w, h)
    x1 = (cx - bw / 2).tolist()
    y1 = (cy - bh / 2).tolist()
    boxes = [[x1[i], y1[i], float(bw[i]), float(bh[i])] for i in range(len(preds))]
    indices = cv2.dnn.NMSBoxes(boxes, confs.tolist(), conf_threshold, 0.45)
    if len(indices) == 0:
        return []
    indices = np.array(indices).flatten()

    detections = []
    for i in indices:
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
