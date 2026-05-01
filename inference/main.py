import base64
from contextlib import asynccontextmanager

import cv2
import numpy as np
from fastapi import FastAPI, HTTPException
from loguru import logger

from config import settings
from models.loader import load_models
from pipeline import run_pipeline
from schemas import InferRequest, InferResponse, ZoneScore


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Loading ONNX models: acne={} wrinkle={}", settings.acne_model_path, settings.wrinkle_model_path)
    load_models(settings.acne_model_path, settings.wrinkle_model_path)
    logger.info("Models loaded")
    yield
    logger.info("Inference service shutting down")


app = FastAPI(title="Skin Inference Service", version="0.1.0", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/infer", response_model=InferResponse)
async def infer(body: InferRequest):
    image_data = body.image_data
    if "," in image_data:
        image_data = image_data.split(",", 1)[1]

    try:
        raw = base64.b64decode(image_data)
    except Exception:
        raise HTTPException(status_code=422, detail="Invalid base64 image data")

    arr = np.frombuffer(raw, dtype=np.uint8)
    bgr = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if bgr is None:
        raise HTTPException(status_code=422, detail="Could not decode image")

    image_array = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)

    result = run_pipeline(image_array)

    if result["status"] == "rejected":
        raise HTTPException(status_code=422, detail=result["reason"])

    return InferResponse(
        acne_score=result["acne_score"],
        wrinkle_score=result["wrinkle_score"],
        oiliness_score=result["oiliness_score"],
        overall_score=result["overall_score"],
        severity_level=result["severity_level"],
        acne_zones=[ZoneScore(**z) for z in result["acne_zones"]],
        blur_score=result["blur_score"],
        face_count=result["face_count"],
        model_version=result["model_version"],
        yolo_detections=result.get("yolo_detections", []),
    )
