from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from loguru import logger

from schemas import InferRequest, InferResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Slice 5: load ONNX models here via models.loader.load_models(...)
    logger.info("Inference service starting up (ML models not loaded — Slice 5)")
    yield
    logger.info("Inference service shutting down")


app = FastAPI(title="Skin Inference Service", version="0.1.0", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/infer", response_model=InferResponse)
async def infer(body: InferRequest):
    # Slice 5: call quality_gate → pipeline.run_pipeline → return scores
    raise HTTPException(status_code=501, detail="ML inference implemented in Slice 5")
