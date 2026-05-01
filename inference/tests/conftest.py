"""Stub out heavy inference deps so tests can run without Docker environment."""

import sys
import types
from unittest.mock import MagicMock

# Stub mediapipe before any quality_gate import fires
if "mediapipe" not in sys.modules:
    mp_stub = types.ModuleType("mediapipe")
    solutions = types.ModuleType("mediapipe.solutions")
    face_mesh_mod = types.ModuleType("mediapipe.solutions.face_mesh")

    face_mesh_instance = MagicMock()
    face_mesh_instance.process.return_value = MagicMock(multi_face_landmarks=None)
    face_mesh_cls = MagicMock(return_value=face_mesh_instance)
    face_mesh_mod.FaceMesh = face_mesh_cls

    solutions.face_mesh = face_mesh_mod
    mp_stub.solutions = solutions

    sys.modules["mediapipe"] = mp_stub
    sys.modules["mediapipe.solutions"] = solutions
    sys.modules["mediapipe.solutions.face_mesh"] = face_mesh_mod

# Stub onnxruntime
if "onnxruntime" not in sys.modules:
    ort_stub = types.ModuleType("onnxruntime")
    ort_stub.InferenceSession = MagicMock
    sys.modules["onnxruntime"] = ort_stub
