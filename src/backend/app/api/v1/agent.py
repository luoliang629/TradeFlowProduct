"""
Agent API端点 - 提供TradeFlowAgent的HTTP接口
"""

import uuid
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.core.logging import get_logger
from app.services.agent_service import agent_service
from app.services.session_manager import session_manager
from app.services.agent_performance_optimizer import performance_optimizer
from app.dependencies.auth import get_current_user
from app.schemas.auth import UserResponse

logger = get_logger(__name__)

router = APIRouter(prefix="/agent", tags=["agent"])


# 请求模型
class AgentQueryRequest(BaseModel):
    """Agent查询请求"""
    query: str = Field(..., description="查询内容", min_length=1, max_length=5000)
    session_id: Optional[str] = Field(None, description="会话ID，不提供则自动生成")
    auto_create_session: bool = Field(True, description="是否自动创建会话")


class SessionCreateRequest(BaseModel):
    """会话创建请求"""
    session_id: Optional[str] = Field(None, description="会话ID，不提供则自动生成")
    metadata: Optional[Dict[str, Any]] = Field(None, description="会话元数据")


# 响应模型
class AgentQueryResponse(BaseModel):
    """Agent查询响应"""
    status: str = Field(..., description="响应状态")
    response: str = Field(..., description="Agent响应内容")
    user_id: str = Field(..., description="用户ID")
    session_id: str = Field(..., description="会话ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="响应元数据")


class SessionResponse(BaseModel):
    """会话响应"""
    user_id: str = Field(..., description="用户ID")
    session_id: str = Field(..., description="会话ID")
    created_at: str = Field(..., description="创建时间")
    last_active: str = Field(..., description="最后活跃时间")
    message_count: int = Field(..., description="消息数量")
    status: str = Field(..., description="会话状态")
    metadata: Optional[Dict[str, Any]] = Field(None, description="会话元数据")


class HealthCheckResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(..., description="健康状态")
    healthy: bool = Field(..., description="是否健康")
    message: str = Field(..., description="状态消息")
    checks: Optional[Dict[str, Any]] = Field(None, description="检查详情")


@router.post(
    "/query",
    response_model=AgentQueryResponse,
    summary="同步Agent查询",
    description="发送查询到TradeFlowAgent并等待完整响应"
)
async def query_agent_sync(
    request: AgentQueryRequest,
    current_user: UserResponse = Depends(get_current_user)
) -> AgentQueryResponse:
    """
    同步Agent查询接口
    """
    try:
        # 生成会话ID（如果未提供）
        session_id = request.session_id or str(uuid.uuid4())
        
        logger.info(f"收到同步Agent查询 - 用户: {current_user.id}, 会话: {session_id}")
        
        # 调用Agent服务
        result = await agent_service.query_agent_sync(
            user_id=str(current_user.id),
            session_id=session_id,
            query=request.query,
            auto_create_session=request.auto_create_session
        )
        
        if result["status"] == "error":
            raise HTTPException(
                status_code=500,
                detail=f"Agent查询失败: {result.get('error', '未知错误')}"
            )
        
        return AgentQueryResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"同步Agent查询失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"内部服务错误: {str(e)}"
        )


@router.get(
    "/stream",
    summary="流式Agent查询",
    description="发送查询到TradeFlowAgent并获取流式响应"
)
async def query_agent_stream(
    query: str = Query(..., description="查询内容", min_length=1),
    session_id: Optional[str] = Query(None, description="会话ID"),
    auto_create_session: bool = Query(True, description="是否自动创建会话"),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    流式Agent查询接口 - 返回SSE格式的流式响应
    """
    try:
        # 生成会话ID（如果未提供）
        session_id = session_id or str(uuid.uuid4())
        
        logger.info(f"收到流式Agent查询 - 用户: {current_user.id}, 会话: {session_id}")
        
        # 创建流式响应生成器
        async def generate_stream():
            try:
                async for sse_event in agent_service.query_agent_stream(
                    user_id=str(current_user.id),
                    session_id=session_id,
                    query=query,
                    auto_create_session=auto_create_session
                ):
                    yield sse_event
                    
            except Exception as e:
                logger.error(f"流式响应生成失败: {e}")
                # 发送错误事件
                from app.services.sse_converter import SSEConverter
                yield SSEConverter.create_error_event(f"流式响应错误: {str(e)}")
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # 禁用nginx缓冲
            }
        )
        
    except Exception as e:
        logger.error(f"流式Agent查询失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"流式查询失败: {str(e)}"
        )


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="Agent健康检查",
    description="检查TradeFlowAgent服务的健康状态"
)
async def agent_health_check() -> HealthCheckResponse:
    """
    Agent健康检查接口
    """
    try:
        health_info = await agent_service.health_check()
        return HealthCheckResponse(**health_info)
        
    except Exception as e:
        logger.error(f"Agent健康检查失败: {e}")
        return HealthCheckResponse(
            status="error",
            healthy=False,
            message=f"健康检查失败: {str(e)}"
        )


@router.post(
    "/sessions",
    response_model=SessionResponse,
    summary="创建会话",
    description="创建新的Agent会话"
)
async def create_session(
    request: SessionCreateRequest,
    current_user: UserResponse = Depends(get_current_user)
) -> SessionResponse:
    """
    创建Agent会话接口
    """
    try:
        session_id = await session_manager.create_session(
            user_id=str(current_user.id),
            session_id=request.session_id,
            metadata=request.metadata
        )
        
        # 获取创建的会话信息
        session_info = await session_manager.get_session(
            str(current_user.id), session_id
        )
        
        if not session_info:
            raise HTTPException(
                status_code=500,
                detail="会话创建后无法获取信息"
            )
        
        return SessionResponse(
            user_id=session_info["user_id"],
            session_id=session_info["session_id"],
            created_at=session_info["created_at"],
            last_active=session_info["last_active"],
            message_count=session_info["message_count"],
            status=session_info["status"],
            metadata=session_info["metadata"]
        )
        
    except Exception as e:
        logger.error(f"创建会话失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"会话创建失败: {str(e)}"
        )


@router.get(
    "/sessions",
    summary="获取用户会话列表",
    description="获取当前用户的所有Agent会话"
)
async def get_user_sessions(
    limit: int = Query(20, description="返回数量限制", ge=1, le=100),
    current_user: UserResponse = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    获取用户会话列表接口
    """
    try:
        sessions = await session_manager.get_user_sessions(
            str(current_user.id), limit
        )
        
        return {
            "user_id": str(current_user.id),
            "total": len(sessions),
            "sessions": sessions
        }
        
    except Exception as e:
        logger.error(f"获取用户会话失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"获取会话列表失败: {str(e)}"
        )


@router.get(
    "/sessions/{session_id}",
    response_model=SessionResponse,
    summary="获取会话详情",
    description="获取特定会话的详细信息"
)
async def get_session_detail(
    session_id: str,
    current_user: UserResponse = Depends(get_current_user)
) -> SessionResponse:
    """
    获取会话详情接口
    """
    try:
        session_info = await session_manager.get_session(
            str(current_user.id), session_id
        )
        
        if not session_info:
            raise HTTPException(
                status_code=404,
                detail="会话不存在"
            )
        
        return SessionResponse(
            user_id=session_info["user_id"],
            session_id=session_info["session_id"],
            created_at=session_info["created_at"],
            last_active=session_info["last_active"],
            message_count=session_info["message_count"],
            status=session_info["status"],
            metadata=session_info["metadata"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取会话详情失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"获取会话详情失败: {str(e)}"
        )


@router.get(
    "/sessions/{session_id}/history",
    summary="获取会话历史",
    description="获取特定会话的消息历史记录"
)
async def get_session_history(
    session_id: str,
    limit: int = Query(50, description="返回数量限制", ge=1, le=200),
    current_user: UserResponse = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    获取会话历史接口
    """
    try:
        history = await session_manager.get_message_history(
            str(current_user.id), session_id, limit
        )
        
        return {
            "user_id": str(current_user.id),
            "session_id": session_id,
            "total": len(history),
            "messages": history
        }
        
    except Exception as e:
        logger.error(f"获取会话历史失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"获取会话历史失败: {str(e)}"
        )


@router.delete(
    "/sessions/{session_id}",
    summary="关闭会话",
    description="关闭指定的Agent会话"
)
async def close_session(
    session_id: str,
    current_user: UserResponse = Depends(get_current_user)
) -> Dict[str, str]:
    """
    关闭会话接口
    """
    try:
        await session_manager.close_session(
            str(current_user.id), session_id
        )
        
        return {
            "message": f"会话 {session_id} 已关闭",
            "session_id": session_id
        }
        
    except Exception as e:
        logger.error(f"关闭会话失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"关闭会话失败: {str(e)}"
        )


@router.get(
    "/performance/stats",
    summary="获取性能统计",
    description="获取Agent服务的性能统计信息"
)
async def get_performance_stats(
    current_user: UserResponse = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    获取Agent性能统计信息
    """
    try:
        stats = await performance_optimizer.get_performance_stats()
        user_usage = await performance_optimizer.token_monitor.get_user_usage(str(current_user.id))
        
        return {
            "performance": stats,
            "user_usage": user_usage,
            "timestamp": SSEConverter._get_timestamp()
        }
        
    except Exception as e:
        logger.error(f"获取性能统计失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"获取性能统计失败: {str(e)}"
        )


@router.post(
    "/maintenance/cleanup-sessions",
    summary="清理过期会话",
    description="清理过期的Agent会话（管理员功能）"
)
async def cleanup_expired_sessions(
    background_tasks: BackgroundTasks,
    current_user: UserResponse = Depends(get_current_user)
) -> Dict[str, str]:
    """
    清理过期会话接口（后台任务）
    """
    try:
        # 添加到后台任务
        background_tasks.add_task(session_manager.cleanup_expired_sessions)
        
        return {
            "message": "会话清理任务已启动",
            "status": "running"
        }
        
    except Exception as e:
        logger.error(f"启动会话清理失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"会话清理失败: {str(e)}"
        )


@router.delete(
    "/performance/cache/user",
    summary="清除用户缓存",
    description="清除当前用户的所有响应缓存"
)
async def clear_user_cache(
    current_user: UserResponse = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    清除用户缓存接口
    """
    try:
        cleared_count = await performance_optimizer.response_cache.invalidate_user_cache(
            str(current_user.id)
        )
        
        return {
            "message": f"已清除 {cleared_count} 个缓存项",
            "cleared_count": cleared_count,
            "user_id": str(current_user.id)
        }
        
    except Exception as e:
        logger.error(f"清除用户缓存失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"清除缓存失败: {str(e)}"
        )