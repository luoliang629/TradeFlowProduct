"""
Agent性能优化器
包含Runner实例池管理、响应缓存策略、异步处理优化等功能
"""

import asyncio
import hashlib
import json
import time
from typing import Dict, Any, Optional, List
from collections import defaultdict
from datetime import datetime, timedelta

from app.core.logging import get_logger
from app.utils.redis_client import get_redis
from app.config import settings

logger = get_logger(__name__)


class RunnerPool:
    """Runner实例池管理器"""
    
    def __init__(self, max_pool_size: int = 5, idle_timeout: int = 300):
        self.max_pool_size = max_pool_size
        self.idle_timeout = idle_timeout  # 空闲超时时间（秒）
        self._pool: List[Dict[str, Any]] = []
        self._lock = asyncio.Lock()
        self._stats = {
            "created": 0,
            "reused": 0,
            "expired": 0,
            "max_pool_size_reached": 0
        }
    
    async def get_runner(self) -> Any:
        """
        获取Runner实例
        
        Returns:
            Runner实例
        """
        async with self._lock:
            # 清理过期的Runner实例
            await self._cleanup_expired_runners()
            
            # 查找可用的Runner实例
            for runner_info in self._pool:
                if not runner_info["in_use"]:
                    runner_info["in_use"] = True
                    runner_info["last_used"] = time.time()
                    self._stats["reused"] += 1
                    
                    logger.debug(f"复用Runner实例，池大小: {len(self._pool)}")
                    return runner_info["runner"]
            
            # 如果池中没有可用实例且未达到最大大小，创建新实例
            if len(self._pool) < self.max_pool_size:
                runner = await self._create_new_runner()
                if runner:
                    runner_info = {
                        "runner": runner,
                        "created_at": time.time(),
                        "last_used": time.time(),
                        "in_use": True,
                        "use_count": 1
                    }
                    
                    self._pool.append(runner_info)
                    self._stats["created"] += 1
                    
                    logger.info(f"创建新Runner实例，池大小: {len(self._pool)}")
                    return runner
            
            # 池已满，等待或使用最少使用的实例
            self._stats["max_pool_size_reached"] += 1
            logger.warning(f"Runner实例池已满 ({self.max_pool_size})，等待可用实例")
            
            # 简单策略：等待一小段时间后重试
            await asyncio.sleep(0.1)
            return await self.get_runner()
    
    async def return_runner(self, runner: Any) -> None:
        """
        归还Runner实例到池中
        
        Args:
            runner: Runner实例
        """
        async with self._lock:
            for runner_info in self._pool:
                if runner_info["runner"] is runner:
                    runner_info["in_use"] = False
                    runner_info["last_used"] = time.time()
                    runner_info["use_count"] += 1
                    
                    logger.debug(f"归还Runner实例到池，使用次数: {runner_info['use_count']}")
                    break
    
    async def _create_new_runner(self) -> Optional[Any]:
        """创建新的Runner实例"""
        try:
            from google.adk.core import Runner
            runner = Runner()
            return runner
        except Exception as e:
            logger.error(f"创建Runner实例失败: {e}")
            return None
    
    async def _cleanup_expired_runners(self) -> None:
        """清理过期的Runner实例"""
        current_time = time.time()
        expired_runners = []
        
        for i, runner_info in enumerate(self._pool):
            if (not runner_info["in_use"] and 
                current_time - runner_info["last_used"] > self.idle_timeout):
                expired_runners.append(i)
        
        # 从后往前删除，避免索引错位
        for i in reversed(expired_runners):
            removed = self._pool.pop(i)
            self._stats["expired"] += 1
            logger.debug(f"清理过期Runner实例，使用次数: {removed['use_count']}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取池统计信息"""
        async with self._lock:
            return {
                "pool_size": len(self._pool),
                "active_runners": sum(1 for r in self._pool if r["in_use"]),
                "idle_runners": sum(1 for r in self._pool if not r["in_use"]),
                "max_pool_size": self.max_pool_size,
                "stats": self._stats.copy()
            }
    
    async def cleanup(self) -> None:
        """清理所有Runner实例"""
        async with self._lock:
            self._pool.clear()
            logger.info("Runner实例池已清理")


class ResponseCache:
    """响应缓存管理器"""
    
    def __init__(self, default_ttl: int = 3600, max_cache_size: int = 1000):
        self.default_ttl = default_ttl  # 默认缓存时间（秒）
        self.max_cache_size = max_cache_size
        self._cache_prefix = "agent_response_cache"
    
    def _generate_cache_key(self, user_id: str, query: str, context: Dict[str, Any] = None) -> str:
        """
        生成缓存键
        
        Args:
            user_id: 用户ID
            query: 查询内容
            context: 查询上下文
            
        Returns:
            缓存键
        """
        # 创建查询指纹
        query_data = {
            "query": query.strip().lower(),
            "user_id": user_id,
            "context": context or {}
        }
        
        query_json = json.dumps(query_data, sort_keys=True, ensure_ascii=False)
        query_hash = hashlib.md5(query_json.encode('utf-8')).hexdigest()
        
        return f"{self._cache_prefix}:{query_hash}"
    
    async def get_cached_response(
        self, 
        user_id: str, 
        query: str, 
        context: Dict[str, Any] = None
    ) -> Optional[Dict[str, Any]]:
        """
        获取缓存的响应
        
        Args:
            user_id: 用户ID
            query: 查询内容
            context: 查询上下文
            
        Returns:
            缓存的响应数据，如果不存在返回None
        """
        if not settings.AGENT_ENABLE_CACHE:
            return None
        
        try:
            redis = await get_redis()
            cache_key = self._generate_cache_key(user_id, query, context)
            
            cached_data = await redis.get(cache_key)
            if cached_data:
                response_data = json.loads(cached_data)
                
                # 检查缓存是否过期（双重检查）
                if response_data.get("expires_at", 0) > time.time():
                    logger.info(f"命中缓存响应 - 用户: {user_id}")
                    return response_data
            
            return None
            
        except Exception as e:
            logger.error(f"获取缓存响应失败: {e}")
            return None
    
    async def cache_response(
        self,
        user_id: str,
        query: str,
        response: str,
        context: Dict[str, Any] = None,
        ttl: Optional[int] = None
    ) -> bool:
        """
        缓存响应
        
        Args:
            user_id: 用户ID
            query: 查询内容
            response: Agent响应
            context: 查询上下文
            ttl: 缓存时间（秒）
            
        Returns:
            是否缓存成功
        """
        if not settings.AGENT_ENABLE_CACHE:
            return False
        
        try:
            redis = await get_redis()
            cache_key = self._generate_cache_key(user_id, query, context)
            
            ttl = ttl or self.default_ttl
            expires_at = time.time() + ttl
            
            cache_data = {
                "response": response,
                "user_id": user_id,
                "query": query,
                "context": context,
                "cached_at": time.time(),
                "expires_at": expires_at
            }
            
            await redis.setex(
                cache_key,
                ttl,
                json.dumps(cache_data, ensure_ascii=False)
            )
            
            logger.debug(f"缓存响应 - 用户: {user_id}, TTL: {ttl}s")
            return True
            
        except Exception as e:
            logger.error(f"缓存响应失败: {e}")
            return False
    
    async def invalidate_user_cache(self, user_id: str) -> int:
        """
        清除用户的所有缓存
        
        Args:
            user_id: 用户ID
            
        Returns:
            清除的缓存数量
        """
        try:
            redis = await get_redis()
            pattern = f"{self._cache_prefix}:*"
            
            keys = await redis.keys(pattern)
            if not keys:
                return 0
            
            # 检查每个键是否属于该用户
            user_keys = []
            for key in keys:
                try:
                    data = await redis.get(key)
                    if data:
                        cache_info = json.loads(data)
                        if cache_info.get("user_id") == user_id:
                            user_keys.append(key)
                except:
                    continue
            
            if user_keys:
                await redis.delete(*user_keys)
                logger.info(f"清除用户 {user_id} 的 {len(user_keys)} 个缓存")
            
            return len(user_keys)
            
        except Exception as e:
            logger.error(f"清除用户缓存失败: {e}")
            return 0
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        try:
            redis = await get_redis()
            pattern = f"{self._cache_prefix}:*"
            keys = await redis.keys(pattern)
            
            total_keys = len(keys)
            valid_keys = 0
            expired_keys = 0
            current_time = time.time()
            
            for key in keys:
                try:
                    data = await redis.get(key)
                    if data:
                        cache_info = json.loads(data)
                        if cache_info.get("expires_at", 0) > current_time:
                            valid_keys += 1
                        else:
                            expired_keys += 1
                except:
                    expired_keys += 1
            
            return {
                "total_cached_responses": total_keys,
                "valid_responses": valid_keys,
                "expired_responses": expired_keys,
                "cache_enabled": settings.AGENT_ENABLE_CACHE,
                "default_ttl": self.default_ttl
            }
            
        except Exception as e:
            logger.error(f"获取缓存统计失败: {e}")
            return {"error": str(e)}


class TokenUsageMonitor:
    """Token使用监控器"""
    
    def __init__(self):
        self._usage_stats = defaultdict(lambda: {
            "total_tokens": 0,
            "requests": 0,
            "last_reset": datetime.utcnow(),
            "daily_limit_reached": False
        })
        self._lock = asyncio.Lock()
    
    async def record_usage(
        self, 
        user_id: str, 
        input_tokens: int, 
        output_tokens: int
    ) -> bool:
        """
        记录Token使用情况
        
        Args:
            user_id: 用户ID
            input_tokens: 输入Token数
            output_tokens: 输出Token数
            
        Returns:
            是否在限额内
        """
        async with self._lock:
            today = datetime.utcnow().date()
            user_stats = self._usage_stats[user_id]
            
            # 如果是新的一天，重置统计
            if user_stats["last_reset"].date() != today:
                user_stats["total_tokens"] = 0
                user_stats["requests"] = 0
                user_stats["daily_limit_reached"] = False
                user_stats["last_reset"] = datetime.utcnow()
            
            # 更新使用统计
            total_tokens = input_tokens + output_tokens
            user_stats["total_tokens"] += total_tokens
            user_stats["requests"] += 1
            
            # 检查是否超过限额（这里可以配置每日Token限额）
            daily_limit = 50000  # 示例：每日50k tokens
            if user_stats["total_tokens"] > daily_limit:
                user_stats["daily_limit_reached"] = True
                logger.warning(f"用户 {user_id} 达到每日Token限额")
                return False
            
            return True
    
    async def get_user_usage(self, user_id: str) -> Dict[str, Any]:
        """获取用户使用情况"""
        async with self._lock:
            stats = self._usage_stats.get(user_id, {})
            return {
                "user_id": user_id,
                "today_tokens": stats.get("total_tokens", 0),
                "today_requests": stats.get("requests", 0),
                "limit_reached": stats.get("daily_limit_reached", False),
                "last_reset": stats.get("last_reset", datetime.utcnow()).isoformat()
            }


class AgentPerformanceOptimizer:
    """Agent性能优化器主类"""
    
    def __init__(self):
        self.runner_pool = RunnerPool(
            max_pool_size=getattr(settings, 'AGENT_RUNNER_POOL_SIZE', 5),
            idle_timeout=getattr(settings, 'AGENT_RUNNER_IDLE_TIMEOUT', 300)
        )
        self.response_cache = ResponseCache(
            default_ttl=getattr(settings, 'AGENT_CACHE_TTL', 3600),
            max_cache_size=getattr(settings, 'AGENT_CACHE_MAX_SIZE', 1000)
        )
        self.token_monitor = TokenUsageMonitor()
    
    async def get_optimized_runner(self) -> Any:
        """获取优化的Runner实例"""
        return await self.runner_pool.get_runner()
    
    async def return_runner(self, runner: Any) -> None:
        """归还Runner实例"""
        await self.runner_pool.return_runner(runner)
    
    async def get_cached_response_or_none(
        self, 
        user_id: str, 
        query: str, 
        context: Dict[str, Any] = None
    ) -> Optional[Dict[str, Any]]:
        """获取缓存响应"""
        return await self.response_cache.get_cached_response(user_id, query, context)
    
    async def cache_response_if_enabled(
        self,
        user_id: str,
        query: str,
        response: str,
        context: Dict[str, Any] = None,
        ttl: Optional[int] = None
    ) -> bool:
        """缓存响应"""
        return await self.response_cache.cache_response(user_id, query, response, context, ttl)
    
    async def check_token_usage(
        self, 
        user_id: str, 
        input_tokens: int = 0, 
        output_tokens: int = 0
    ) -> bool:
        """检查Token使用情况"""
        return await self.token_monitor.record_usage(user_id, input_tokens, output_tokens)
    
    async def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计信息"""
        runner_stats = await self.runner_pool.get_stats()
        cache_stats = await self.response_cache.get_cache_stats()
        
        return {
            "runner_pool": runner_stats,
            "response_cache": cache_stats,
            "optimizer_enabled": True,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def cleanup(self) -> None:
        """清理资源"""
        await self.runner_pool.cleanup()


# 全局性能优化器实例
performance_optimizer = AgentPerformanceOptimizer()