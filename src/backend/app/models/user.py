"""用户模型定义."""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Enum as SQLEnum, Integer, String, Text
from sqlalchemy.sql import func

from app.models.base import Base


class UserStatus(str, Enum):
    """用户状态枚举."""
    
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class CompanyStatus(str, Enum):
    """企业认证状态枚举."""
    
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NOT_APPLIED = "not_applied"


class User(Base):
    """用户模型."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # OAuth信息
    oauth_provider = Column(String(50), nullable=False, comment="OAuth提供商")
    oauth_id = Column(String(255), nullable=False, comment="OAuth用户ID")
    
    # 基本信息
    email = Column(String(255), unique=True, index=True, nullable=False, comment="邮箱")
    full_name = Column(String(100), nullable=False, comment="姓名")
    avatar_url = Column(String(500), comment="头像URL")
    
    # 状态信息
    status = Column(
        SQLEnum(UserStatus), 
        default=UserStatus.ACTIVE, 
        nullable=False, 
        comment="用户状态"
    )
    
    # 企业信息
    company_name = Column(String(200), comment="公司名称")
    company_website = Column(String(500), comment="公司网站")
    company_description = Column(Text, comment="公司描述")
    company_status = Column(
        SQLEnum(CompanyStatus),
        default=CompanyStatus.NOT_APPLIED,
        nullable=False,
        comment="企业认证状态"
    )
    
    # 使用统计
    total_conversations = Column(Integer, default=0, comment="对话总数")
    total_tokens_used = Column(Integer, default=0, comment="使用Token总数")
    
    # 时间戳
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False,
        comment="创建时间"
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="更新时间"
    )
    last_login_at = Column(DateTime(timezone=True), comment="最后登录时间")
    
    def __repr__(self) -> str:
        """字符串表示."""
        return f"<User {self.email}>"
    
    @property
    def is_active(self) -> bool:
        """是否为活跃用户."""
        return self.status == UserStatus.ACTIVE
    
    @property
    def is_company_verified(self) -> bool:
        """是否通过企业认证."""
        return self.company_status == CompanyStatus.APPROVED


class TokenBlacklist(Base):
    """Token黑名单模型."""
    
    __tablename__ = "token_blacklist"
    
    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String(36), unique=True, index=True, nullable=False, comment="JWT ID")
    user_id = Column(Integer, nullable=False, comment="用户ID")
    token_type = Column(String(20), nullable=False, comment="Token类型")
    expires_at = Column(DateTime(timezone=True), nullable=False, comment="过期时间")
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="创建时间"
    )
    
    def __repr__(self) -> str:
        """字符串表示."""
        return f"<TokenBlacklist {self.jti}>"