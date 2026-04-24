import os


class Settings:
    blur_score_threshold: float = float(os.getenv("BLUR_SCORE_THRESHOLD", "100.0"))
    yolo_conf_threshold: float = float(os.getenv("YOLO_CONF_THRESHOLD", "0.4"))
    acne_model_path: str = os.getenv("ACNE_MODEL_PATH", "weights/yolo11n_acne.onnx")
    wrinkle_model_path: str = os.getenv("WRINKLE_MODEL_PATH", "weights/unet_wrinkle.onnx")
    port: int = int(os.getenv("PORT", "8001"))


settings = Settings()
