"""认证相关数据模式."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

from app.models.user import UserStatus, CompanyStatus


class TokenResponse(BaseModel):
    """令牌响应模式."""
    
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # 秒


class UserBase(BaseModel):
    """用户基础模式."""
    
    email: EmailStr
    full_name: str
    avatar_url: Optional[str] = None
    company_name: Optional[str] = None
    company_website: Optional[str] = None
    company_description: Optional[str] = None


class UserCreate(UserBase):
    """用户创建模式."""
    
    oauth_provider: str
    oauth_id: str


class UserUpdate(BaseModel):
    """用户更新模式."""
    
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    company_name: Optional[str] = None
    company_website: Optional[str] = None
    company_description: Optional[str] = None


class UserResponse(UserBase):
    """用户响应模式."""
    
    id: int
    oauth_provider: str
    status: UserStatus
    company_status: CompanyStatus
    total_conversations: int
    total_tokens_used: int
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserProfile(UserResponse):
    """用户资料模式（包含敏感信息）."""
    
    pass


class UserPublic(BaseModel):
    """用户公开信息模式."""
    
    id: int
    full_name: str
    avatar_url: Optional[str] = None
    company_name: Optional[str] = None
    is_company_verified: bool
    
    class Config:
        from_attributes = True


class CompanyVerificationRequest(BaseModel):
    """企业认证请求模式."""
    
    company_name: str
    company_website: str
    company_description: str


class OAuthAuthorizationRequest(BaseModel):
    """OAuth授权请求模式."""
    
    provider: str
    redirect_uri: Optional[str] = None


class OAuthAuthorizationResponse(BaseModel):
    """OAuth授权响应模式."""
    
    authorization_url: str
    state: str


class OAuthCallbackRequest(BaseModel):
    """OAuth回调请求模式."""
    
    code: str
    state: str


class RefreshTokenRequest(BaseModel):
    """刷新令牌请求模式."""
    
    refresh_token: str


class LogoutRequest(BaseModel):
    """登出请求模式."""
    
    refresh_token: Optional[str] = None


class AuthErrorResponse(BaseModel):
    """认证错误响应模式."""
    
    error: str
    error_description: Optional[str] = None
    error_uri: Optional[str] = None