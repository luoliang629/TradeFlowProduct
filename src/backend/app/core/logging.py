"""日志配置模块."""

import logging
import sys
from contextvars import ContextVar
from typing import Any, Dict, Optional
from uuid import uuid4

import structlog
from structlog.typing import FilteringBoundLogger

from app.config import settings

# 请求ID上下文变量
request_id_context: ContextVar[Optional[str]] = ContextVar('request_id', default=None)


def get_request_id() -> str:
    """获取当前请求ID."""
    request_id = request_id_context.get()
    return request_id or str(uuid4())


def set_request_id(request_id: str) -> None:
    """设置当前请求ID."""
    request_id_context.set(request_id)


class RequestIdProcessor:
    """请求ID处理器."""
    
    def __call__(self, _: Any, __: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
        """添加请求ID到事件字典."""
        request_id = request_id_context.get()
        if request_id:
            event_dict["request_id"] = request_id
        return event_dict


def configure_logging() -> None:
    """配置结构化日志."""
    # 配置标准库日志
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL.upper()),
    )
    
    # 配置structlog
    processors = [
        structlog.contextvars.merge_contextvars,
        RequestIdProcessor(),
        structlog.processors.TimeStamper(fmt="ISO"),
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.CallsiteParameterAdder(
            parameters=[
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
            ]
        ),
    ]
    
    if settings.is_development:
        # 开发环境使用彩色输出
        processors.append(structlog.dev.ConsoleRenderer(colors=True))
    else:
        # 生产环境使用JSON格式
        processors.append(structlog.processors.JSONRenderer())
    
    structlog.configure(
        processors=processors,
        logger_factory=structlog.WriteLoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.LOG_LEVEL.upper())
        ),
        cache_logger_on_first_use=True,
    )
    
    # 静默一些第三方库的日志
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("motor").setLevel(logging.WARNING)
    

def get_logger(name: str) -> FilteringBoundLogger:
    """获取结构化日志记录器."""
    return structlog.get_logger(name)