"""对话相关模型定义."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from bson import ObjectId
from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    """消息角色枚举."""
    
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageType(str, Enum):
    """消息类型枚举."""
    
    TEXT = "text"
    FILE = "file"
    IMAGE = "image"
    ERROR = "error"


class ConversationStatus(str, Enum):
    """对话状态枚举."""
    
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Message(BaseModel):
    """消息模型."""
    
    id: str = Field(default_factory=lambda: str(ObjectId()))
    role: MessageRole
    content: str
    type: MessageType = MessageType.TEXT
    metadata: Optional[Dict[str, Any]] = None
    file_ids: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    tokens_used: Optional[int] = None
    
    class Config:
        use_enum_values = True


class Conversation(BaseModel):
    """对话模型（MongoDB文档）."""
    
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    user_id: int
    session_id: str
    title: Optional[str] = None
    messages: List[Message] = Field(default_factory=list)
    status: ConversationStatus = ConversationStatus.ACTIVE
    context: Optional[Dict[str, Any]] = None
    total_tokens: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        use_enum_values = True
        populate_by_name = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }


class ConversationStats(BaseModel):
    """对话统计模型."""
    
    user_id: int
    total_conversations: int = 0
    active_conversations: int = 0
    total_messages: int = 0
    total_tokens_used: int = 0
    avg_tokens_per_conversation: float = 0.0
    avg_messages_per_conversation: float = 0.0
    last_conversation_at: Optional[datetime] = None
    daily_usage: Dict[str, int] = Field(default_factory=dict)
    hourly_distribution: Dict[int, int] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }