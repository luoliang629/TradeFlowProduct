"""指标收集中间件."""

import time
from typing import Callable

from fastapi import Request, Response
from prometheus_client import Counter, Histogram, Gauge

from app.core.logging import get_logger

logger = get_logger(__name__)

# 定义Prometheus指标
request_count = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status_code']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint']
)

request_size = Histogram(
    'http_request_size_bytes',
    'HTTP request size in bytes',
    ['method', 'endpoint']
)

response_size = Histogram(
    'http_response_size_bytes',
    'HTTP response size in bytes',
    ['method', 'endpoint']
)

active_requests = Gauge(
    'http_requests_active',
    'Number of active HTTP requests'
)

error_count = Counter(
    'http_errors_total',
    'Total number of HTTP errors',
    ['method', 'endpoint', 'error_type']
)


class MetricsMiddleware:
    """指标收集中间件."""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """处理请求并收集指标."""
        # 记录请求开始时间
        start_time = time.time()
        
        # 提取路径信息
        path = request.url.path
        method = request.method
        
        # 规范化路径（移除路径参数的具体值）
        endpoint = self._normalize_path(path)
        
        # 增加活跃请求计数
        active_requests.inc()
        
        try:
            # 记录请求大小
            content_length = request.headers.get('content-length')
            if content_length:
                request_size.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(int(content_length))
            
            # 处理请求
            response = await call_next(request)
            
            # 记录响应指标
            duration = time.time() - start_time
            status_code = response.status_code
            
            # 记录请求计数
            request_count.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code
            ).inc()
            
            # 记录请求时长
            request_duration.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
            
            # 记录响应大小
            response_length = response.headers.get('content-length')
            if response_length:
                response_size.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(int(response_length))
            
            # 记录错误
            if status_code >= 400:
                error_type = self._get_error_type(status_code)
                error_count.labels(
                    method=method,
                    endpoint=endpoint,
                    error_type=error_type
                ).inc()
            
            # 添加响应头
            response.headers['X-Request-ID'] = request.state.request_id if hasattr(request.state, 'request_id') else 'unknown'
            response.headers['X-Response-Time'] = f"{duration:.3f}"
            
            return response
            
        except Exception as e:
            # 记录异常
            duration = time.time() - start_time
            
            error_count.labels(
                method=method,
                endpoint=endpoint,
                error_type='exception'
            ).inc()
            
            request_count.labels(
                method=method,
                endpoint=endpoint,
                status_code=500
            ).inc()
            
            request_duration.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
            
            logger.error(f"Request failed: {e}")
            raise
            
        finally:
            # 减少活跃请求计数
            active_requests.dec()
    
    def _normalize_path(self, path: str) -> str:
        """
        规范化路径，将路径参数替换为占位符.
        
        例如: /users/123 -> /users/{id}
        """
        # 常见的路径模式
        patterns = [
            (r'/users/\d+', '/users/{id}'),
            (r'/products/\d+', '/products/{id}'),
            (r'/conversations/[\w-]+', '/conversations/{id}'),
            (r'/files/\d+', '/files/{id}'),
            (r'/api/v\d+', '/api/{version}')
        ]
        
        import re
        normalized = path
        
        for pattern, replacement in patterns:
            normalized = re.sub(pattern, replacement, normalized)
        
        return normalized
    
    def _get_error_type(self, status_code: int) -> str:
        """根据状态码获取错误类型."""
        if 400 <= status_code < 500:
            return 'client_error'
        elif 500 <= status_code < 600:
            return 'server_error'
        else:
            return 'unknown'


class PerformanceMonitoringMiddleware:
    """性能监控中间件."""
    
    def __init__(self, app, slow_request_threshold: float = 1.0):
        """
        初始化性能监控中间件.
        
        Args:
            app: FastAPI应用
            slow_request_threshold: 慢请求阈值（秒）
        """
        self.app = app
        self.slow_request_threshold = slow_request_threshold
        
        # 慢请求计数器
        self.slow_requests = Counter(
            'http_slow_requests_total',
            'Total number of slow HTTP requests',
            ['method', 'endpoint']
        )
    
    async def __call__(self, scope, receive, send):
        """监控请求性能."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
            
        start_time = time.time()
        
        # 获取请求信息
        path = scope["path"]
        method = scope["method"]
        
        async def wrapped_send(message):
            if message["type"] == "http.response.start":
                # 计算耗时
                duration = time.time() - start_time
                
                # 检查是否为慢请求
                if duration > self.slow_request_threshold:
                    endpoint = self._normalize_path(path)
                    
                    self.slow_requests.labels(
                        method=method,
                        endpoint=endpoint
                    ).inc()
                    
                    logger.warning(
                        f"Slow request detected: {method} {path} took {duration:.3f}s"
                    )
            
            await send(message)
        
        await self.app(scope, receive, wrapped_send)
    
    def _normalize_path(self, path: str) -> str:
        """规范化路径."""
        # 复用MetricsMiddleware的规范化逻辑
        import re
        patterns = [
            (r'/users/\d+', '/users/{id}'),
            (r'/products/\d+', '/products/{id}'),
            (r'/conversations/[\w-]+', '/conversations/{id}'),
            (r'/files/\d+', '/files/{id}')
        ]
        
        normalized = path
        for pattern, replacement in patterns:
            normalized = re.sub(pattern, replacement, normalized)
        
        return normalized