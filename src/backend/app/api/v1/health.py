"""健康检查API端点."""

import asyncio
import time
from typing import Any, Dict

import redis.asyncio as redis
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.database import get_db
from app.core.logging import get_logger
from app.schemas.common import HealthCheckResponse
from app.utils.minio_client import get_minio_client
from app.utils.redis_client import get_redis_client

# 应用启动时间
start_time = time.time()

logger = get_logger(__name__)
router = APIRouter(prefix="/health", tags=["健康检查"])


@router.get(
    "",
    response_model=HealthCheckResponse,
    summary="基础健康检查",
    description="检查应用基础状态"
)
async def health_check() -> HealthCheckResponse:
    """基础健康检查端点."""
    uptime = time.time() - start_time
    
    return HealthCheckResponse(
        status="healthy",
        version="1.0.0",
        uptime=uptime,
        message="Service is running",
    )


@router.get(
    "/detailed",
    response_model=HealthCheckResponse,
    summary="详细健康检查",
    description="检查应用及其依赖服务状态"
)
async def detailed_health_check(
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client),
) -> HealthCheckResponse:
    """详细健康检查端点，包括所有依赖服务."""
    uptime = time.time() - start_time
    dependencies: Dict[str, Dict[str, Any]] = {}
    overall_status = "healthy"
    
    # 检查PostgreSQL连接
    try:
        await db.execute("SELECT 1")
        dependencies["postgresql"] = {
            "status": "healthy",
            "response_time_ms": 0,
            "details": "Connection successful"
        }
        logger.info("PostgreSQL health check passed")
    except Exception as e:
        dependencies["postgresql"] = {
            "status": "unhealthy",
            "error": str(e),
            "details": "Connection failed"
        }
        overall_status = "degraded"
        logger.error("PostgreSQL health check failed", error=str(e))
    
    # 检查Redis连接
    try:
        start_redis = time.time()
        await redis_client.ping()
        response_time = (time.time() - start_redis) * 1000
        
        dependencies["redis"] = {
            "status": "healthy",
            "response_time_ms": round(response_time, 2),
            "details": "Connection successful"
        }
        logger.info("Redis health check passed", response_time_ms=response_time)
    except Exception as e:
        dependencies["redis"] = {
            "status": "unhealthy",
            "error": str(e),
            "details": "Connection failed"
        }
        overall_status = "degraded"
        logger.error("Redis health check failed", error=str(e))
    
    # 检查MongoDB连接
    try:
        start_mongo = time.time()
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        await client.admin.command('ping')
        response_time = (time.time() - start_mongo) * 1000
        
        dependencies["mongodb"] = {
            "status": "healthy",
            "response_time_ms": round(response_time, 2),
            "details": "Connection successful"
        }
        await client.close()
        logger.info("MongoDB health check passed", response_time_ms=response_time)
    except Exception as e:
        dependencies["mongodb"] = {
            "status": "unhealthy",
            "error": str(e),
            "details": "Connection failed"
        }
        overall_status = "degraded"
        logger.error("MongoDB health check failed", error=str(e))
    
    # 检查MinIO连接
    try:
        start_minio = time.time()
        minio_client = get_minio_client()
        # 检查存储桶是否存在
        bucket_exists = minio_client.bucket_exists(settings.MINIO_BUCKET_NAME)
        response_time = (time.time() - start_minio) * 1000
        
        dependencies["minio"] = {
            "status": "healthy",
            "response_time_ms": round(response_time, 2),
            "details": f"Bucket '{settings.MINIO_BUCKET_NAME}' exists: {bucket_exists}"
        }
        logger.info("MinIO health check passed", response_time_ms=response_time)
    except Exception as e:
        dependencies["minio"] = {
            "status": "unhealthy",
            "error": str(e),
            "details": "Connection failed"
        }
        overall_status = "degraded"
        logger.error("MinIO health check failed", error=str(e))
    
    # 如果所有依赖都失败，则标记为不健康
    unhealthy_count = sum(
        1 for dep in dependencies.values() 
        if dep["status"] == "unhealthy"
    )
    
    if unhealthy_count == len(dependencies):
        overall_status = "unhealthy"
    
    response = HealthCheckResponse(
        status=overall_status,
        version="1.0.0",
        uptime=uptime,
        dependencies=dependencies,
        message=f"Service status: {overall_status}"
    )
    
    # 如果服务不健康，返回503状态码
    if overall_status == "unhealthy":
        raise HTTPException(status_code=503, detail=response.dict())
    
    return response


@router.get(
    "/liveness",
    summary="存活性检查",
    description="Kubernetes存活性探针使用"
)
async def liveness_check() -> Dict[str, str]:
    """存活性检查，用于Kubernetes liveness probe."""
    return {"status": "alive"}


@router.get(
    "/readiness",
    summary="就绪性检查", 
    description="Kubernetes就绪性探针使用"
)
async def readiness_check(
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client),
) -> Dict[str, str]:
    """就绪性检查，用于Kubernetes readiness probe."""
    try:
        # 检查关键依赖
        await asyncio.gather(
            db.execute("SELECT 1"),
            redis_client.ping(),
            return_exceptions=True
        )
        return {"status": "ready"}
    except Exception as e:
        logger.error("Readiness check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service not ready")