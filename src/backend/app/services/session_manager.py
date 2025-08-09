"""
Agent会话管理器 - 管理用户会话状态和上下文
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from app.core.logging import get_logger
from app.utils.redis_client import get_redis_client
from app.config import settings

logger = get_logger(__name__)


class SessionManager:
    """Agent会话管理器"""
    
    def __init__(self):
        self.redis = None
        self._session_prefix = "agent_session"
        self._context_prefix = "agent_context"
        self._history_prefix = "agent_history"
        self.default_ttl = 3600 * 24  # 24小时
    
    async def _get_redis(self):
        """获取Redis连接"""
        if not self.redis:
            self.redis = await get_redis_client()
        return self.redis
    
    def _get_session_key(self, user_id: str, session_id: str) -> str:
        """获取会话存储键"""
        return f"{self._session_prefix}:{user_id}:{session_id}"
    
    def _get_context_key(self, user_id: str, session_id: str) -> str:
        """获取上下文存储键"""
        return f"{self._context_prefix}:{user_id}:{session_id}"
    
    def _get_history_key(self, user_id: str, session_id: str) -> str:
        """获取历史记录存储键"""
        return f"{self._history_prefix}:{user_id}:{session_id}"
    
    async def create_session(
        self, 
        user_id: str, 
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        创建新会话
        
        Args:
            user_id: 用户ID
            session_id: 会话ID（可选，不提供则自动生成）
            metadata: 会话元数据
            
        Returns:
            会话ID
        """
        if not session_id:
            session_id = str(uuid.uuid4())
        
        try:
            redis = await self._get_redis()
            
            session_data = {
                "user_id": user_id,
                "session_id": session_id,
                "created_at": datetime.utcnow().isoformat(),
                "last_active": datetime.utcnow().isoformat(),
                "message_count": 0,
                "status": "active",
                "metadata": metadata or {}
            }
            
            session_key = self._get_session_key(user_id, session_id)
            
            # 存储会话信息
            await redis.hset(
                session_key,
                mapping={k: json.dumps(v) if not isinstance(v, str) else v 
                        for k, v in session_data.items()}
            )
            await redis.expire(session_key, self.default_ttl)
            
            # 初始化上下文
            await self._initialize_context(user_id, session_id)
            
            logger.info(f"创建新会话 - 用户: {user_id}, 会话: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"创建会话失败: {e}")
            raise RuntimeError(f"会话创建失败: {e}")
    
    async def get_session(self, user_id: str, session_id: str) -> Optional[Dict[str, Any]]:
        """
        获取会话信息
        
        Args:
            user_id: 用户ID
            session_id: 会话ID
            
        Returns:
            会话数据，不存在返回None
        """
        try:
            redis = await self._get_redis()
            session_key = self._get_session_key(user_id, session_id)
            
            session_raw = await redis.hgetall(session_key)
            if not session_raw:
                return None
            
            # 反序列化数据
            session_data = {}
            for key, value in session_raw.items():
                try:
                    session_data[key] = json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    session_data[key] = value
            
            return session_data
            
        except Exception as e:
            logger.error(f"获取会话失败: {e}")
            return None
    
    async def update_session_activity(self, user_id: str, session_id: str) -> None:
        """更新会话活跃时间"""
        try:
            redis = await self._get_redis()
            session_key = self._get_session_key(user_id, session_id)
            
            # 更新最后活跃时间
            await redis.hset(
                session_key,
                "last_active",
                datetime.utcnow().isoformat()
            )
            
            # 重新设置过期时间
            await redis.expire(session_key, self.default_ttl)
            
        except Exception as e:
            logger.error(f"更新会话活跃时间失败: {e}")
    
    async def _initialize_context(self, user_id: str, session_id: str) -> None:
        """初始化会话上下文"""
        try:
            redis = await self._get_redis()
            context_key = self._get_context_key(user_id, session_id)
            
            initial_context = {
                "conversation_turns": 0,
                "current_topic": "",
                "user_preferences": {},
                "agent_memory": {},
                "tool_usage_history": [],
                "created_at": datetime.utcnow().isoformat()
            }
            
            await redis.set(
                context_key,
                json.dumps(initial_context),
                ex=self.default_ttl
            )
            
        except Exception as e:
            logger.error(f"初始化上下文失败: {e}")
    
    async def get_context(self, user_id: str, session_id: str) -> Dict[str, Any]:
        """获取会话上下文"""
        try:
            redis = await self._get_redis()
            context_key = self._get_context_key(user_id, session_id)
            
            context_raw = await redis.get(context_key)
            if not context_raw:
                # 如果上下文不存在，创建默认上下文
                await self._initialize_context(user_id, session_id)
                context_raw = await redis.get(context_key)
            
            return json.loads(context_raw) if context_raw else {}
            
        except Exception as e:
            logger.error(f"获取上下文失败: {e}")
            return {}
    
    async def update_context(
        self, 
        user_id: str, 
        session_id: str, 
        context_updates: Dict[str, Any]
    ) -> None:
        """更新会话上下文"""
        try:
            redis = await self._get_redis()
            context_key = self._get_context_key(user_id, session_id)
            
            # 获取当前上下文
            current_context = await self.get_context(user_id, session_id)
            
            # 合并更新
            current_context.update(context_updates)
            current_context["updated_at"] = datetime.utcnow().isoformat()
            
            # 保存更新后的上下文
            await redis.set(
                context_key,
                json.dumps(current_context),
                ex=self.default_ttl
            )
            
        except Exception as e:
            logger.error(f"更新上下文失败: {e}")
    
    async def add_message_to_history(
        self,
        user_id: str,
        session_id: str,
        role: str,  # "user" or "assistant"
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """添加消息到历史记录"""
        try:
            redis = await self._get_redis()
            history_key = self._get_history_key(user_id, session_id)
            
            message = {
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": metadata or {}
            }
            
            # 添加到历史记录列表
            await redis.lpush(history_key, json.dumps(message))
            await redis.expire(history_key, self.default_ttl)
            
            # 更新会话消息计数
            session_key = self._get_session_key(user_id, session_id)
            await redis.hincrby(session_key, "message_count", 1)
            
        except Exception as e:
            logger.error(f"添加历史消息失败: {e}")
    
    async def get_message_history(
        self,
        user_id: str,
        session_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """获取消息历史记录"""
        try:
            redis = await self._get_redis()
            history_key = self._get_history_key(user_id, session_id)
            
            # 获取最近的消息（Redis列表是LIFO，所以需要反转）
            messages_raw = await redis.lrange(history_key, 0, limit - 1)
            
            messages = []
            for msg_raw in reversed(messages_raw):
                try:
                    message = json.loads(msg_raw)
                    messages.append(message)
                except json.JSONDecodeError:
                    logger.warning(f"无法解析历史消息: {msg_raw}")
                    continue
            
            return messages
            
        except Exception as e:
            logger.error(f"获取消息历史失败: {e}")
            return []
    
    async def close_session(self, user_id: str, session_id: str) -> None:
        """关闭会话"""
        try:
            redis = await self._get_redis()
            session_key = self._get_session_key(user_id, session_id)
            
            # 更新会话状态
            await redis.hset(session_key, "status", "closed")
            await redis.hset(session_key, "closed_at", datetime.utcnow().isoformat())
            
            logger.info(f"会话已关闭 - 用户: {user_id}, 会话: {session_id}")
            
        except Exception as e:
            logger.error(f"关闭会话失败: {e}")
    
    async def cleanup_expired_sessions(self) -> int:
        """清理过期会话"""
        try:
            redis = await self._get_redis()
            
            # 查找所有会话键
            pattern = f"{self._session_prefix}:*"
            keys = await redis.keys(pattern)
            
            cleaned_count = 0
            expired_threshold = datetime.utcnow() - timedelta(days=1)
            
            for key in keys:
                try:
                    session_data = await redis.hgetall(key)
                    if not session_data:
                        continue
                    
                    last_active = session_data.get("last_active")
                    if last_active:
                        last_active_dt = datetime.fromisoformat(last_active.replace("Z", "+00:00"))
                        
                        if last_active_dt < expired_threshold:
                            # 删除相关的所有键
                            parts = key.split(":")
                            if len(parts) >= 3:
                                user_id, session_id = parts[1], parts[2]
                                context_key = self._get_context_key(user_id, session_id)
                                history_key = self._get_history_key(user_id, session_id)
                                
                                await redis.delete(key, context_key, history_key)
                                cleaned_count += 1
                                
                except Exception as e:
                    logger.error(f"清理会话失败 {key}: {e}")
                    continue
            
            logger.info(f"清理了 {cleaned_count} 个过期会话")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"会话清理失败: {e}")
            return 0
    
    async def get_user_sessions(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """获取用户的所有会话"""
        try:
            redis = await self._get_redis()
            pattern = f"{self._session_prefix}:{user_id}:*"
            keys = await redis.keys(pattern)
            
            sessions = []
            for key in keys[:limit]:
                session_data = await redis.hgetall(key)
                if session_data:
                    # 反序列化数据
                    session = {}
                    for k, v in session_data.items():
                        try:
                            session[k] = json.loads(v)
                        except (json.JSONDecodeError, TypeError):
                            session[k] = v
                    sessions.append(session)
            
            # 按最后活跃时间排序
            sessions.sort(
                key=lambda x: x.get("last_active", ""), 
                reverse=True
            )
            
            return sessions
            
        except Exception as e:
            logger.error(f"获取用户会话失败: {e}")
            return []


# 全局会话管理器实例
session_manager = SessionManager()