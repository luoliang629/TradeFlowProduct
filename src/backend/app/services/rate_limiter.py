"""API限流服务."""

import time
from typing import Optional, Tuple

from app.core.logging import get_logger
from app.utils.redis_client import redis_client

logger = get_logger(__name__)


class RateLimiter:
    """限流器实现."""
    
    def __init__(
        self,
        key_prefix: str = "rate_limit",
        default_limit: int = 100,
        default_window: int = 60
    ):
        """
        初始化限流器.
        
        Args:
            key_prefix: Redis键前缀
            default_limit: 默认请求限制
            default_window: 默认时间窗口（秒）
        """
        self.key_prefix = key_prefix
        self.default_limit = default_limit
        self.default_window = default_window
    
    async def check_rate_limit(
        self,
        identifier: str,
        limit: Optional[int] = None,
        window: Optional[int] = None,
        cost: int = 1
    ) -> Tuple[bool, int, int]:
        """
        检查限流.
        
        Args:
            identifier: 标识符（如用户ID、IP地址）
            limit: 请求限制
            window: 时间窗口（秒）
            cost: 本次请求消耗
            
        Returns:
            (是否允许, 剩余次数, 重置时间)
        """
        limit = limit or self.default_limit
        window = window or self.default_window
        
        key = f"{self.key_prefix}:{identifier}"
        now = int(time.time())
        
        try:
            # 使用滑动窗口算法
            pipeline = redis_client.pipeline()
            
            # 移除过期的记录
            pipeline.zremrangebyscore(key, 0, now - window)
            
            # 获取当前窗口内的请求数
            pipeline.zcard(key)
            
            # 执行管道
            results = await pipeline.execute()
            current_count = results[1]
            
            # 检查是否超限
            if current_count + cost > limit:
                remaining = max(0, limit - current_count)
                reset_time = now + window
                return False, remaining, reset_time
            
            # 添加新的请求记录
            await redis_client.zadd(key, {f"{now}:{time.time_ns()}": now})
            await redis_client.expire(key, window)
            
            remaining = limit - current_count - cost
            reset_time = now + window
            
            return True, remaining, reset_time
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            # 出错时允许请求通过，避免影响服务
            return True, 0, 0
    
    async def get_rate_limit_info(
        self,
        identifier: str,
        limit: Optional[int] = None,
        window: Optional[int] = None
    ) -> Tuple[int, int, int]:
        """
        获取限流信息.
        
        Args:
            identifier: 标识符
            limit: 请求限制
            window: 时间窗口
            
        Returns:
            (已使用次数, 剩余次数, 重置时间)
        """
        limit = limit or self.default_limit
        window = window or self.default_window
        
        key = f"{self.key_prefix}:{identifier}"
        now = int(time.time())
        
        try:
            # 移除过期记录并获取当前计数
            await redis_client.zremrangebyscore(key, 0, now - window)
            current_count = await redis_client.zcard(key)
            
            remaining = max(0, limit - current_count)
            reset_time = now + window
            
            return current_count, remaining, reset_time
            
        except Exception as e:
            logger.error(f"Failed to get rate limit info: {e}")
            return 0, limit, 0


class MultiDimensionalRateLimiter:
    """多维度限流器."""
    
    def __init__(self):
        """初始化多维度限流器."""
        # 用户级限流
        self.user_limiter = RateLimiter(
            key_prefix="rate_limit:user",
            default_limit=1000,
            default_window=3600  # 1小时
        )
        
        # IP级限流
        self.ip_limiter = RateLimiter(
            key_prefix="rate_limit:ip",
            default_limit=100,
            default_window=60  # 1分钟
        )
        
        # API端点级限流
        self.endpoint_limiter = RateLimiter(
            key_prefix="rate_limit:endpoint",
            default_limit=50,
            default_window=60  # 1分钟
        )
        
        # 全局限流
        self.global_limiter = RateLimiter(
            key_prefix="rate_limit:global",
            default_limit=10000,
            default_window=60  # 1分钟
        )
    
    async def check_limits(
        self,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        endpoint: Optional[str] = None,
        custom_limits: Optional[dict] = None
    ) -> Tuple[bool, dict]:
        """
        检查多维度限流.
        
        Args:
            user_id: 用户ID
            ip_address: IP地址
            endpoint: API端点
            custom_limits: 自定义限制
            
        Returns:
            (是否允许, 限流信息)
        """
        results = {}
        
        # 检查用户级限流
        if user_id:
            user_limit = custom_limits.get("user_limit") if custom_limits else None
            user_window = custom_limits.get("user_window") if custom_limits else None
            
            allowed, remaining, reset = await self.user_limiter.check_rate_limit(
                str(user_id),
                limit=user_limit,
                window=user_window
            )
            
            results["user"] = {
                "allowed": allowed,
                "remaining": remaining,
                "reset": reset
            }
            
            if not allowed:
                return False, results
        
        # 检查IP级限流
        if ip_address:
            ip_limit = custom_limits.get("ip_limit") if custom_limits else None
            ip_window = custom_limits.get("ip_window") if custom_limits else None
            
            allowed, remaining, reset = await self.ip_limiter.check_rate_limit(
                ip_address,
                limit=ip_limit,
                window=ip_window
            )
            
            results["ip"] = {
                "allowed": allowed,
                "remaining": remaining,
                "reset": reset
            }
            
            if not allowed:
                return False, results
        
        # 检查端点级限流
        if endpoint:
            endpoint_limit = custom_limits.get("endpoint_limit") if custom_limits else None
            endpoint_window = custom_limits.get("endpoint_window") if custom_limits else None
            
            allowed, remaining, reset = await self.endpoint_limiter.check_rate_limit(
                endpoint,
                limit=endpoint_limit,
                window=endpoint_window
            )
            
            results["endpoint"] = {
                "allowed": allowed,
                "remaining": remaining,
                "reset": reset
            }
            
            if not allowed:
                return False, results
        
        # 检查全局限流
        allowed, remaining, reset = await self.global_limiter.check_rate_limit("global")
        results["global"] = {
            "allowed": allowed,
            "remaining": remaining,
            "reset": reset
        }
        
        return allowed, results


# 全局限流器实例
rate_limiter = RateLimiter()
multi_rate_limiter = MultiDimensionalRateLimiter()