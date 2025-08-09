"""OAuth认证服务."""

import httpx
from typing import Dict, Optional, Tuple
from urllib.parse import urlencode

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.core.logging import get_logger
from app.models.user import User, UserStatus
from app.utils.jwt_utils import jwt_manager

logger = get_logger(__name__)


class OAuthProvider:
    """OAuth提供商基类."""
    
    def __init__(self, provider_name: str):
        """初始化OAuth提供商."""
        self.provider_name = provider_name
    
    def get_authorization_url(self, state: str) -> str:
        """获取授权URL."""
        raise NotImplementedError
    
    async def get_access_token(self, code: str) -> Optional[str]:
        """获取访问令牌."""
        raise NotImplementedError
    
    async def get_user_info(self, access_token: str) -> Optional[Dict]:
        """获取用户信息."""
        raise NotImplementedError


class GoogleOAuthProvider(OAuthProvider):
    """Google OAuth提供商."""
    
    def __init__(self):
        """初始化Google OAuth提供商."""
        super().__init__("google")
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.redirect_uri = settings.GOOGLE_REDIRECT_URI
        
        self.auth_url = "https://accounts.google.com/o/oauth2/auth"
        self.token_url = "https://oauth2.googleapis.com/token"
        self.user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    
    def get_authorization_url(self, state: str) -> str:
        """获取Google授权URL."""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "openid email profile",
            "response_type": "code",
            "state": state,
            "access_type": "offline",
            "prompt": "consent",
        }
        
        return f"{self.auth_url}?{urlencode(params)}"
    
    async def get_access_token(self, code: str) -> Optional[str]:
        """获取Google访问令牌."""
        try:
            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": self.redirect_uri,
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(self.token_url, data=data)
                response.raise_for_status()
                
                token_data = response.json()
                return token_data.get("access_token")
                
        except Exception as e:
            logger.error("Failed to get Google access token", error=str(e))
            return None
    
    async def get_user_info(self, access_token: str) -> Optional[Dict]:
        """获取Google用户信息."""
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(self.user_info_url, headers=headers)
                response.raise_for_status()
                
                user_data = response.json()
                
                return {
                    "oauth_id": user_data.get("id"),
                    "email": user_data.get("email"),
                    "full_name": user_data.get("name"),
                    "avatar_url": user_data.get("picture"),
                }
                
        except Exception as e:
            logger.error("Failed to get Google user info", error=str(e))
            return None


class GitHubOAuthProvider(OAuthProvider):
    """GitHub OAuth提供商."""
    
    def __init__(self):
        """初始化GitHub OAuth提供商."""
        super().__init__("github")
        self.client_id = settings.GITHUB_CLIENT_ID
        self.client_secret = settings.GITHUB_CLIENT_SECRET
        self.redirect_uri = settings.GITHUB_REDIRECT_URI
        
        self.auth_url = "https://github.com/login/oauth/authorize"
        self.token_url = "https://github.com/login/oauth/access_token"
        self.user_info_url = "https://api.github.com/user"
    
    def get_authorization_url(self, state: str) -> str:
        """获取GitHub授权URL."""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "user:email",
            "state": state,
        }
        
        return f"{self.auth_url}?{urlencode(params)}"
    
    async def get_access_token(self, code: str) -> Optional[str]:
        """获取GitHub访问令牌."""
        try:
            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": code,
            }
            
            headers = {"Accept": "application/json"}
            
            async with httpx.AsyncClient() as client:
                response = await client.post(self.token_url, data=data, headers=headers)
                response.raise_for_status()
                
                token_data = response.json()
                return token_data.get("access_token")
                
        except Exception as e:
            logger.error("Failed to get GitHub access token", error=str(e))
            return None
    
    async def get_user_info(self, access_token: str) -> Optional[Dict]:
        """获取GitHub用户信息."""
        try:
            headers = {"Authorization": f"token {access_token}"}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(self.user_info_url, headers=headers)
                response.raise_for_status()
                
                user_data = response.json()
                
                return {
                    "oauth_id": str(user_data.get("id")),
                    "email": user_data.get("email"),
                    "full_name": user_data.get("name") or user_data.get("login"),
                    "avatar_url": user_data.get("avatar_url"),
                }
                
        except Exception as e:
            logger.error("Failed to get GitHub user info", error=str(e))
            return None


class OAuthService:
    """OAuth服务类."""
    
    def __init__(self):
        """初始化OAuth服务."""
        self.providers = {
            "google": GoogleOAuthProvider(),
            "github": GitHubOAuthProvider(),
        }
    
    def get_provider(self, provider_name: str) -> Optional[OAuthProvider]:
        """获取OAuth提供商."""
        return self.providers.get(provider_name)
    
    def get_authorization_url(self, provider_name: str, state: str) -> Optional[str]:
        """获取授权URL."""
        provider = self.get_provider(provider_name)
        if not provider:
            return None
        
        return provider.get_authorization_url(state)
    
    async def authenticate_user(
        self,
        db: AsyncSession,
        provider_name: str,
        code: str
    ) -> Optional[Tuple[User, str, str]]:
        """认证用户并返回用户对象和令牌."""
        try:
            provider = self.get_provider(provider_name)
            if not provider:
                logger.error("Unknown OAuth provider", provider=provider_name)
                return None
            
            # 获取访问令牌
            access_token = await provider.get_access_token(code)
            if not access_token:
                logger.error("Failed to get access token", provider=provider_name)
                return None
            
            # 获取用户信息
            user_info = await provider.get_user_info(access_token)
            if not user_info:
                logger.error("Failed to get user info", provider=provider_name)
                return None
            
            # 查找或创建用户
            user = await self._find_or_create_user(db, provider_name, user_info)
            if not user:
                logger.error("Failed to create user", provider=provider_name)
                return None
            
            # 生成JWT令牌
            jwt_access_token = jwt_manager.create_access_token(user.id)
            jwt_refresh_token = jwt_manager.create_refresh_token(user.id)
            
            # 更新最后登录时间
            from datetime import datetime
            user.last_login_at = datetime.utcnow()
            await db.commit()
            
            logger.info(
                "User authenticated successfully",
                user_id=user.id,
                provider=provider_name,
                email=user.email
            )
            
            return user, jwt_access_token, jwt_refresh_token
            
        except Exception as e:
            logger.error("OAuth authentication failed", error=str(e))
            return None
    
    async def _find_or_create_user(
        self,
        db: AsyncSession,
        provider_name: str,
        user_info: Dict
    ) -> Optional[User]:
        """查找或创建用户."""
        try:
            oauth_id = user_info.get("oauth_id")
            email = user_info.get("email")
            
            if not oauth_id or not email:
                logger.error("Missing required user info", user_info=user_info)
                return None
            
            # 先通过OAuth ID查找用户
            stmt = select(User).where(
                User.oauth_provider == provider_name,
                User.oauth_id == oauth_id
            )
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()
            
            if user:
                # 更新用户信息（防止用户在OAuth提供商处更新了信息）
                user.email = email
                user.full_name = user_info.get("full_name") or user.full_name
                user.avatar_url = user_info.get("avatar_url") or user.avatar_url
                await db.commit()
                return user
            
            # 检查是否存在相同邮箱的用户
            stmt = select(User).where(User.email == email)
            result = await db.execute(stmt)
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                logger.warning(
                    "User with email already exists but different OAuth provider",
                    email=email,
                    existing_provider=existing_user.oauth_provider,
                    new_provider=provider_name
                )
                # 这里可以选择合并账户或拒绝登录
                # 为了简单起见，这里拒绝登录
                return None
            
            # 创建新用户
            user = User(
                oauth_provider=provider_name,
                oauth_id=oauth_id,
                email=email,
                full_name=user_info.get("full_name", ""),
                avatar_url=user_info.get("avatar_url"),
                status=UserStatus.ACTIVE,
            )
            
            db.add(user)
            await db.commit()
            await db.refresh(user)
            
            logger.info("New user created", user_id=user.id, email=email, provider=provider_name)
            return user
            
        except Exception as e:
            logger.error("Failed to find or create user", error=str(e))
            await db.rollback()
            return None


# 全局OAuth服务实例
oauth_service = OAuthService()