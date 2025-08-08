"""Redis客户端配置模块."""

from typing import AsyncGenerator, Optional, Union

import redis.asyncio as redis
from redis.asyncio import ConnectionPool

from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class RedisClient:
    """Redis客户端管理器."""
    
    def __init__(self) -> None:
        """初始化Redis客户端."""
        self._pool: Optional[ConnectionPool] = None
        self._client: Optional[redis.Redis] = None
    
    @property
    def pool(self) -> ConnectionPool:
        """获取Redis连接池."""
        if not self._pool:
            self._pool = ConnectionPool.from_url(
                settings.redis_url,
                max_connections=50,
                retry_on_timeout=True,
                socket_keepalive=True,
                socket_keepalive_options={},
                health_check_interval=30,
            )
        return self._pool
    
    @property
    def client(self) -> redis.Redis:
        """获取Redis客户端."""
        if not self._client:
            self._client = redis.Redis(connection_pool=self.pool, decode_responses=True)
        return self._client
    
    async def close(self) -> None:
        """关闭Redis连接."""
        if self._client:
            await self._client.close()
            self._client = None
        
        if self._pool:
            await self._pool.disconnect()
            self._pool = None
        
        logger.info("Redis connection closed")
    
    async def ping(self) -> bool:
        """检查Redis连接状态."""
        try:
            return await self.client.ping()
        except Exception as e:
            logger.error("Redis ping failed", error=str(e))
            return False
    
    async def set(
        self,
        key: str,
        value: Union[str, bytes, int, float],
        ex: Optional[int] = None,
        px: Optional[int] = None,
        nx: bool = False,
        xx: bool = False,
    ) -> bool:
        """设置键值对."""
        try:
            return await self.client.set(key, value, ex=ex, px=px, nx=nx, xx=xx)
        except Exception as e:
            logger.error("Redis set failed", key=key, error=str(e))
            raise
    
    async def get(self, key: str) -> Optional[str]:
        """获取键值."""
        try:
            return await self.client.get(key)
        except Exception as e:
            logger.error("Redis get failed", key=key, error=str(e))
            raise
    
    async def delete(self, *keys: str) -> int:
        """删除键."""
        try:
            return await self.client.delete(*keys)
        except Exception as e:
            logger.error("Redis delete failed", keys=keys, error=str(e))
            raise
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在."""
        try:
            return bool(await self.client.exists(key))
        except Exception as e:
            logger.error("Redis exists failed", key=key, error=str(e))
            raise
    
    async def expire(self, key: str, time: int) -> bool:
        """设置键过期时间."""
        try:
            return await self.client.expire(key, time)
        except Exception as e:
            logger.error("Redis expire failed", key=key, error=str(e))
            raise
    
    async def hset(
        self,
        name: str,
        mapping: Optional[dict] = None,
        **kwargs: Union[str, bytes, int, float],
    ) -> int:
        """设置哈希表字段."""
        try:
            if mapping:
                return await self.client.hset(name, mapping=mapping)
            return await self.client.hset(name, **kwargs)
        except Exception as e:
            logger.error("Redis hset failed", name=name, error=str(e))
            raise
    
    async def hget(self, name: str, key: str) -> Optional[str]:
        """获取哈希表字段值."""
        try:
            return await self.client.hget(name, key)
        except Exception as e:
            logger.error("Redis hget failed", name=name, key=key, error=str(e))
            raise
    
    async def hgetall(self, name: str) -> dict:
        """获取哈希表所有字段."""
        try:
            return await self.client.hgetall(name)
        except Exception as e:
            logger.error("Redis hgetall failed", name=name, error=str(e))
            raise
    
    async def hdel(self, name: str, *keys: str) -> int:
        """删除哈希表字段."""
        try:
            return await self.client.hdel(name, *keys)
        except Exception as e:
            logger.error("Redis hdel failed", name=name, keys=keys, error=str(e))
            raise


# 全局Redis客户端实例
redis_client = RedisClient()


async def get_redis_client() -> redis.Redis:
    """获取Redis客户端依赖."""
    return redis_client.client


async def get_redis_manager() -> RedisClient:
    """获取Redis管理器依赖."""
    return redis_client


# Redis初始化和关闭事件
async def init_redis() -> None:
    """初始化Redis连接."""
    try:
        ping_result = await redis_client.ping()
        if ping_result:
            logger.info("Redis connection established")
        else:
            raise Exception("Redis ping failed")
    except Exception as e:
        logger.error("Redis initialization failed", error=str(e))
        raise


async def close_redis() -> None:
    """关闭Redis连接."""
    try:
        await redis_client.close()
    except Exception as e:
        logger.error("Error closing Redis connection", error=str(e))
        raise