from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from loguru import logger

from app.api.v1.router import v1_router
from app.config import settings
from app.exceptions import AppError
from app.middleware import add_middleware
from app.routers import health


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up")
    yield
    logger.info("Shutting down")


app = FastAPI(
    title="Skin API",
    version="0.1.0",
    debug=settings.debug,
    lifespan=lifespan,
)

add_middleware(app)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.detail, "detail": None}},
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error on {} {}", request.method, request.url)
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "INTERNAL_ERROR", "message": "Internal server error", "detail": None}},
    )


app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(v1_router, prefix="/api/v1")
