"""性能监控中间件."""

import asyncio
import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import get_logger

logger = get_logger(__name__)


class PerformanceMiddleware(BaseHTTPMiddleware):
    """性能监控中间件."""
    
    def __init__(self, app, slow_request_threshold: float = 1.0):
        """初始化性能监控中间件.
        
        Args:
            app: FastAPI应用实例
            slow_request_threshold: 慢请求阈值(秒)，超过此时间的请求会被记录
        """
        super().__init__(app)
        self.slow_request_threshold = slow_request_threshold
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求并监控性能."""
        # 记录开始时间和内存使用
        start_time = time.perf_counter()
        start_cpu_time = time.process_time()
        
        try:
            # 处理请求
            response = await call_next(request)
            
            # 计算性能指标
            end_time = time.perf_counter()
            end_cpu_time = time.process_time()
            
            total_time = end_time - start_time
            cpu_time = end_cpu_time - start_cpu_time
            
            # 添加性能头部信息
            response.headers["X-Response-Time"] = f"{total_time:.3f}s"
            response.headers["X-CPU-Time"] = f"{cpu_time:.3f}s"
            
            # 记录性能日志
            log_data = {
                "method": request.method,
                "url": str(request.url),
                "status_code": response.status_code,
                "response_time": round(total_time * 1000, 2),  # 毫秒
                "cpu_time": round(cpu_time * 1000, 2),  # 毫秒
            }
            
            # 如果是慢请求，记录警告日志
            if total_time > self.slow_request_threshold:
                logger.warning(
                    "Slow request detected",
                    **log_data,
                    threshold_ms=self.slow_request_threshold * 1000,
                )
            else:
                logger.info(
                    "Request performance",
                    **log_data,
                )
            
            return response
            
        except Exception as e:
            # 即使出现异常也要记录性能数据
            end_time = time.perf_counter()
            end_cpu_time = time.process_time()
            
            total_time = end_time - start_time
            cpu_time = end_cpu_time - start_cpu_time
            
            logger.error(
                "Request failed with performance data",
                method=request.method,
                url=str(request.url),
                response_time=round(total_time * 1000, 2),
                cpu_time=round(cpu_time * 1000, 2),
                error=str(e),
            )
            
            # 重新抛出异常
            raise


class RateLimitMiddleware(BaseHTTPMiddleware):
    """简单的速率限制中间件."""
    
    def __init__(self, app, requests_per_minute: int = 60):
        """初始化速率限制中间件.
        
        Args:
            app: FastAPI应用实例
            requests_per_minute: 每分钟允许的请求数
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_times = {}
        self.cleanup_interval = 60  # 每60秒清理一次过期记录
        self.last_cleanup = time.time()
    
    def _cleanup_old_requests(self) -> None:
        """清理过期的请求记录."""
        current_time = time.time()
        
        if current_time - self.last_cleanup > self.cleanup_interval:
            cutoff_time = current_time - 60  # 保留最近1分钟的记录
            
            for client_ip in list(self.request_times.keys()):
                self.request_times[client_ip] = [
                    req_time for req_time in self.request_times[client_ip]
                    if req_time > cutoff_time
                ]
                
                # 如果客户端没有最近的请求，删除记录
                if not self.request_times[client_ip]:
                    del self.request_times[client_ip]
            
            self.last_cleanup = current_time
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求并检查速率限制."""
        # 获取客户端IP
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # 清理过期记录
        self._cleanup_old_requests()
        
        # 获取客户端的请求历史
        if client_ip not in self.request_times:
            self.request_times[client_ip] = []
        
        # 检查最近1分钟的请求数量
        recent_requests = [
            req_time for req_time in self.request_times[client_ip]
            if req_time > current_time - 60
        ]
        
        # 检查是否超过限制
        if len(recent_requests) >= self.requests_per_minute:
            logger.warning(
                "Rate limit exceeded",
                client_ip=client_ip,
                request_count=len(recent_requests),
                limit=self.requests_per_minute,
                url=str(request.url),
            )
            
            from fastapi.responses import JSONResponse
            from app.schemas.common import ErrorResponse
            
            error_response = ErrorResponse(
                message="Rate limit exceeded",
                error_code="RATE_LIMIT_ERROR",
                details={
                    "limit": self.requests_per_minute,
                    "window": "1 minute",
                    "retry_after": 60,
                },
            )
            
            return JSONResponse(
                status_code=429,
                content=error_response.dict(),
                headers={"Retry-After": "60"},
            )
        
        # 记录当前请求时间
        self.request_times[client_ip].append(current_time)
        
        # 处理请求
        response = await call_next(request)
        
        # 添加速率限制头部信息
        remaining = max(0, self.requests_per_minute - len(recent_requests) - 1)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(current_time + 60))
        
        return response