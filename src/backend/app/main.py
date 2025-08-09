"""FastAPI应用程序入口点."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.api.v1.health import router as health_router
from app.api.v1.auth import router as auth_router
from app.config import settings
from app.core.database import close_databases, init_databases
from app.core.logging import configure_logging, get_logger
from app.middleware.cors import add_cors_middleware
from app.middleware.error_handler import ErrorHandlerMiddleware
from app.middleware.logging import LoggingMiddleware
from app.middleware.performance import PerformanceMiddleware, RateLimitMiddleware
from app.utils.minio_client import init_minio
from app.utils.redis_client import close_redis, init_redis

# 配置日志
configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """应用程序生命周期管理."""
    # 启动时的初始化
    logger.info("Starting TradeFlow Backend API")
    
    try:
        # 初始化数据库连接
        await init_databases()
        logger.info("Database connections initialized")
        
        # 初始化Redis连接
        await init_redis()
        logger.info("Redis connection initialized")
        
        # 初始化MinIO
        await init_minio()
        logger.info("MinIO initialized")
        
        logger.info("Application startup completed successfully")
        
    except Exception as e:
        logger.error("Application startup failed", error=str(e))
        raise
    
    yield
    
    # 关闭时的清理
    logger.info("Shutting down TradeFlow Backend API")
    
    try:
        # 关闭数据库连接
        await close_databases()
        logger.info("Database connections closed")
        
        # 关闭Redis连接
        await close_redis()
        logger.info("Redis connection closed")
        
        logger.info("Application shutdown completed successfully")
        
    except Exception as e:
        logger.error("Application shutdown failed", error=str(e))
        raise


def create_app() -> FastAPI:
    """创建FastAPI应用程序实例."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.DESCRIPTION,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json" if settings.DEBUG else None,
        docs_url=f"{settings.API_V1_PREFIX}/docs" if settings.DEBUG else None,
        redoc_url=f"{settings.API_V1_PREFIX}/redoc" if settings.DEBUG else None,
        lifespan=lifespan,
    )
    
    # 添加中间件（注意顺序很重要）
    # 1. CORS中间件（最外层）
    add_cors_middleware(app)
    
    # 2. 性能监控中间件
    app.add_middleware(PerformanceMiddleware, slow_request_threshold=2.0)
    
    # 3. 速率限制中间件（开发环境跳过）
    if not settings.is_development:
        app.add_middleware(RateLimitMiddleware, requests_per_minute=120)
    
    # 4. 请求日志中间件
    app.add_middleware(LoggingMiddleware)
    
    # 5. 错误处理中间件（最内层）
    app.add_middleware(ErrorHandlerMiddleware)
    
    # 注册路由
    app.include_router(health_router, prefix=settings.API_V1_PREFIX)
    app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
    
    # 根路径处理
    @app.get("/", include_in_schema=False)
    async def root():
        """根路径重定向."""
        return JSONResponse({
            "message": "TradeFlow Backend API",
            "version": settings.VERSION,
            "docs_url": f"{settings.API_V1_PREFIX}/docs" if settings.DEBUG else None,
        })
    
    return app


# 创建应用实例
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting development server")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=False,  # 我们使用自定义的请求日志中间件
    )