"""SSE（Server-Sent Events）服务实现."""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Any, AsyncGenerator, Dict, Optional, Set
from collections import defaultdict

from fastapi import Request
from sse_starlette.sse import EventSourceResponse

from app.core.logging import get_logger
from app.utils.redis_client import redis_client

logger = get_logger(__name__)


class SSEConnection:
    """SSE连接管理."""
    
    def __init__(self, connection_id: str, user_id: int, session_id: str):
        """初始化SSE连接."""
        self.connection_id = connection_id
        self.user_id = user_id
        self.session_id = session_id
        self.queue: asyncio.Queue = asyncio.Queue()
        self.connected_at = datetime.utcnow()
        self.last_heartbeat = datetime.utcnow()
        self.is_active = True
    
    async def send_message(self, message: Dict[str, Any]) -> None:
        """发送消息到队列."""
        if self.is_active:
            await self.queue.put(message)
    
    async def disconnect(self) -> None:
        """断开连接."""
        self.is_active = False
        # 发送结束信号
        await self.queue.put(None)


class SSEManager:
    """SSE连接管理器."""
    
    def __init__(self):
        """初始化SSE管理器."""
        # 连接池：user_id -> Set[SSEConnection]
        self._connections: Dict[int, Set[SSEConnection]] = defaultdict(set)
        # 连接映射：connection_id -> SSEConnection
        self._connection_map: Dict[str, SSEConnection] = {}
        # 心跳任务
        self._heartbeat_task: Optional[asyncio.Task] = None
        # 标记是否已初始化
        self._initialized = False
    
    async def _start_heartbeat(self) -> None:
        """启动心跳任务."""
        if not self._initialized:
            self._initialized = True
            if not self._heartbeat_task or self._heartbeat_task.done():
                self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
    
    async def _heartbeat_loop(self) -> None:
        """心跳循环."""
        while True:
            try:
                await asyncio.sleep(30)  # 每30秒发送一次心跳
                
                # 发送心跳到所有活跃连接
                for connection in list(self._connection_map.values()):
                    if connection.is_active:
                        await connection.send_message({
                            "type": "heartbeat",
                            "timestamp": datetime.utcnow().isoformat()
                        })
                        connection.last_heartbeat = datetime.utcnow()
                    else:
                        # 清理非活跃连接
                        await self.disconnect(connection.connection_id)
                
            except Exception as e:
                logger.error(f"Heartbeat error: {e}")
    
    async def connect(
        self,
        user_id: int,
        session_id: str,
        request: Request
    ) -> SSEConnection:
        """建立SSE连接."""
        # 确保心跳任务已启动
        await self._start_heartbeat()
        
        connection_id = str(uuid.uuid4())
        connection = SSEConnection(connection_id, user_id, session_id)
        
        # 添加到连接池
        self._connections[user_id].add(connection)
        self._connection_map[connection_id] = connection
        
        # 记录到Redis（用于分布式环境）
        await self._register_connection_redis(connection_id, user_id, session_id)
        
        logger.info(
            f"SSE connection established",
            extra={
                "connection_id": connection_id,
                "user_id": user_id,
                "session_id": session_id
            }
        )
        
        # 发送连接成功消息
        await connection.send_message({
            "type": "connection",
            "status": "connected",
            "connection_id": connection_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return connection
    
    async def disconnect(self, connection_id: str) -> None:
        """断开SSE连接."""
        connection = self._connection_map.get(connection_id)
        if not connection:
            return
        
        # 从连接池移除
        if connection.user_id in self._connections:
            self._connections[connection.user_id].discard(connection)
            if not self._connections[connection.user_id]:
                del self._connections[connection.user_id]
        
        # 从映射移除
        if connection_id in self._connection_map:
            del self._connection_map[connection_id]
        
        # 断开连接
        await connection.disconnect()
        
        # 从Redis移除
        await self._unregister_connection_redis(connection_id)
        
        logger.info(
            f"SSE connection closed",
            extra={
                "connection_id": connection_id,
                "user_id": connection.user_id
            }
        )
    
    async def send_to_user(
        self,
        user_id: int,
        message: Dict[str, Any],
        session_id: Optional[str] = None
    ) -> int:
        """发送消息给用户的所有连接或特定会话."""
        connections = self._connections.get(user_id, set())
        sent_count = 0
        
        for connection in list(connections):
            if session_id and connection.session_id != session_id:
                continue
            
            if connection.is_active:
                await connection.send_message(message)
                sent_count += 1
        
        return sent_count
    
    async def broadcast(self, message: Dict[str, Any]) -> int:
        """广播消息给所有连接."""
        sent_count = 0
        
        for connections in self._connections.values():
            for connection in list(connections):
                if connection.is_active:
                    await connection.send_message(message)
                    sent_count += 1
        
        return sent_count
    
    async def stream_generator(
        self,
        connection: SSEConnection,
        request: Request
    ) -> AsyncGenerator[str, None]:
        """生成SSE事件流."""
        try:
            while connection.is_active:
                # 检查客户端是否断开
                if await request.is_disconnected():
                    break
                
                try:
                    # 从队列获取消息（超时1秒）
                    message = await asyncio.wait_for(
                        connection.queue.get(),
                        timeout=1.0
                    )
                    
                    if message is None:
                        # 收到结束信号
                        break
                    
                    # 格式化SSE消息
                    event_type = message.get("type", "message")
                    event_data = json.dumps(message, ensure_ascii=False)
                    
                    yield f"event: {event_type}\n"
                    yield f"data: {event_data}\n"
                    yield "\n"
                    
                except asyncio.TimeoutError:
                    # 超时继续循环（用于检查断开连接）
                    continue
                
        except Exception as e:
            logger.error(
                f"SSE stream error",
                extra={
                    "connection_id": connection.connection_id,
                    "error": str(e)
                }
            )
        
        finally:
            # 确保断开连接
            await self.disconnect(connection.connection_id)
    
    async def _register_connection_redis(
        self,
        connection_id: str,
        user_id: int,
        session_id: str
    ) -> None:
        """在Redis中注册连接（用于分布式环境）."""
        try:
            key = f"sse:connections:{user_id}"
            value = json.dumps({
                "connection_id": connection_id,
                "session_id": session_id,
                "connected_at": datetime.utcnow().isoformat()
            })
            
            await redis_client.hset(key, connection_id, value)
            await redis_client.expire(key, 86400)  # 24小时过期
            
        except Exception as e:
            logger.error(f"Failed to register connection in Redis: {e}")
    
    async def _unregister_connection_redis(self, connection_id: str) -> None:
        """从Redis中注销连接."""
        try:
            # 查找并删除连接
            pattern = "sse:connections:*"
            async for key in redis_client.scan_iter(match=pattern):
                await redis_client.hdel(key, connection_id)
            
        except Exception as e:
            logger.error(f"Failed to unregister connection from Redis: {e}")
    
    def get_connection_count(self, user_id: Optional[int] = None) -> int:
        """获取连接数."""
        if user_id:
            return len(self._connections.get(user_id, set()))
        
        return sum(len(conns) for conns in self._connections.values())
    
    def get_active_users(self) -> Set[int]:
        """获取活跃用户ID集合."""
        return set(self._connections.keys())


# 全局SSE管理器实例
sse_manager = SSEManager()