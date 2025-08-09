"""API v1路由集合."""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.chat import router as chat_router
from app.api.v1.products import router as products_router
from app.api.v1.files import router as files_router
from app.api.v1.business import router as business_router
from app.api.v1.payment import router as payment_router
from app.api.v1.users import router as users_router
from app.api.v1.agent import router as agent_router

# 创建v1路由器
api_router = APIRouter()

# 注册所有路由
api_router.include_router(auth_router, prefix="/auth", tags=["认证"])
api_router.include_router(users_router, prefix="/users", tags=["用户"])
api_router.include_router(chat_router, prefix="/chat", tags=["对话"])
api_router.include_router(agent_router, tags=["AI智能体"])
api_router.include_router(products_router, prefix="/products", tags=["产品"])
api_router.include_router(files_router, prefix="/files", tags=["文件"])
api_router.include_router(business_router, prefix="/business", tags=["业务"])
api_router.include_router(payment_router, prefix="/payment", tags=["支付"])

__all__ = ["api_router"]