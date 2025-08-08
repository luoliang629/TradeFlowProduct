"""CORS中间件配置."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def add_cors_middleware(app: FastAPI) -> None:
    """添加CORS中间件."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Total-Count"],
    )
    
    logger.info(
        "CORS middleware configured",
        origins=settings.CORS_ORIGINS,
        allow_credentials=True
    )