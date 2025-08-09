"""对话管理服务."""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from bson import ObjectId

from app.core.database import get_mongodb
from app.core.logging import get_logger
from app.models.conversation import (
    Conversation,
    ConversationStats,
    ConversationStatus,
    Message,
    MessageRole,
    MessageType,
)
from app.utils.redis_client import redis_client

logger = get_logger(__name__)


class ConversationService:
    """对话服务类."""
    
    def __init__(self):
        """初始化对话服务."""
        self.collection_name = "conversations"
        self.stats_collection_name = "conversation_stats"
    
    async def create_conversation(
        self,
        user_id: int,
        session_id: str,
        title: Optional[str] = None
    ) -> Conversation:
        """创建新对话."""
        try:
            db = await get_mongodb()
            collection = db[self.collection_name]
            
            conversation = Conversation(
                user_id=user_id,
                session_id=session_id,
                title=title or f"对话 {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
            )
            
            # 插入到MongoDB
            result = await collection.insert_one(conversation.dict(by_alias=True))
            conversation.id = str(result.inserted_id)
            
            # 更新用户统计
            await self._update_user_stats(user_id, "conversation_created")
            
            # 缓存到Redis
            await self._cache_conversation(conversation)
            
            logger.info(f"Conversation created: {conversation.id}")
            return conversation
            
        except Exception as e:
            logger.error(f"Failed to create conversation: {e}")
            raise
    
    async def get_conversation(
        self,
        conversation_id: str,
        user_id: Optional[int] = None
    ) -> Optional[Conversation]:
        """获取对话."""
        try:
            # 先从缓存获取
            cached = await self._get_cached_conversation(conversation_id)
            if cached:
                return cached
            
            # 从数据库获取
            db = await get_mongodb()
            collection = db[self.collection_name]
            
            query = {"_id": ObjectId(conversation_id)}
            if user_id:
                query["user_id"] = user_id
            
            doc = await collection.find_one(query)
            if doc:
                conversation = Conversation(**doc)
                # 缓存结果
                await self._cache_conversation(conversation)
                return conversation
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get conversation: {e}")
            return None
    
    async def add_message(
        self,
        conversation_id: str,
        message: Message,
        user_id: Optional[int] = None
    ) -> bool:
        """添加消息到对话."""
        try:
            db = await get_mongodb()
            collection = db[self.collection_name]
            
            # 构建更新查询
            query = {"_id": ObjectId(conversation_id)}
            if user_id:
                query["user_id"] = user_id
            
            # 更新对话
            update = {
                "$push": {"messages": message.dict()},
                "$inc": {"total_tokens": message.tokens_used or 0},
                "$set": {"updated_at": datetime.utcnow()}
            }
            
            result = await collection.update_one(query, update)
            
            if result.modified_count > 0:
                # 清除缓存
                await self._invalidate_cache(conversation_id)
                
                # 更新统计
                if user_id:
                    await self._update_user_stats(
                        user_id,
                        "message_added",
                        tokens=message.tokens_used or 0
                    )
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to add message: {e}")
            return False
    
    async def list_conversations(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
        status: Optional[ConversationStatus] = None
    ) -> List[Conversation]:
        """列出用户的对话."""
        try:
            db = await get_mongodb()
            collection = db[self.collection_name]
            
            query = {"user_id": user_id}
            if status:
                query["status"] = status.value
            
            cursor = collection.find(query).sort(
                "updated_at", -1
            ).skip(skip).limit(limit)
            
            conversations = []
            async for doc in cursor:
                conversations.append(Conversation(**doc))
            
            return conversations
            
        except Exception as e:
            logger.error(f"Failed to list conversations: {e}")
            return []
    
    async def update_conversation_status(
        self,
        conversation_id: str,
        status: ConversationStatus,
        user_id: Optional[int] = None
    ) -> bool:
        """更新对话状态."""
        try:
            db = await get_mongodb()
            collection = db[self.collection_name]
            
            query = {"_id": ObjectId(conversation_id)}
            if user_id:
                query["user_id"] = user_id
            
            update = {
                "$set": {
                    "status": status.value,
                    "updated_at": datetime.utcnow()
                }
            }
            
            result = await collection.update_one(query, update)
            
            if result.modified_count > 0:
                await self._invalidate_cache(conversation_id)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to update conversation status: {e}")
            return False
    
    async def delete_conversation(
        self,
        conversation_id: str,
        user_id: Optional[int] = None
    ) -> bool:
        """删除对话."""
        try:
            db = await get_mongodb()
            collection = db[self.collection_name]
            
            query = {"_id": ObjectId(conversation_id)}
            if user_id:
                query["user_id"] = user_id
            
            result = await collection.delete_one(query)
            
            if result.deleted_count > 0:
                await self._invalidate_cache(conversation_id)
                
                if user_id:
                    await self._update_user_stats(user_id, "conversation_deleted")
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete conversation: {e}")
            return False
    
    async def get_user_stats(self, user_id: int) -> ConversationStats:
        """获取用户对话统计."""
        try:
            db = await get_mongodb()
            
            # 获取或创建统计文档
            stats_collection = db[self.stats_collection_name]
            stats_doc = await stats_collection.find_one({"user_id": user_id})
            
            if stats_doc:
                return ConversationStats(**stats_doc)
            
            # 如果没有统计，计算统计
            stats = await self._calculate_user_stats(user_id)
            
            # 保存统计
            await stats_collection.insert_one(stats.dict())
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get user stats: {e}")
            return ConversationStats(user_id=user_id)
    
    async def _calculate_user_stats(self, user_id: int) -> ConversationStats:
        """计算用户统计."""
        try:
            db = await get_mongodb()
            collection = db[self.collection_name]
            
            # 聚合统计
            pipeline = [
                {"$match": {"user_id": user_id}},
                {
                    "$group": {
                        "_id": None,
                        "total_conversations": {"$sum": 1},
                        "active_conversations": {
                            "$sum": {
                                "$cond": [
                                    {"$eq": ["$status", ConversationStatus.ACTIVE.value]},
                                    1,
                                    0
                                ]
                            }
                        },
                        "total_messages": {"$sum": {"$size": "$messages"}},
                        "total_tokens": {"$sum": "$total_tokens"},
                        "last_conversation_at": {"$max": "$updated_at"}
                    }
                }
            ]
            
            cursor = collection.aggregate(pipeline)
            result = await cursor.to_list(1)
            
            if result:
                data = result[0]
                stats = ConversationStats(
                    user_id=user_id,
                    total_conversations=data.get("total_conversations", 0),
                    active_conversations=data.get("active_conversations", 0),
                    total_messages=data.get("total_messages", 0),
                    total_tokens_used=data.get("total_tokens", 0),
                    last_conversation_at=data.get("last_conversation_at")
                )
                
                # 计算平均值
                if stats.total_conversations > 0:
                    stats.avg_tokens_per_conversation = (
                        stats.total_tokens_used / stats.total_conversations
                    )
                    stats.avg_messages_per_conversation = (
                        stats.total_messages / stats.total_conversations
                    )
                
                return stats
            
            return ConversationStats(user_id=user_id)
            
        except Exception as e:
            logger.error(f"Failed to calculate user stats: {e}")
            return ConversationStats(user_id=user_id)
    
    async def _update_user_stats(
        self,
        user_id: int,
        action: str,
        tokens: int = 0
    ) -> None:
        """更新用户统计."""
        try:
            db = await get_mongodb()
            stats_collection = db[self.stats_collection_name]
            
            update = {}
            
            if action == "conversation_created":
                update = {
                    "$inc": {
                        "total_conversations": 1,
                        "active_conversations": 1
                    },
                    "$set": {"last_conversation_at": datetime.utcnow()}
                }
            elif action == "conversation_deleted":
                update = {
                    "$inc": {
                        "total_conversations": -1,
                        "active_conversations": -1
                    }
                }
            elif action == "message_added":
                update = {
                    "$inc": {
                        "total_messages": 1,
                        "total_tokens_used": tokens
                    }
                }
                
                # 更新每日使用量
                today = datetime.utcnow().strftime("%Y-%m-%d")
                update["$inc"][f"daily_usage.{today}"] = tokens
                
                # 更新小时分布
                hour = datetime.utcnow().hour
                update["$inc"][f"hourly_distribution.{hour}"] = 1
            
            if update:
                await stats_collection.update_one(
                    {"user_id": user_id},
                    update,
                    upsert=True
                )
            
        except Exception as e:
            logger.error(f"Failed to update user stats: {e}")
    
    async def _cache_conversation(self, conversation: Conversation) -> None:
        """缓存对话到Redis."""
        try:
            key = f"conversation:{conversation.id}"
            value = conversation.json()
            await redis_client.setex(key, 3600, value)  # 1小时缓存
        except Exception as e:
            logger.error(f"Failed to cache conversation: {e}")
    
    async def _get_cached_conversation(
        self,
        conversation_id: str
    ) -> Optional[Conversation]:
        """从缓存获取对话."""
        try:
            key = f"conversation:{conversation_id}"
            value = await redis_client.get(key)
            
            if value:
                return Conversation.parse_raw(value)
            
            return None
        except Exception as e:
            logger.error(f"Failed to get cached conversation: {e}")
            return None
    
    async def _invalidate_cache(self, conversation_id: str) -> None:
        """清除缓存."""
        try:
            key = f"conversation:{conversation_id}"
            await redis_client.delete(key)
        except Exception as e:
            logger.error(f"Failed to invalidate cache: {e}")


# 全局对话服务实例
conversation_service = ConversationService()