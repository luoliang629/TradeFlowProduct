"""错误处理中间件."""

import traceback
from typing import Callable

from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.exceptions import TradeFlowException
from app.core.logging import get_logger
from app.schemas.common import ErrorResponse

logger = get_logger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """全局错误处理中间件."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求并捕获异常."""
        try:
            response = await call_next(request)
            return response
            
        except HTTPException as e:
            # FastAPI HTTPException，直接返回
            logger.warning(
                "HTTP exception occurred",
                status_code=e.status_code,
                detail=e.detail,
                url=str(request.url),
                method=request.method,
            )
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail}
            )
            
        except TradeFlowException as e:
            # 自定义业务异常
            logger.error(
                "Business exception occurred",
                error_code=e.error_code,
                message=e.message,
                details=e.details,
                url=str(request.url),
                method=request.method,
            )
            
            error_response = ErrorResponse(
                message=e.message,
                error_code=e.error_code,
                details=e.details,
            )
            
            return JSONResponse(
                status_code=e.status_code,
                content=error_response.dict(),
            )
            
        except Exception as e:
            # 未预期的系统异常
            error_id = str(id(e))
            
            logger.error(
                "Unexpected error occurred",
                error_id=error_id,
                error_type=type(e).__name__,
                error=str(e),
                url=str(request.url),
                method=request.method,
                traceback=traceback.format_exc(),
                exc_info=True,
            )
            
            # 在开发环境返回详细错误信息
            from app.config import settings
            
            if settings.is_development:
                error_response = ErrorResponse(
                    message=f"Internal server error: {str(e)}",
                    error_code="INTERNAL_ERROR",
                    details={
                        "error_id": error_id,
                        "error_type": type(e).__name__,
                        "traceback": traceback.format_exc(),
                    },
                )
            else:
                # 生产环境只返回通用错误信息
                error_response = ErrorResponse(
                    message="Internal server error occurred",
                    error_code="INTERNAL_ERROR",
                    details={"error_id": error_id},
                )
            
            return JSONResponse(
                status_code=500,
                content=error_response.dict(),
            )