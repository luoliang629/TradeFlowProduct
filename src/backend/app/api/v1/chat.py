"""对话相关API路由."""

from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.logging import get_logger
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.conversation import (
    ConversationStatus,
    Message,
    MessageRole,
    MessageType
)
from app.schemas.common import ResponseModel
from app.services.conversation import conversation_service
from app.services.sse import sse_manager
from app.services.payment import subscription_service

logger = get_logger(__name__)

router = APIRouter(prefix="/chat", tags=["对话"])


@router.post("/", response_model=ResponseModel)
async def create_conversation(
    title: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ResponseModel:
    """创建新对话."""
    try:
        # 检查订阅限额
        can_create = await subscription_service.check_usage_limit(
            db, current_user.id, "conversations"
        )
        
        if not can_create:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Conversation limit reached"
            )
        
        # 创建对话
        conversation = await conversation_service.create_conversation(
            current_user.id,
            session_id=str(current_user.id),
            title=title
        )
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create conversation"
            )
        
        # 记录使用量
        await subscription_service.record_usage(
            db, current_user.id, "conversations"
        )
        
        return ResponseModel(
            success=True,
            data=conversation.dict(),
            message="Conversation created successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/stream")
async def stream_conversation(
    request: Request,
    conversation_id: str = Query(...),
    current_user: User = Depends(get_current_user)
):
    """SSE流式对话端点."""
    try:
        # 验证对话归属
        conversation = await conversation_service.get_conversation(
            conversation_id,
            current_user.id
        )
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # 建立SSE连接
        connection = await sse_manager.connect(
            current_user.id,
            session_id=str(current_user.id),
            request=request
        )
        
        # 返回SSE响应
        return EventSourceResponse(
            sse_manager.stream_generator(connection, request),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # 禁用Nginx缓冲
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to establish SSE connection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to establish connection"
        )


@router.post("/{conversation_id}/message", response_model=ResponseModel)
async def send_message(
    conversation_id: str,
    content: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ResponseModel:
    """发送消息到对话."""
    try:
        # 验证对话归属
        conversation = await conversation_service.get_conversation(
            conversation_id,
            current_user.id
        )
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # 检查Token限额
        estimated_tokens = len(content) // 4  # 简单估算
        can_use = await subscription_service.check_usage_limit(
            db, current_user.id, "tokens", estimated_tokens
        )
        
        if not can_use:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Token limit reached"
            )
        
        # 添加用户消息
        user_message = Message(
            role=MessageRole.USER,
            content=content,
            type=MessageType.TEXT,
            tokens_used=estimated_tokens
        )
        
        success = await conversation_service.add_message(
            conversation_id,
            user_message,
            current_user.id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add message"
            )
        
        # 记录Token使用
        await subscription_service.record_usage(
            db, current_user.id, "tokens", estimated_tokens
        )
        
        # 通过SSE发送消息给用户
        await sse_manager.send_to_user(
            current_user.id,
            {
                "type": "message",
                "conversation_id": conversation_id,
                "message": user_message.dict(),
                "timestamp": datetime.utcnow().isoformat()
            },
            session_id=str(current_user.id)
        )
        
        # TODO: 这里应该调用Agent处理消息并返回响应
        # 现在只返回简单的确认
        
        return ResponseModel(
            success=True,
            data={"message_id": user_message.id},
            message="Message sent successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/history", response_model=ResponseModel)
async def get_conversation_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[ConversationStatus] = None,
    current_user: User = Depends(get_current_user)
) -> ResponseModel:
    """获取对话历史列表."""
    try:
        conversations = await conversation_service.list_conversations(
            current_user.id,
            skip=skip,
            limit=limit,
            status=status
        )
        
        return ResponseModel(
            success=True,
            data={
                "conversations": [conv.dict() for conv in conversations],
                "total": len(conversations),
                "skip": skip,
                "limit": limit
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to get conversation history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{conversation_id}", response_model=ResponseModel)
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user)
) -> ResponseModel:
    """获取对话详情."""
    try:
        conversation = await conversation_service.get_conversation(
            conversation_id,
            current_user.id
        )
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        return ResponseModel(
            success=True,
            data=conversation.dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/{conversation_id}", response_model=ResponseModel)
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user)
) -> ResponseModel:
    """删除对话."""
    try:
        success = await conversation_service.delete_conversation(
            conversation_id,
            current_user.id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        return ResponseModel(
            success=True,
            message="Conversation deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/stats/summary", response_model=ResponseModel)
async def get_conversation_stats(
    current_user: User = Depends(get_current_user)
) -> ResponseModel:
    """获取对话统计信息."""
    try:
        stats = await conversation_service.get_user_stats(current_user.id)
        
        return ResponseModel(
            success=True,
            data=stats.dict()
        )
        
    except Exception as e:
        logger.error(f"Failed to get conversation stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )