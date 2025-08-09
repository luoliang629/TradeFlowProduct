"""监控和指标API路由."""

import asyncio
import os
import psutil
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import PlainTextResponse
from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    Summary,
    generate_latest,
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    multiprocess,
    REGISTRY
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db, engine
from app.core.logging import get_logger
from app.utils.redis_client import redis_client
from app.services.mongodb import mongodb_service

logger = get_logger(__name__)

router = APIRouter(prefix="/monitoring", tags=["监控"])

# Prometheus指标定义
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

active_connections = Gauge(
    'active_connections',
    'Number of active connections',
    ['connection_type']
)

db_connections_active = Gauge(
    'db_connections_active',
    'Active database connections',
    ['database']
)

redis_operations_total = Counter(
    'redis_operations_total',
    'Total Redis operations',
    ['operation', 'status']
)

business_metrics = Counter(
    'business_metrics_total',
    'Business metrics counter',
    ['metric_type', 'status']
)

system_memory_usage = Gauge(
    'system_memory_usage_bytes',
    'System memory usage in bytes',
    ['type']
)

system_cpu_usage = Gauge(
    'system_cpu_usage_percent',
    'System CPU usage percentage'
)

system_disk_usage = Gauge(
    'system_disk_usage_bytes',
    'System disk usage in bytes',
    ['mount_point', 'type']
)


class HealthChecker:
    """健康检查器."""
    
    @staticmethod
    async def check_database() -> Dict:
        """检查数据库健康状态."""
        try:
            async with engine.begin() as conn:
                result = await conn.execute("SELECT 1")
                result.scalar()
            
            # 获取连接池状态
            pool_status = {
                "size": engine.pool.size(),
                "checked_in": engine.pool.checkedin(),
                "overflow": engine.pool.overflow(),
                "total": engine.pool.checkedout()
            }
            
            return {
                "status": "healthy",
                "response_time_ms": 0,
                "pool_status": pool_status
            }
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    @staticmethod
    async def check_redis() -> Dict:
        """检查Redis健康状态."""
        try:
            start_time = asyncio.get_event_loop().time()
            await redis_client.ping()
            response_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            # 获取Redis信息
            info = await redis_client.info()
            
            return {
                "status": "healthy",
                "response_time_ms": response_time,
                "version": info.get("redis_version"),
                "connected_clients": info.get("connected_clients"),
                "used_memory": info.get("used_memory_human")
            }
            
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    @staticmethod
    async def check_mongodb() -> Dict:
        """检查MongoDB健康状态."""
        try:
            # 执行ping命令
            result = await mongodb_service.db.command("ping")
            
            # 获取服务器状态
            server_status = await mongodb_service.db.command("serverStatus")
            
            return {
                "status": "healthy",
                "version": server_status.get("version"),
                "uptime": server_status.get("uptime"),
                "connections": server_status.get("connections", {})
            }
            
        except Exception as e:
            logger.error(f"MongoDB health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    @staticmethod
    async def check_system() -> Dict:
        """检查系统资源."""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 内存使用
            memory = psutil.virtual_memory()
            
            # 磁盘使用
            disk = psutil.disk_usage('/')
            
            # 网络连接
            connections = len(psutil.net_connections())
            
            # 更新Prometheus指标
            system_cpu_usage.set(cpu_percent)
            system_memory_usage.labels(type='used').set(memory.used)
            system_memory_usage.labels(type='available').set(memory.available)
            system_memory_usage.labels(type='total').set(memory.total)
            system_disk_usage.labels(mount_point='/', type='used').set(disk.used)
            system_disk_usage.labels(mount_point='/', type='free').set(disk.free)
            system_disk_usage.labels(mount_point='/', type='total').set(disk.total)
            
            return {
                "status": "healthy",
                "cpu": {
                    "percent": cpu_percent,
                    "count": psutil.cpu_count()
                },
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": disk.percent
                },
                "network": {
                    "connections": connections
                }
            }
            
        except Exception as e:
            logger.error(f"System health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }


health_checker = HealthChecker()


@router.get("/health")
async def health_check():
    """基本健康检查端点."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/health/detailed")
async def detailed_health_check():
    """详细健康检查端点."""
    try:
        # 并行执行所有健康检查
        results = await asyncio.gather(
            health_checker.check_database(),
            health_checker.check_redis(),
            health_checker.check_mongodb(),
            health_checker.check_system(),
            return_exceptions=True
        )
        
        # 处理结果
        checks = {
            "database": results[0] if not isinstance(results[0], Exception) else {"status": "error", "error": str(results[0])},
            "redis": results[1] if not isinstance(results[1], Exception) else {"status": "error", "error": str(results[1])},
            "mongodb": results[2] if not isinstance(results[2], Exception) else {"status": "error", "error": str(results[2])},
            "system": results[3] if not isinstance(results[3], Exception) else {"status": "error", "error": str(results[3])}
        }
        
        # 确定总体状态
        overall_status = "healthy"
        for check in checks.values():
            if check.get("status") != "healthy":
                overall_status = "unhealthy"
                break
        
        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": checks
        }
        
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Health check failed"
        )


@router.get("/health/live")
async def liveness_probe():
    """Kubernetes存活探针端点."""
    return {"status": "alive"}


@router.get("/health/ready")
async def readiness_probe():
    """Kubernetes就绪探针端点."""
    try:
        # 检查关键服务
        db_check = await health_checker.check_database()
        redis_check = await health_checker.check_redis()
        
        if db_check["status"] == "healthy" and redis_check["status"] == "healthy":
            return {"status": "ready"}
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service not ready"
            )
            
    except Exception as e:
        logger.error(f"Readiness probe failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not ready"
        )


@router.get("/metrics", response_class=PlainTextResponse)
async def get_metrics():
    """Prometheus指标端点."""
    try:
        # 更新数据库连接指标
        if hasattr(engine.pool, 'size'):
            db_connections_active.labels(database='postgresql').set(
                engine.pool.checkedout()
            )
        
        # 生成指标输出
        metrics = generate_latest(REGISTRY)
        
        return PlainTextResponse(
            content=metrics,
            media_type=CONTENT_TYPE_LATEST
        )
        
    except Exception as e:
        logger.error(f"Failed to generate metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate metrics"
        )


@router.get("/metrics/custom")
async def get_custom_metrics():
    """获取自定义业务指标."""
    try:
        # 这里可以添加自定义业务指标的计算逻辑
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "business": {
                "total_users": 0,  # TODO: 从数据库获取
                "active_conversations": 0,  # TODO: 从MongoDB获取
                "total_messages": 0,  # TODO: 从MongoDB获取
                "api_calls_today": 0,  # TODO: 从Redis获取
                "revenue_today": 0.0  # TODO: 从数据库获取
            },
            "performance": {
                "avg_response_time_ms": 0,  # TODO: 计算平均响应时间
                "error_rate": 0.0,  # TODO: 计算错误率
                "cache_hit_rate": 0.0  # TODO: 计算缓存命中率
            }
        }
        
        return metrics
        
    except Exception as e:
        logger.error(f"Failed to get custom metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get metrics"
        )


@router.post("/metrics/record")
async def record_metric(
    metric_type: str,
    value: float = 1,
    labels: Optional[Dict] = None
):
    """记录自定义指标."""
    try:
        # 记录业务指标
        business_metrics.labels(
            metric_type=metric_type,
            status="success"
        ).inc(value)
        
        # 可以将指标存储到Redis或时序数据库
        metric_key = f"metrics:{metric_type}:{datetime.utcnow().strftime('%Y%m%d')}"
        await redis_client.hincrby(metric_key, "count", int(value))
        await redis_client.expire(metric_key, 86400 * 7)  # 保留7天
        
        return {
            "success": True,
            "metric_type": metric_type,
            "value": value,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to record metric: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record metric"
        )


@router.get("/debug/connections")
async def debug_connections():
    """调试连接信息."""
    try:
        # PostgreSQL连接池信息
        pg_info = {
            "size": engine.pool.size() if hasattr(engine.pool, 'size') else 0,
            "checked_in": engine.pool.checkedin() if hasattr(engine.pool, 'checkedin') else 0,
            "checked_out": engine.pool.checkedout() if hasattr(engine.pool, 'checkedout') else 0,
            "overflow": engine.pool.overflow() if hasattr(engine.pool, 'overflow') else 0
        }
        
        # Redis连接信息
        redis_info = await redis_client.info()
        redis_clients = {
            "connected_clients": redis_info.get("connected_clients", 0),
            "blocked_clients": redis_info.get("blocked_clients", 0)
        }
        
        # 系统网络连接
        net_connections = psutil.net_connections()
        connection_summary = {
            "total": len(net_connections),
            "established": len([c for c in net_connections if c.status == 'ESTABLISHED']),
            "listen": len([c for c in net_connections if c.status == 'LISTEN']),
            "time_wait": len([c for c in net_connections if c.status == 'TIME_WAIT'])
        }
        
        return {
            "postgresql": pg_info,
            "redis": redis_clients,
            "system": connection_summary
        }
        
    except Exception as e:
        logger.error(f"Failed to get connection debug info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get debug info"
        )