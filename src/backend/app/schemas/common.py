"""通用数据模型."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ResponseModel(BaseModel):
    """通用响应模型."""
    
    success: bool = Field(default=True, description="请求是否成功")
    message: str = Field(default="OK", description="响应消息")
    data: Optional[Any] = Field(default=None, description="响应数据")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="响应时间戳")


class BaseResponse(BaseModel):
    """基础响应模型."""
    
    success: bool = Field(default=True, description="请求是否成功")
    message: str = Field(default="OK", description="响应消息")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="响应时间戳")


class ErrorResponse(BaseResponse):
    """错误响应模型."""
    
    success: bool = Field(default=False, description="请求是否成功")
    error_code: str = Field(..., description="错误代码")
    details: Optional[Dict[str, Any]] = Field(default=None, description="错误详情")


class HealthCheckResponse(BaseResponse):
    """健康检查响应模型."""
    
    status: str = Field(..., description="服务状态")
    version: str = Field(..., description="服务版本")
    uptime: float = Field(..., description="服务运行时间(秒)")
    dependencies: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict, description="依赖服务状态"
    )


class PaginationParams(BaseModel):
    """分页参数."""
    
    page: int = Field(default=1, ge=1, description="页码")
    size: int = Field(default=20, ge=1, le=100, description="每页大小")
    
    @property
    def offset(self) -> int:
        """计算偏移量."""
        return (self.page - 1) * self.size


class PaginatedResponse(BaseResponse):
    """分页响应模型."""
    
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页大小")
    pages: int = Field(..., description="总页数")
    has_next: bool = Field(..., description="是否有下一页")
    has_prev: bool = Field(..., description="是否有上一页")
    data: List[Any] = Field(default_factory=list, description="数据列表")
    
    @classmethod
    def create(
        cls,
        data: List[Any],
        total: int,
        page: int,
        size: int,
        message: str = "OK",
    ) -> "PaginatedResponse":
        """创建分页响应."""
        pages = (total + size - 1) // size if total > 0 else 0
        
        return cls(
            message=message,
            total=total,
            page=page,
            size=size,
            pages=pages,
            has_next=page < pages,
            has_prev=page > 1,
            data=data,
        )