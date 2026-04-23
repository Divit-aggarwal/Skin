from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from loguru import logger

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
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error on {} {}", request.method, request.url)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


api_v1 = FastAPI(title="Skin API v1")
api_v1.include_router(health.router, tags=["health"])

app.mount("/api/v1", api_v1)
