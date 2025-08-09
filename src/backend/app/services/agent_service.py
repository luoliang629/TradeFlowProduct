"""
TradeFlowAgent服务 - ADK Runner封装整合版
提供Agent服务的核心功能，整合Session管理、SSE转换、错误处理等组件
"""

import asyncio
import os
import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict, Any, Optional
from pathlib import Path

from app.core.logging import get_logger
from app.config import settings
from app.services.session_manager import session_manager
from app.services.sse_converter import SSEConverter, StreamEventProcessor
from app.services.agent_error_handler import with_retry, AgentError, ErrorType
from app.services.agent_performance_optimizer import performance_optimizer

logger = get_logger(__name__)


class AgentService:
    """TradeFlowAgent服务封装类"""
    
    def __init__(self):
        self._runner = None
        self._root_agent = None
        self._initialized = False
        self._lock = asyncio.Lock()
    
    async def initialize(self) -> None:
        """初始化Agent服务"""
        if self._initialized:
            return
        
        async with self._lock:
            if self._initialized:
                return
            
            try:
                logger.info("正在初始化TradeFlowAgent服务...")
                
                # 添加TradeFlowAgent路径到Python路径
                agent_path = Path(__file__).parent.parent.parent.parent / "agent" / "TradeFlowAgent"
                if agent_path.exists():
                    sys.path.insert(0, str(agent_path))
                    logger.info(f"已添加Agent路径: {agent_path}")
                else:
                    raise FileNotFoundError(f"TradeFlowAgent路径不存在: {agent_path}")
                
                # 设置环境变量
                self._setup_environment()
                
                # 导入ADK相关模块
                from google.adk.core import Runner
                from trade_flow.main_agent import root_agent
                
                # 初始化Runner和Agent
                self._root_agent = root_agent
                self._runner = Runner()
                
                logger.info("TradeFlowAgent服务初始化成功")
                self._initialized = True
                
            except ImportError as e:
                logger.error(f"导入ADK模块失败: {e}")
                raise RuntimeError(f"ADK模块导入失败，请确保已安装google-adk: {e}")
            except Exception as e:
                logger.error(f"Agent服务初始化失败: {e}")
                raise RuntimeError(f"Agent服务初始化失败: {e}")
    
    def _setup_environment(self) -> None:
        """设置Agent运行所需的环境变量"""
        # 从后端配置映射到Agent配置
        env_mapping = {
            'MODEL': getattr(settings, 'GOOGLE_ADK_MODEL', 'gemini-2.0-flash'),
            'API_KEY': getattr(settings, 'GOOGLE_ADK_API_KEY', ''),
            'TEMPERATURE': '0.7',
            # 可以根据需要添加更多配置映射
        }
        
        for key, value in env_mapping.items():
            if value:
                os.environ[key] = str(value)
                logger.debug(f"设置环境变量: {key}=***")
    
    @with_retry(max_retries=3, timeout_seconds=30)
    async def query_agent_sync(
        self, 
        user_id: str, 
        session_id: str, 
        query: str,
        auto_create_session: bool = True
    ) -> Dict[str, Any]:
        """
        同步Agent查询 - 整合会话管理和错误处理
        
        Args:
            user_id: 用户ID
            session_id: 会话ID  
            query: 查询内容
            auto_create_session: 是否自动创建会话
            
        Returns:
            Agent响应结果
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            logger.info(f"开始同步Agent查询 - 用户: {user_id}, 会话: {session_id}")
            
            # 检查缓存响应
            context = await session_manager.get_context(user_id, session_id)
            cached_response = await performance_optimizer.get_cached_response_or_none(
                user_id, query, context
            )
            
            if cached_response:
                logger.info(f"返回缓存响应 - 用户: {user_id}")
                return {
                    "status": "success",
                    "response": cached_response["response"],
                    "user_id": user_id,
                    "session_id": session_id,
                    "metadata": {
                        "response_length": len(cached_response["response"]),
                        "cached": True,
                        "cached_at": cached_response["cached_at"],
                        "timestamp": SSEConverter._get_timestamp()
                    }
                }
            
            # 检查或创建会话
            session = await session_manager.get_session(user_id, session_id)
            if not session and auto_create_session:
                await session_manager.create_session(user_id, session_id)
                logger.info(f"自动创建会话: {session_id}")
            
            # 更新会话活跃时间
            await session_manager.update_session_activity(user_id, session_id)
            
            # 添加用户消息到历史
            await session_manager.add_message_to_history(
                user_id, session_id, "user", query
            )
            
            # 获取优化的Runner实例
            runner = await performance_optimizer.get_optimized_runner()
            
            try:
                # 构建Content对象
                from google.adk.core import Content
                content = Content(role="user", parts=[{"text": query}])
                
                # 调用Runner执行
                result = await runner.run_async(
                    agent=self._root_agent,
                    user_id=user_id,
                    contents=[content]
                )
                
            finally:
                # 归还Runner实例到池中
                await performance_optimizer.return_runner(runner)
            
            logger.info(f"Agent查询完成 - 用户: {user_id}")
            
            # 提取最终结果
            response_text = ""
            if hasattr(result, 'parts') and result.parts:
                for part in result.parts:
                    if hasattr(part, 'text'):
                        response_text += part.text
            else:
                response_text = str(result)
            
            # 缓存响应
            await performance_optimizer.cache_response_if_enabled(
                user_id, query, response_text, context
            )
            
            # Token使用监控（估算值）
            estimated_input_tokens = len(query) // 4  # 粗略估算
            estimated_output_tokens = len(response_text) // 4
            await performance_optimizer.check_token_usage(
                user_id, estimated_input_tokens, estimated_output_tokens
            )
            
            # 添加Assistant响应到历史
            await session_manager.add_message_to_history(
                user_id, session_id, "assistant", response_text
            )
            
            # 更新上下文
            await session_manager.update_context(user_id, session_id, {
                "conversation_turns": context.get("conversation_turns", 0) + 1,
                "last_query": query,
                "last_response_length": len(response_text)
            })
            
            return {
                "status": "success",
                "response": response_text,
                "user_id": user_id,
                "session_id": session_id,
                "metadata": {
                    "response_length": len(response_text),
                    "cached": False,
                    "timestamp": SSEConverter._get_timestamp()
                }
            }
            
        except Exception as e:
            logger.error(f"Agent查询失败: {e}")
            
            # 记录错误到会话历史
            await session_manager.add_message_to_history(
                user_id, session_id, "system", f"错误: {str(e)}"
            )
            
            # 抛出AgentError以触发重试机制
            raise AgentError(
                f"Agent查询失败: {str(e)}",
                error_type=ErrorType.API_ERROR,
                metadata={"user_id": user_id, "session_id": session_id}
            )
    
    async def query_agent_stream(
        self, 
        user_id: str, 
        session_id: str, 
        query: str,
        auto_create_session: bool = True
    ) -> AsyncGenerator[str, None]:
        """
        流式Agent查询 - 整合SSE转换和会话管理
        
        Args:
            user_id: 用户ID
            session_id: 会话ID
            query: 查询内容
            auto_create_session: 是否自动创建会话
            
        Yields:
            SSE格式的流式响应事件
        """
        if not self._initialized:
            await self.initialize()
        
        # 创建流事件处理器
        stream_processor = StreamEventProcessor(user_id, session_id)
        
        try:
            logger.info(f"开始流式Agent查询 - 用户: {user_id}, 会话: {session_id}")
            
            # 检查或创建会话
            session = await session_manager.get_session(user_id, session_id)
            if not session and auto_create_session:
                await session_manager.create_session(user_id, session_id)
                logger.info(f"自动创建会话: {session_id}")
            
            # 更新会话活跃时间
            await session_manager.update_session_activity(user_id, session_id)
            
            # 发送开始事件
            yield stream_processor.start_stream(query)
            
            # 添加用户消息到历史
            await session_manager.add_message_to_history(
                user_id, session_id, "user", query
            )
            
            # TODO: 这里应该实现真正的ADK流式API
            # 目前使用同步查询然后分块模拟流式效果
            try:
                # 构建Content对象
                from google.adk.core import Content
                content = Content(role="user", parts=[{"text": query}])
                
                # 调用Runner执行（同步版本）
                result = await self._runner.run_async(
                    agent=self._root_agent,
                    user_id=user_id,
                    contents=[content]
                )
                
                # 提取响应文本
                response_text = ""
                if hasattr(result, 'parts') and result.parts:
                    for part in result.parts:
                        if hasattr(part, 'text'):
                            response_text += part.text
                else:
                    response_text = str(result)
                
                # 模拟流式输出
                chunk_size = 30  # 每次输出30字符
                
                for i in range(0, len(response_text), chunk_size):
                    chunk = response_text[i:i+chunk_size]
                    
                    # 创建chunk事件并转换为SSE格式
                    chunk_event = {
                        "event": "chunk",
                        "data": {"text": chunk, "index": i // chunk_size}
                    }
                    
                    yield SSEConverter.format_sse_event(
                        SSEConverter.SSEEventType.CHUNK,
                        chunk_event["data"]
                    )
                    
                    await asyncio.sleep(0.02)  # 小延迟模拟流式效果
                
                # 添加Assistant响应到历史
                await session_manager.add_message_to_history(
                    user_id, session_id, "assistant", response_text
                )
                
                # 更新上下文
                await session_manager.update_context(user_id, session_id, {
                    "conversation_turns": (await session_manager.get_context(user_id, session_id)).get("conversation_turns", 0) + 1,
                    "last_query": query,
                    "last_response_length": len(response_text)
                })
                
                # 发送结束事件
                yield stream_processor.end_stream(
                    success=True,
                    metadata={
                        "response_length": len(response_text),
                        "chunks_sent": (len(response_text) + chunk_size - 1) // chunk_size
                    }
                )
                
            except Exception as e:
                logger.error(f"Agent执行失败: {e}")
                
                # 记录错误到会话历史
                await session_manager.add_message_to_history(
                    user_id, session_id, "system", f"错误: {str(e)}"
                )
                
                # 发送错误事件
                yield SSEConverter.create_error_event(f"Agent执行失败: {str(e)}")
                
        except Exception as e:
            logger.error(f"流式Agent查询失败: {e}")
            yield SSEConverter.create_error_event(f"流式查询失败: {str(e)}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Agent健康检查"""
        try:
            if not self._initialized:
                return {
                    "status": "not_initialized",
                    "healthy": False,
                    "message": "Agent服务未初始化"
                }
            
            # 检查核心组件
            checks = {
                "runner": self._runner is not None,
                "root_agent": self._root_agent is not None,
                "initialized": self._initialized
            }
            
            all_healthy = all(checks.values())
            
            return {
                "status": "healthy" if all_healthy else "unhealthy",
                "healthy": all_healthy,
                "checks": checks,
                "message": "所有组件正常" if all_healthy else "部分组件异常"
            }
            
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
            return {
                "status": "error",
                "healthy": False,
                "error": str(e)
            }
    
    async def cleanup(self) -> None:
        """清理资源"""
        try:
            logger.info("正在清理Agent服务资源...")
            
            # 清理Runner和Agent
            self._runner = None
            self._root_agent = None
            self._initialized = False
            
            logger.info("Agent服务资源清理完成")
            
        except Exception as e:
            logger.error(f"Agent服务资源清理失败: {e}")


# 全局Agent服务实例
agent_service = AgentService()


@asynccontextmanager
async def get_agent_service():
    """获取Agent服务实例的上下文管理器"""
    try:
        if not agent_service._initialized:
            await agent_service.initialize()
        yield agent_service
    finally:
        # 这里不清理，因为服务需要持续运行
        pass


async def initialize_agent_service():
    """初始化全局Agent服务"""
    await agent_service.initialize()


async def cleanup_agent_service():
    """清理全局Agent服务"""
    await agent_service.cleanup()