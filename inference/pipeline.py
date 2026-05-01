"""Orchestrates quality_gate → acne → wrinkle → oiliness → score aggregation."""

import numpy as np

from config import settings
from models.acne import detect_acne
from models.oiliness import estimate_oiliness
from models.wrinkle import segment_wrinkles
from quality_gate import validate_image

_MODEL_VERSION = "yolo11n-acne-v0.1_unet-wrinkle-v0.1_oiliness-heuristic-v1"
_ALL_ZONES = ("forehead", "nose", "left_cheek", "right_cheek", "chin")


def _compute_acne_score(detections: list[dict]) -> float:
    if not detections:
        return 0.0
    # Each high-confidence detection (conf≈1.0) contributes ~15 pts; 7 detections ≈ 100
    raw = sum(d["confidence"] for d in detections) * 15.0
    return float(np.clip(raw, 0.0, 100.0))


def _compute_zone_breakdown(detections: list[dict]) -> list[dict]:
    zone_confs: dict[str, list[float]] = {z: [] for z in _ALL_ZONES}
    for d in detections:
        zone_confs[d["zone"]].append(d["confidence"])
    return [
        {"zone": z, "score": float(np.clip(sum(confs) * 15.0, 0.0, 100.0))}
        for z, confs in zone_confs.items()
    ]


def run_pipeline(image_array: np.ndarray) -> dict:
    """Run the full analysis pipeline on an RGB image array.

    Returns a dict matching InferResponse fields, plus a 'status' key.
    Raises ValueError with a rejection reason if quality gate fails.
    """
    qg = validate_image(image_array)
    if not qg["passed"]:
        return {
            "status": "rejected",
            "reason": qg["reason"],
            "blur_score": qg["blur_score"],
            "face_count": qg["face_count"],
        }

    detections = detect_acne(image_array, conf_threshold=settings.yolo_conf_threshold)
    wrinkle_result = segment_wrinkles(image_array)
    oiliness_score = estimate_oiliness(image_array)

    acne_score = _compute_acne_score(detections)
    wrinkle_score = wrinkle_result["score"]

    overall_score = float(
        np.clip(acne_score * 0.4 + wrinkle_score * 0.3 + oiliness_score * 0.3, 0.0, 100.0)
    )

    if overall_score < 33:
        severity_level = "mild"
    elif overall_score <= 66:
        severity_level = "moderate"
    else:
        severity_level = "severe"

    return {
        "status": "completed",
        "acne_score": acne_score,
        "wrinkle_score": wrinkle_score,
        "oiliness_score": oiliness_score,
        "overall_score": overall_score,
        "severity_level": severity_level,
        "acne_zones": _compute_zone_breakdown(detections),
        "blur_score": qg["blur_score"],
        "face_count": qg["face_count"],
        "model_version": _MODEL_VERSION,
        "yolo_detections": detections,
    }
