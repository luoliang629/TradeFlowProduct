"""
Agent错误处理和重试机制
提供Agent执行过程中的异常捕获、错误处理和重试策略
"""

import asyncio
import random
from datetime import datetime
from enum import Enum
from typing import Callable, Any, Optional, Dict, Union
from functools import wraps

from app.core.logging import get_logger
from app.config import settings

logger = get_logger(__name__)


class ErrorType(str, Enum):
    """错误类型枚举"""
    TIMEOUT = "timeout"              # 超时错误
    API_ERROR = "api_error"          # API调用错误
    NETWORK_ERROR = "network_error"  # 网络错误
    AUTH_ERROR = "auth_error"        # 认证错误
    RATE_LIMIT = "rate_limit"        # 速率限制
    QUOTA_EXCEEDED = "quota_exceeded" # 配额超限
    MODEL_ERROR = "model_error"      # 模型错误
    PARSE_ERROR = "parse_error"      # 解析错误
    UNKNOWN_ERROR = "unknown_error"  # 未知错误


class RetryStrategy(str, Enum):
    """重试策略枚举"""
    EXPONENTIAL_BACKOFF = "exponential_backoff"  # 指数退避
    LINEAR_BACKOFF = "linear_backoff"            # 线性退避
    FIXED_DELAY = "fixed_delay"                  # 固定延迟
    IMMEDIATE = "immediate"                       # 立即重试
    NO_RETRY = "no_retry"                        # 不重试


class AgentError(Exception):
    """Agent错误基类"""
    
    def __init__(
        self,
        message: str,
        error_type: ErrorType = ErrorType.UNKNOWN_ERROR,
        retry_strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF,
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_type = error_type
        self.retry_strategy = retry_strategy
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow()


class AgentTimeoutError(AgentError):
    """Agent超时错误"""
    
    def __init__(self, message: str = "Agent执行超时", **kwargs):
        super().__init__(message, ErrorType.TIMEOUT, RetryStrategy.EXPONENTIAL_BACKOFF, **kwargs)


class AgentAPIError(AgentError):
    """Agent API错误"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, ErrorType.API_ERROR, RetryStrategy.EXPONENTIAL_BACKOFF, **kwargs)


class AgentNetworkError(AgentError):
    """Agent网络错误"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, ErrorType.NETWORK_ERROR, RetryStrategy.EXPONENTIAL_BACKOFF, **kwargs)


class AgentRateLimitError(AgentError):
    """Agent速率限制错误"""
    
    def __init__(self, message: str = "API调用速率限制", **kwargs):
        super().__init__(message, ErrorType.RATE_LIMIT, RetryStrategy.EXPONENTIAL_BACKOFF, **kwargs)


class AgentErrorHandler:
    """Agent错误处理器"""
    
    def __init__(
        self,
        max_retries: int = None,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        timeout_seconds: int = None
    ):
        self.max_retries = max_retries or settings.AGENT_MAX_RETRIES
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.timeout_seconds = timeout_seconds or settings.AGENT_TIMEOUT_SECONDS
        
    def classify_error(self, error: Exception) -> ErrorType:
        """
        分类错误类型
        
        Args:
            error: 原始异常
            
        Returns:
            错误类型
        """
        if isinstance(error, AgentError):
            return error.error_type
        
        error_str = str(error).lower()
        error_type = type(error).__name__.lower()
        
        # 超时错误
        if "timeout" in error_str or isinstance(error, asyncio.TimeoutError):
            return ErrorType.TIMEOUT
        
        # 网络错误
        if any(keyword in error_str for keyword in ["connection", "network", "unreachable"]):
            return ErrorType.NETWORK_ERROR
        
        # API错误
        if "api" in error_str or "http" in error_str:
            return ErrorType.API_ERROR
        
        # 认证错误
        if any(keyword in error_str for keyword in ["auth", "unauthorized", "forbidden"]):
            return ErrorType.AUTH_ERROR
        
        # 速率限制
        if any(keyword in error_str for keyword in ["rate", "limit", "quota", "throttle"]):
            return ErrorType.RATE_LIMIT
        
        # 解析错误
        if any(keyword in error_str for keyword in ["parse", "json", "decode"]):
            return ErrorType.PARSE_ERROR
        
        return ErrorType.UNKNOWN_ERROR
    
    def should_retry(self, error: Exception, attempt: int) -> bool:
        """
        判断是否应该重试
        
        Args:
            error: 异常对象
            attempt: 当前尝试次数
            
        Returns:
            是否应该重试
        """
        if attempt >= self.max_retries:
            return False
        
        error_type = self.classify_error(error)
        
        # 不可重试的错误类型
        non_retryable_errors = {
            ErrorType.AUTH_ERROR,
            ErrorType.PARSE_ERROR
        }
        
        if error_type in non_retryable_errors:
            return False
        
        # AgentError的重试策略
        if isinstance(error, AgentError):
            return error.retry_strategy != RetryStrategy.NO_RETRY
        
        return True
    
    async def calculate_delay(
        self, 
        attempt: int, 
        error: Exception,
        strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    ) -> float:
        """
        计算重试延迟
        
        Args:
            attempt: 当前尝试次数
            error: 异常对象
            strategy: 重试策略
            
        Returns:
            延迟时间（秒）
        """
        if isinstance(error, AgentError):
            strategy = error.retry_strategy
        
        if strategy == RetryStrategy.IMMEDIATE:
            return 0
        
        elif strategy == RetryStrategy.FIXED_DELAY:
            return self.base_delay
        
        elif strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = self.base_delay * attempt
            
        elif strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = self.base_delay * (2 ** attempt)
        
        else:
            delay = self.base_delay
        
        # 添加随机抖动，避免雷群效应
        jitter = random.uniform(0, 0.1) * delay
        delay += jitter
        
        # 限制最大延迟
        return min(delay, self.max_delay)
    
    def create_user_friendly_message(self, error: Exception) -> str:
        """
        创建用户友好的错误消息
        
        Args:
            error: 异常对象
            
        Returns:
            用户友好的错误消息
        """
        error_type = self.classify_error(error)
        
        message_map = {
            ErrorType.TIMEOUT: "请求处理超时，请稍后重试",
            ErrorType.API_ERROR: "服务暂时不可用，请稍后重试",
            ErrorType.NETWORK_ERROR: "网络连接异常，请检查网络后重试",
            ErrorType.AUTH_ERROR: "身份验证失败，请重新登录",
            ErrorType.RATE_LIMIT: "请求过于频繁，请稍后重试",
            ErrorType.QUOTA_EXCEEDED: "服务配额已用完，请联系管理员",
            ErrorType.MODEL_ERROR: "AI模型处理异常，请重新提问",
            ErrorType.PARSE_ERROR: "响应格式错误，请重新提问",
            ErrorType.UNKNOWN_ERROR: "系统异常，请稍后重试"
        }
        
        return message_map.get(error_type, "系统异常，请稍后重试")
    
    async def handle_error(
        self,
        error: Exception,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        处理错误并返回结构化信息
        
        Args:
            error: 异常对象
            context: 错误上下文
            
        Returns:
            结构化的错误信息
        """
        error_type = self.classify_error(error)
        user_message = self.create_user_friendly_message(error)
        
        error_info = {
            "error_type": error_type.value,
            "user_message": user_message,
            "technical_message": str(error),
            "timestamp": datetime.utcnow().isoformat(),
            "context": context or {}
        }
        
        # 记录错误日志
        logger.error(
            f"Agent错误 - 类型: {error_type.value}, 消息: {str(error)}",
            extra={
                "error_type": error_type.value,
                "context": context
            }
        )
        
        return error_info


def with_retry(
    max_retries: int = None,
    timeout_seconds: int = None,
    error_handler: AgentErrorHandler = None
):
    """
    重试装饰器
    
    Args:
        max_retries: 最大重试次数
        timeout_seconds: 超时时间
        error_handler: 错误处理器
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            handler = error_handler or AgentErrorHandler(
                max_retries=max_retries,
                timeout_seconds=timeout_seconds
            )
            
            attempt = 0
            last_error = None
            
            while attempt <= handler.max_retries:
                try:
                    # 添加超时控制
                    if handler.timeout_seconds:
                        result = await asyncio.wait_for(
                            func(*args, **kwargs),
                            timeout=handler.timeout_seconds
                        )
                    else:
                        result = await func(*args, **kwargs)
                    
                    return result
                    
                except Exception as error:
                    last_error = error
                    
                    # 检查是否应该重试
                    if not handler.should_retry(error, attempt):
                        logger.error(f"函数 {func.__name__} 执行失败，不可重试: {error}")
                        break
                    
                    if attempt < handler.max_retries:
                        delay = await handler.calculate_delay(attempt, error)
                        logger.warning(
                            f"函数 {func.__name__} 执行失败，{delay:.2f}秒后进行第{attempt + 1}次重试: {error}"
                        )
                        await asyncio.sleep(delay)
                    
                    attempt += 1
            
            # 所有重试都失败了
            error_info = await handler.handle_error(last_error)
            raise AgentError(
                f"函数 {func.__name__} 执行失败: {error_info['user_message']}",
                error_type=ErrorType(error_info['error_type']),
                metadata=error_info
            )
        
        return wrapper
    return decorator


# 全局错误处理器实例
error_handler = AgentErrorHandler()