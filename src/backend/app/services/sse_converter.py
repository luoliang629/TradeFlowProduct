"""
SSE事件转换器 - 将ADK事件转换为标准SSE格式
"""

import json
from typing import Dict, Any, Optional
from enum import Enum

from app.core.logging import get_logger

logger = get_logger(__name__)


class SSEEventType(str, Enum):
    """SSE事件类型枚举"""
    START = "start"           # 对话开始
    THINKING = "thinking"     # Agent思考中
    CHUNK = "chunk"          # 文本块
    TOOL_USE = "tool_use"    # 工具调用
    TOOL_RESULT = "tool_result"  # 工具结果
    MESSAGE = "message"      # 完整消息
    ERROR = "error"          # 错误事件
    DONE = "done"           # 完成事件


class SSEConverter:
    """SSE事件转换器"""
    
    @staticmethod
    def format_sse_event(
        event_type: SSEEventType,
        data: Dict[str, Any],
        event_id: Optional[str] = None
    ) -> str:
        """
        格式化SSE事件
        
        Args:
            event_type: 事件类型
            data: 事件数据
            event_id: 事件ID（可选）
            
        Returns:
            格式化的SSE事件字符串
        """
        try:
            # 构建SSE事件
            sse_lines = []
            
            if event_id:
                sse_lines.append(f"id: {event_id}")
            
            sse_lines.append(f"event: {event_type.value}")
            sse_lines.append(f"data: {json.dumps(data, ensure_ascii=False)}")
            sse_lines.append("")  # 空行表示事件结束
            
            return "\n".join(sse_lines) + "\n"
            
        except Exception as e:
            logger.error(f"SSE事件格式化失败: {e}")
            error_data = {"error": f"SSE格式化错误: {str(e)}"}
            return f"event: error\ndata: {json.dumps(error_data)}\n\n"
    
    @staticmethod
    def convert_adk_event(adk_event: Any) -> Dict[str, Any]:
        """
        转换ADK事件为SSE事件数据
        
        Args:
            adk_event: ADK事件对象
            
        Returns:
            转换后的事件数据
        """
        try:
            # 检查事件类型和内容
            event_type = getattr(adk_event, 'type', None)
            
            if not event_type:
                # 尝试从类名推断事件类型
                event_type = type(adk_event).__name__.lower()
            
            # 根据不同的ADK事件类型进行转换
            if event_type in ['thinking', 'thought']:
                return {
                    "sse_type": SSEEventType.THINKING,
                    "data": {
                        "content": getattr(adk_event, 'content', str(adk_event)),
                        "timestamp": SSEConverter._get_timestamp()
                    }
                }
            
            elif event_type in ['chunk', 'text_chunk']:
                return {
                    "sse_type": SSEEventType.CHUNK,
                    "data": {
                        "text": getattr(adk_event, 'text', str(adk_event)),
                        "timestamp": SSEConverter._get_timestamp()
                    }
                }
            
            elif event_type in ['tool_use', 'tool_call']:
                return {
                    "sse_type": SSEEventType.TOOL_USE,
                    "data": {
                        "tool_name": getattr(adk_event, 'tool_name', 'unknown'),
                        "parameters": getattr(adk_event, 'parameters', {}),
                        "timestamp": SSEConverter._get_timestamp()
                    }
                }
            
            elif event_type in ['tool_result', 'tool_response']:
                return {
                    "sse_type": SSEEventType.TOOL_RESULT,
                    "data": {
                        "tool_name": getattr(adk_event, 'tool_name', 'unknown'),
                        "result": getattr(adk_event, 'result', ''),
                        "success": getattr(adk_event, 'success', True),
                        "timestamp": SSEConverter._get_timestamp()
                    }
                }
            
            elif event_type in ['message', 'final']:
                return {
                    "sse_type": SSEEventType.MESSAGE,
                    "data": {
                        "content": getattr(adk_event, 'content', str(adk_event)),
                        "final": True,
                        "timestamp": SSEConverter._get_timestamp()
                    }
                }
            
            else:
                # 未知事件类型，作为普通消息处理
                logger.warning(f"未知的ADK事件类型: {event_type}")
                return {
                    "sse_type": SSEEventType.CHUNK,
                    "data": {
                        "text": str(adk_event),
                        "raw_type": event_type,
                        "timestamp": SSEConverter._get_timestamp()
                    }
                }
                
        except Exception as e:
            logger.error(f"ADK事件转换失败: {e}")
            return {
                "sse_type": SSEEventType.ERROR,
                "data": {
                    "error": f"事件转换错误: {str(e)}",
                    "timestamp": SSEConverter._get_timestamp()
                }
            }
    
    @staticmethod
    def create_start_event(user_id: str, session_id: str, query: str) -> str:
        """创建对话开始事件"""
        data = {
            "user_id": user_id,
            "session_id": session_id,
            "query": query,
            "timestamp": SSEConverter._get_timestamp()
        }
        return SSEConverter.format_sse_event(SSEEventType.START, data)
    
    @staticmethod
    def create_done_event(
        success: bool = True, 
        message: str = "对话完成",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """创建完成事件"""
        data = {
            "success": success,
            "message": message,
            "timestamp": SSEConverter._get_timestamp()
        }
        
        if metadata:
            data.update(metadata)
        
        return SSEConverter.format_sse_event(SSEEventType.DONE, data)
    
    @staticmethod
    def create_error_event(error_message: str, error_code: Optional[str] = None) -> str:
        """创建错误事件"""
        data = {
            "error": error_message,
            "timestamp": SSEConverter._get_timestamp()
        }
        
        if error_code:
            data["error_code"] = error_code
        
        return SSEConverter.format_sse_event(SSEEventType.ERROR, data)
    
    @staticmethod
    def create_heartbeat_event() -> str:
        """创建心跳事件"""
        data = {
            "type": "heartbeat",
            "timestamp": SSEConverter._get_timestamp()
        }
        return f"data: {json.dumps(data)}\n\n"
    
    @staticmethod
    def _get_timestamp() -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"


class StreamEventProcessor:
    """流事件处理器"""
    
    def __init__(self, user_id: str, session_id: str):
        self.user_id = user_id
        self.session_id = session_id
        self.event_count = 0
        self.converter = SSEConverter()
    
    def process_event(self, adk_event: Any) -> str:
        """
        处理单个ADK事件并转换为SSE格式
        
        Args:
            adk_event: ADK事件对象
            
        Returns:
            SSE格式的事件字符串
        """
        self.event_count += 1
        event_id = f"{self.session_id}_{self.event_count}"
        
        try:
            # 转换ADK事件
            converted = self.converter.convert_adk_event(adk_event)
            
            # 格式化为SSE事件
            return self.converter.format_sse_event(
                event_type=converted["sse_type"],
                data=converted["data"],
                event_id=event_id
            )
            
        except Exception as e:
            logger.error(f"事件处理失败: {e}")
            return self.converter.create_error_event(f"事件处理错误: {str(e)}")
    
    def start_stream(self, query: str) -> str:
        """开始流式传输"""
        return self.converter.create_start_event(self.user_id, self.session_id, query)
    
    def end_stream(self, success: bool = True, metadata: Optional[Dict[str, Any]] = None) -> str:
        """结束流式传输"""
        final_metadata = {
            "total_events": self.event_count,
            "user_id": self.user_id,
            "session_id": self.session_id
        }
        
        if metadata:
            final_metadata.update(metadata)
        
        return self.converter.create_done_event(
            success=success,
            message="流式对话完成",
            metadata=final_metadata
        )