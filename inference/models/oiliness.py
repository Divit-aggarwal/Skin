"""Oiliness heuristic using OpenCV HSV T-zone saturation.

T-zone = forehead + nose strip: top 60% of image height, centre 40% of width.
High saturation + high value in HSV correlates with oily/shiny skin.
"""

import cv2
import numpy as np


def estimate_oiliness(image_array: np.ndarray) -> float:
    """Return oiliness score 0.0–100.0.

    Extracts the T-zone ROI (forehead + nose), converts to HSV, and uses
    a weighted combination of saturation and brightness to detect shine.
    """
    h, w = image_array.shape[:2]

    # T-zone: top 60 % height, centre 40 % width
    y_end = int(h * 0.60)
    x_start = int(w * 0.30)
    x_end = int(w * 0.70)

    roi = image_array[:y_end, x_start:x_end]
    if roi.size == 0:
        return 0.0

    # OpenCV expects BGR; image_array is RGB
    bgr = cv2.cvtColor(roi, cv2.COLOR_RGB2BGR)
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV).astype(np.float32)

    saturation = hsv[:, :, 1]  # 0–255
    value = hsv[:, :, 2]       # 0–255 (brightness)

    # Oily skin = high saturation AND high brightness (specular highlights)
    # Weighted average; normalise each channel to 0–1 first
    oiliness = 0.6 * saturation.mean() / 255.0 + 0.4 * value.mean() / 255.0
    return float(np.clip(oiliness * 100.0, 0.0, 100.0))
