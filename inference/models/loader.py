"""Loads and caches ONNX model sessions on inference service startup.

Implemented in Slice 5. Expected weight files:
  weights/yolo11n_acne.onnx
  weights/unet_wrinkle.onnx
"""

import onnxruntime as ort

_acne_session: ort.InferenceSession | None = None
_wrinkle_session: ort.InferenceSession | None = None


def load_models(acne_path: str, wrinkle_path: str) -> None:
    """Load ONNX sessions into module-level singletons. Called once at startup."""
    raise NotImplementedError("Model loading implemented in Slice 5")


def get_acne_session() -> ort.InferenceSession:
    if _acne_session is None:
        raise RuntimeError("Models not loaded — call load_models() at startup")
    return _acne_session


def get_wrinkle_session() -> ort.InferenceSession:
    if _wrinkle_session is None:
        raise RuntimeError("Models not loaded — call load_models() at startup")
    return _wrinkle_session
