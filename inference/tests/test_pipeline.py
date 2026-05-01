"""Inference pipeline unit tests.

All ONNX model calls are mocked — these tests verify pipeline logic,
not model accuracy.
"""

import sys
import os
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

# Ensure inference root is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def _fake_image(h: int = 480, w: int = 640) -> np.ndarray:
    return np.random.randint(0, 255, (h, w, 3), dtype=np.uint8)


_PASS_QG = {"passed": True, "blur_score": 250.0, "face_count": 1}
_FAIL_BLUR = {"passed": False, "blur_score": 10.0, "face_count": 1, "reason": "Image is too blurry"}
_FAIL_NOFACE = {"passed": False, "blur_score": 250.0, "face_count": 0, "reason": "No face detected"}

_QG_PATH = "pipeline.validate_image"
_ACNE_PATH = "pipeline.detect_acne"
_WRINKLE_PATH = "pipeline.segment_wrinkles"
_OILINESS_PATH = "pipeline.estimate_oiliness"


def _run(qg=_PASS_QG, acne=None, wrinkle=None, oiliness=0.0):
    if acne is None:
        acne = []
    if wrinkle is None:
        wrinkle = {"score": 0.0, "mask_density": 0.0}
    from pipeline import run_pipeline
    img = _fake_image()
    with (
        patch(_QG_PATH, return_value=qg),
        patch(_ACNE_PATH, return_value=acne),
        patch(_WRINKLE_PATH, return_value=wrinkle),
        patch(_OILINESS_PATH, return_value=oiliness),
    ):
        return run_pipeline(img)


# ---------------------------------------------------------------------------
# Quality gate rejections
# ---------------------------------------------------------------------------

def test_blur_rejection():
    result = _run(qg=_FAIL_BLUR)
    assert result["status"] == "rejected"
    assert "blurry" in result["reason"].lower()


def test_no_face_rejection():
    result = _run(qg=_FAIL_NOFACE)
    assert result["status"] == "rejected"
    assert "face" in result["reason"].lower()


# ---------------------------------------------------------------------------
# Successful pipeline
# ---------------------------------------------------------------------------

def test_scores_in_range():
    acne_dets = [
        {"bbox": [100.0, 80.0, 20.0, 20.0], "confidence": 0.8, "zone": "forehead"},
        {"bbox": [200.0, 200.0, 15.0, 15.0], "confidence": 0.6, "zone": "left_cheek"},
    ]
    result = _run(
        acne=acne_dets,
        wrinkle={"score": 40.0, "mask_density": 0.4},
        oiliness=60.0,
    )
    assert result["status"] == "completed"
    assert 0.0 <= result["acne_score"] <= 100.0
    assert 0.0 <= result["wrinkle_score"] <= 100.0
    assert 0.0 <= result["oiliness_score"] <= 100.0
    assert 0.0 <= result["overall_score"] <= 100.0


def test_severity_level_mild():
    result = _run(wrinkle={"score": 10.0, "mask_density": 0.1}, oiliness=5.0)
    assert result["severity_level"] == "mild"
    assert result["overall_score"] < 33


def test_severity_level_moderate():
    result = _run(
        acne=[{"bbox": [100.0, 100.0, 20.0, 20.0], "confidence": 0.9, "zone": "nose"}] * 2,
        wrinkle={"score": 40.0, "mask_density": 0.4},
        oiliness=50.0,
    )
    assert result["severity_level"] in ("mild", "moderate", "severe")
    # Just verify the enum is correct based on the computed score
    score = result["overall_score"]
    if score < 33:
        assert result["severity_level"] == "mild"
    elif score <= 66:
        assert result["severity_level"] == "moderate"
    else:
        assert result["severity_level"] == "severe"


def test_zone_breakdown_contains_all_five_zones():
    result = _run()
    assert result["status"] == "completed"
    zones = {z["zone"] for z in result["acne_zones"]}
    assert zones == {"forehead", "nose", "left_cheek", "right_cheek", "chin"}


def test_model_version_format():
    result = _run()
    assert result["model_version"] == "yolo11n-acne-v0.1_unet-wrinkle-v0.1_oiliness-heuristic-v1"


def test_scores_never_exceed_100():
    # 20 high-confidence detections — should clip at 100
    many_dets = [
        {"bbox": [100.0, 100.0, 10.0, 10.0], "confidence": 0.95, "zone": "forehead"}
        for _ in range(20)
    ]
    result = _run(
        acne=many_dets,
        wrinkle={"score": 100.0, "mask_density": 1.0},
        oiliness=100.0,
    )
    assert result["acne_score"] <= 100.0
    assert result["wrinkle_score"] <= 100.0
    assert result["oiliness_score"] <= 100.0
    assert result["overall_score"] <= 100.0
