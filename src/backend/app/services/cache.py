"""缓存服务实现."""

import json
import pickle
from datetime import datetime, timedelta
from typing import Any, Callable, Optional, Union

from app.core.logging import get_logger
from app.utils.redis_client import redis_client

logger = get_logger(__name__)


class CacheKey:
    """缓存键管理."""
    
    # 缓存键前缀
    USER = "user"
    PRODUCT = "product"
    CONVERSATION = "conversation"
    FILE = "file"
    BUYER = "buyer"
    SUPPLIER = "supplier"
    STATS = "stats"
    
    @staticmethod
    def user_profile(user_id: int) -> str:
        """用户资料缓存键."""
        return f"{CacheKey.USER}:profile:{user_id}"
    
    @staticmethod
    def user_subscription(user_id: int) -> str:
        """用户订阅缓存键."""
        return f"{CacheKey.USER}:subscription:{user_id}"
    
    @staticmethod
    def product_detail(product_id: int) -> str:
        """产品详情缓存键."""
        return f"{CacheKey.PRODUCT}:detail:{product_id}"
    
    @staticmethod
    def product_list(user_id: int, page: int = 1) -> str:
        """产品列表缓存键."""
        return f"{CacheKey.PRODUCT}:list:{user_id}:{page}"
    
    @staticmethod
    def conversation_detail(conversation_id: str) -> str:
        """对话详情缓存键."""
        return f"{CacheKey.CONVERSATION}:detail:{conversation_id}"
    
    @staticmethod
    def conversation_list(user_id: int, page: int = 1) -> str:
        """对话列表缓存键."""
        return f"{CacheKey.CONVERSATION}:list:{user_id}:{page}"
    
    @staticmethod
    def file_preview(file_id: int) -> str:
        """文件预览缓存键."""
        return f"{CacheKey.FILE}:preview:{file_id}"
    
    @staticmethod
    def buyer_recommendations(user_id: int) -> str:
        """买家推荐缓存键."""
        return f"{CacheKey.BUYER}:recommendations:{user_id}"
    
    @staticmethod
    def supplier_search(query_hash: str) -> str:
        """供应商搜索缓存键."""
        return f"{CacheKey.SUPPLIER}:search:{query_hash}"
    
    @staticmethod
    def user_stats(user_id: int, stat_type: str) -> str:
        """用户统计缓存键."""
        return f"{CacheKey.STATS}:{stat_type}:{user_id}"


class CacheService:
    """缓存服务."""
    
    def __init__(self):
        """初始化缓存服务."""
        self.default_ttl = 3600  # 默认1小时
        self.serializer = "json"  # 默认使用JSON序列化
    
    async def get(
        self,
        key: str,
        default: Any = None,
        deserializer: Optional[Callable] = None
    ) -> Any:
        """
        获取缓存.
        
        Args:
            key: 缓存键
            default: 默认值
            deserializer: 反序列化函数
            
        Returns:
            缓存值或默认值
        """
        try:
            value = await redis_client.get(key)
            
            if value is None:
                return default
            
            # 反序列化
            if deserializer:
                return deserializer(value)
            elif self.serializer == "json":
                return json.loads(value)
            elif self.serializer == "pickle":
                return pickle.loads(value)
            else:
                return value
            
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return default
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        serializer: Optional[Callable] = None
    ) -> bool:
        """
        设置缓存.
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒）
            serializer: 序列化函数
            
        Returns:
            是否成功
        """
        try:
            ttl = ttl or self.default_ttl
            
            # 序列化
            if serializer:
                serialized_value = serializer(value)
            elif self.serializer == "json":
                serialized_value = json.dumps(value, ensure_ascii=False)
            elif self.serializer == "pickle":
                serialized_value = pickle.dumps(value)
            else:
                serialized_value = value
            
            await redis_client.setex(key, ttl, serialized_value)
            return True
            
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: Union[str, list]) -> int:
        """
        删除缓存.
        
        Args:
            key: 缓存键或键列表
            
        Returns:
            删除的键数量
        """
        try:
            if isinstance(key, list):
                return await redis_client.delete(*key)
            else:
                return await redis_client.delete(key)
            
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return 0
    
    async def exists(self, key: str) -> bool:
        """
        检查缓存是否存在.
        
        Args:
            key: 缓存键
            
        Returns:
            是否存在
        """
        try:
            return await redis_client.exists(key) > 0
            
        except Exception as e:
            logger.error(f"Cache exists error: {e}")
            return False
    
    async def expire(self, key: str, ttl: int) -> bool:
        """
        设置过期时间.
        
        Args:
            key: 缓存键
            ttl: 过期时间（秒）
            
        Returns:
            是否成功
        """
        try:
            return await redis_client.expire(key, ttl)
            
        except Exception as e:
            logger.error(f"Cache expire error: {e}")
            return False
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """
        根据模式删除缓存.
        
        Args:
            pattern: 键模式
            
        Returns:
            删除的键数量
        """
        try:
            keys = []
            async for key in redis_client.scan_iter(match=pattern):
                keys.append(key)
            
            if keys:
                return await redis_client.delete(*keys)
            
            return 0
            
        except Exception as e:
            logger.error(f"Cache invalidate pattern error: {e}")
            return 0
    
    async def invalidate_user_cache(self, user_id: int) -> None:
        """清除用户相关缓存."""
        patterns = [
            f"{CacheKey.USER}:*:{user_id}",
            f"{CacheKey.PRODUCT}:list:{user_id}:*",
            f"{CacheKey.CONVERSATION}:list:{user_id}:*",
            f"{CacheKey.BUYER}:recommendations:{user_id}",
            f"{CacheKey.STATS}:*:{user_id}"
        ]
        
        for pattern in patterns:
            await self.invalidate_pattern(pattern)
    
    async def cache_warmup(self, user_id: int) -> None:
        """缓存预热."""
        # TODO: 实现缓存预热逻辑
        pass


class CacheDecorator:
    """缓存装饰器."""
    
    def __init__(
        self,
        key_func: Callable,
        ttl: int = 3600,
        cache_none: bool = False
    ):
        """
        初始化缓存装饰器.
        
        Args:
            key_func: 生成缓存键的函数
            ttl: 过期时间
            cache_none: 是否缓存None值
        """
        self.key_func = key_func
        self.ttl = ttl
        self.cache_none = cache_none
        self.cache_service = CacheService()
    
    def __call__(self, func: Callable) -> Callable:
        """装饰器实现."""
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = self.key_func(*args, **kwargs)
            
            # 尝试从缓存获取
            cached_value = await self.cache_service.get(cache_key)
            if cached_value is not None or (cached_value is None and self.cache_none):
                logger.debug(f"Cache hit: {cache_key}")
                return cached_value
            
            # 执行原函数
            result = await func(*args, **kwargs)
            
            # 缓存结果
            if result is not None or self.cache_none:
                await self.cache_service.set(cache_key, result, self.ttl)
            
            return result
        
        return wrapper


# 使用示例
def cache_key_for_product(product_id: int, **kwargs) -> str:
    """生成产品缓存键."""
    return CacheKey.product_detail(product_id)


# 装饰器使用示例
@CacheDecorator(key_func=cache_key_for_product, ttl=1800)
async def get_product_with_cache(product_id: int):
    """带缓存的产品获取."""
    # 实际的数据库查询逻辑
    pass


# 全局缓存服务实例
cache_service = CacheService()