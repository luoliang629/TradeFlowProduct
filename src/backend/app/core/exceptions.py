"""自定义异常类."""

from typing import Any, Dict, Optional


class TradeFlowException(Exception):
    """TradeFlow基础异常类."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 500,
    ) -> None:
        """初始化异常."""
        self.message = message
        self.error_code = error_code or "INTERNAL_ERROR"
        self.details = details or {}
        self.status_code = status_code
        super().__init__(self.message)


class ValidationError(TradeFlowException):
    """验证错误异常."""
    
    def __init__(
        self,
        message: str = "Validation failed",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """初始化验证错误异常."""
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=details,
            status_code=400,
        )


class AuthenticationError(TradeFlowException):
    """认证错误异常."""
    
    def __init__(
        self,
        message: str = "Authentication failed",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """初始化认证错误异常."""
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            details=details,
            status_code=401,
        )


class AuthorizationError(TradeFlowException):
    """授权错误异常."""
    
    def __init__(
        self,
        message: str = "Access denied",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """初始化授权错误异常."""
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            details=details,
            status_code=403,
        )


class NotFoundError(TradeFlowException):
    """资源未找到异常."""
    
    def __init__(
        self,
        message: str = "Resource not found",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """初始化资源未找到异常."""
        super().__init__(
            message=message,
            error_code="NOT_FOUND_ERROR",
            details=details,
            status_code=404,
        )


class ConflictError(TradeFlowException):
    """冲突错误异常."""
    
    def __init__(
        self,
        message: str = "Resource conflict",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """初始化冲突错误异常."""
        super().__init__(
            message=message,
            error_code="CONFLICT_ERROR",
            details=details,
            status_code=409,
        )


class ExternalServiceError(TradeFlowException):
    """外部服务错误异常."""
    
    def __init__(
        self,
        message: str = "External service error",
        service: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """初始化外部服务错误异常."""
        details = details or {}
        if service:
            details["service"] = service
            
        super().__init__(
            message=message,
            error_code="EXTERNAL_SERVICE_ERROR",
            details=details,
            status_code=502,
        )


class DatabaseError(TradeFlowException):
    """数据库错误异常."""
    
    def __init__(
        self,
        message: str = "Database operation failed",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """初始化数据库错误异常."""
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            details=details,
            status_code=500,
        )


class RateLimitError(TradeFlowException):
    """速率限制错误异常."""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """初始化速率限制错误异常."""
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_ERROR",
            details=details,
            status_code=429,
        )