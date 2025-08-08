"""依赖注入模块."""

from typing import AsyncGenerator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from motor.motor_asyncio import AsyncIOMotorDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db, get_mongodb
from app.utils.minio_client import get_minio_client, MinIOClient
from app.utils.redis_client import get_redis_client, get_redis_manager, RedisClient
from app.core.logging import get_logger
import redis.asyncio as redis

logger = get_logger(__name__)
security = HTTPBearer(auto_error=False)


# 数据库依赖
async def get_database() -> AsyncGenerator[AsyncSession, None]:
    """获取PostgreSQL数据库会话依赖."""
    async for session in get_db():
        yield session


async def get_mongo_database() -> AsyncIOMotorDatabase:
    """获取MongoDB数据库依赖."""
    return await get_mongodb()


async def get_redis() -> redis.Redis:
    """获取Redis客户端依赖."""
    return await get_redis_client()


async def get_redis_manager_dep() -> RedisClient:
    """获取Redis管理器依赖."""
    return await get_redis_manager()


def get_minio() -> MinIOClient:
    """获取MinIO客户端依赖."""
    return get_minio_client()


# 认证依赖
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[dict]:
    """获取当前用户（可选）."""
    if not credentials:
        return None
    
    # TODO: 实现JWT token验证逻辑
    # 这里暂时返回None，后续实现用户认证时再完善
    try:
        # 验证token的逻辑将在用户认证模块中实现
        # token = credentials.credentials
        # user = await verify_token(token)
        # return user
        return None
    except Exception as e:
        logger.warning("Token verification failed", error=str(e))
        return None


async def get_current_user(
    current_user: Optional[dict] = Depends(get_current_user_optional)
) -> dict:
    """获取当前用户（必需）."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


async def get_admin_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """获取管理员用户."""
    if not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


# 通用依赖
class CommonQueryParams:
    """通用查询参数."""
    
    def __init__(
        self,
        page: int = 1,
        size: int = 20,
        sort: Optional[str] = None,
        order: str = "asc",
    ):
        self.page = max(1, page)
        self.size = min(100, max(1, size))  # 限制每页最多100条
        self.sort = sort
        self.order = order.lower() if order.lower() in ["asc", "desc"] else "asc"
    
    @property
    def offset(self) -> int:
        """计算偏移量."""
        return (self.page - 1) * self.size
    
    @property
    def limit(self) -> int:
        """获取限制数量."""
        return self.size