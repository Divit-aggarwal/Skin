from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import onnxruntime as ort

_acne_session = None
_wrinkle_session = None


def load_models(acne_path: str, wrinkle_path: str) -> None:
    """Load ONNX sessions into module-level singletons. Called once at startup."""
    import onnxruntime as ort  # noqa: PLC0415 — intentional lazy import

    global _acne_session, _wrinkle_session
    _acne_session = ort.InferenceSession(acne_path, providers=["CPUExecutionProvider"])
    _wrinkle_session = ort.InferenceSession(wrinkle_path, providers=["CPUExecutionProvider"])


def get_acne_session() -> ort.InferenceSession:
    if _acne_session is None:
        raise RuntimeError("Models not loaded — call load_models() at startup")
    return _acne_session


def get_wrinkle_session() -> ort.InferenceSession:
    if _wrinkle_session is None:
        raise RuntimeError("Models not loaded — call load_models() at startup")
    return _wrinkle_session
