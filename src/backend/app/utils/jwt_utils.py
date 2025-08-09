"""JWT工具函数."""

import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.logging import get_logger
from app.models.user import TokenBlacklist
from app.utils.redis_client import redis_client

logger = get_logger(__name__)


class JWTManager:
    """JWT管理器."""
    
    def __init__(self):
        """初始化JWT管理器."""
        self.secret_key = settings.JWT_SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_hours = settings.ACCESS_TOKEN_EXPIRE_HOURS
        self.refresh_token_expire_days = settings.REFRESH_TOKEN_EXPIRE_DAYS
    
    def create_access_token(
        self,
        user_id: int,
        additional_claims: Optional[Dict[str, Any]] = None
    ) -> str:
        """创建访问令牌."""
        now = datetime.utcnow()
        expire = now + timedelta(hours=self.access_token_expire_hours)
        
        payload = {
            "sub": str(user_id),
            "type": "access",
            "iat": now,
            "exp": expire,
            "jti": str(uuid.uuid4()),  # JWT ID，用于黑名单管理
        }
        
        if additional_claims:
            payload.update(additional_claims)
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        logger.info("Access token created", user_id=user_id, expire=expire)
        return token
    
    def create_refresh_token(self, user_id: int) -> str:
        """创建刷新令牌."""
        now = datetime.utcnow()
        expire = now + timedelta(days=self.refresh_token_expire_days)
        
        payload = {
            "sub": str(user_id),
            "type": "refresh",
            "iat": now,
            "exp": expire,
            "jti": str(uuid.uuid4()),
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        logger.info("Refresh token created", user_id=user_id, expire=expire)
        return token
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """验证令牌."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # 检查令牌类型
            token_type = payload.get("type")
            if not token_type:
                logger.warning("Token missing type claim")
                return None
            
            # 检查过期时间
            exp = payload.get("exp")
            if not exp or datetime.utcfromtimestamp(exp) < datetime.utcnow():
                logger.warning("Token expired")
                return None
            
            return payload
            
        except JWTError as e:
            logger.warning("JWT verification failed", error=str(e))
            return None
    
    async def is_token_blacklisted(self, jti: str) -> bool:
        """检查令牌是否在黑名单中."""
        try:
            # 首先从Redis检查（更快）
            cache_key = f"blacklist:{jti}"
            if await redis_client.exists(cache_key):
                return True
            
            # 如果Redis中没有，暂时返回False
            # 实际生产中应该同时检查数据库
            return False
            
        except Exception as e:
            logger.error("Error checking token blacklist", error=str(e))
            # 出错时采用安全策略，拒绝令牌
            return True
    
    async def add_token_to_blacklist(
        self,
        db: AsyncSession,
        jti: str,
        user_id: int,
        token_type: str,
        expires_at: datetime
    ) -> None:
        """将令牌添加到黑名单."""
        try:
            # 添加到数据库
            blacklist_entry = TokenBlacklist(
                jti=jti,
                user_id=user_id,
                token_type=token_type,
                expires_at=expires_at
            )
            db.add(blacklist_entry)
            await db.commit()
            
            # 添加到Redis缓存
            cache_key = f"blacklist:{jti}"
            ttl = int((expires_at - datetime.utcnow()).total_seconds())
            if ttl > 0:
                await redis_client.set(cache_key, "1", ex=ttl)
            
            logger.info(
                "Token added to blacklist",
                jti=jti,
                user_id=user_id,
                token_type=token_type
            )
            
        except Exception as e:
            logger.error("Error adding token to blacklist", error=str(e))
            await db.rollback()
            raise
    
    async def revoke_all_user_tokens(self, db: AsyncSession, user_id: int) -> None:
        """撤销用户的所有令牌."""
        try:
            # 在实际实现中，这里应该：
            # 1. 查询用户的所有有效令牌
            # 2. 将它们添加到黑名单
            # 3. 从Redis中移除相关缓存
            
            # 简化实现：将用户标记为需要重新认证
            cache_key = f"user_tokens_revoked:{user_id}"
            await redis_client.set(cache_key, "1", ex=86400 * 30)  # 30天
            
            logger.info("All user tokens revoked", user_id=user_id)
            
        except Exception as e:
            logger.error("Error revoking user tokens", error=str(e))
            raise
    
    def extract_user_id(self, token: str) -> Optional[int]:
        """从令牌中提取用户ID."""
        payload = self.verify_token(token)
        if not payload:
            return None
        
        try:
            return int(payload.get("sub"))
        except (ValueError, TypeError):
            return None
    
    def get_token_jti(self, token: str) -> Optional[str]:
        """获取令牌的JTI."""
        payload = self.verify_token(token)
        if not payload:
            return None
        
        return payload.get("jti")
    
    def get_token_expiry(self, token: str) -> Optional[datetime]:
        """获取令牌的过期时间."""
        payload = self.verify_token(token)
        if not payload:
            return None
        
        exp = payload.get("exp")
        if exp:
            return datetime.utcfromtimestamp(exp)
        
        return None


# 全局JWT管理器实例
jwt_manager = JWTManager()