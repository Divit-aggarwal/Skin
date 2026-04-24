import os

import cv2
import mediapipe as mp
import numpy as np

_BLUR_THRESHOLD = float(os.getenv("BLUR_SCORE_THRESHOLD", "100.0"))

_face_mesh = mp.solutions.face_mesh.FaceMesh(
    static_image_mode=True,
    max_num_faces=2,
    refine_landmarks=False,
    min_detection_confidence=0.5,
)


def compute_blur_score(image_array: np.ndarray) -> float:
    gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def count_faces(image_array: np.ndarray) -> int:
    results = _face_mesh.process(image_array)
    if not results.multi_face_landmarks:
        return 0
    return len(results.multi_face_landmarks)


def validate_image(image_array: np.ndarray) -> dict:
    blur_score = compute_blur_score(image_array)
    face_count = count_faces(image_array)

    if blur_score < _BLUR_THRESHOLD:
        return {"passed": False, "blur_score": blur_score, "face_count": face_count, "reason": "Image is too blurry"}
    if face_count == 0:
        return {"passed": False, "blur_score": blur_score, "face_count": face_count, "reason": "No face detected"}
    if face_count > 1:
        return {"passed": False, "blur_score": blur_score, "face_count": face_count, "reason": "Multiple faces detected"}

    return {"passed": True, "blur_score": blur_score, "face_count": face_count}
