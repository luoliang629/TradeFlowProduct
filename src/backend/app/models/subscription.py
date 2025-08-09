"""订阅和支付相关模型定义."""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (
    Boolean, Column, DateTime, Enum as SQLEnum,
    Float, Integer, String, Text, JSON, ForeignKey
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.models.base import Base


class PlanType(str, Enum):
    """套餐类型枚举."""
    
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, Enum):
    """订阅状态枚举."""
    
    TRIAL = "trial"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    EXPIRED = "expired"


class PaymentStatus(str, Enum):
    """支付状态枚举."""
    
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"


class Plan(Base):
    """套餐计划模型."""
    
    __tablename__ = "plans"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 基础信息
    name = Column(String(100), unique=True, nullable=False, comment="套餐名称")
    type = Column(
        SQLEnum(PlanType),
        unique=True,
        nullable=False,
        comment="套餐类型"
    )
    description = Column(Text, comment="套餐描述")
    
    # 价格信息
    monthly_price = Column(Float, nullable=False, comment="月费")
    yearly_price = Column(Float, nullable=False, comment="年费")
    currency = Column(String(10), default="USD", comment="货币")
    
    # 配额限制
    monthly_tokens = Column(Integer, nullable=False, comment="每月Token额度")
    max_conversations = Column(Integer, comment="最大对话数")
    max_file_size_mb = Column(Integer, comment="最大文件大小(MB)")
    max_files_per_month = Column(Integer, comment="每月最大文件数")
    
    # 功能权限
    features = Column(JSON, comment="功能列表")
    has_api_access = Column(Boolean, default=False, comment="API访问权限")
    has_priority_support = Column(Boolean, default=False, comment="优先支持")
    has_custom_model = Column(Boolean, default=False, comment="自定义模型")
    
    # Stripe相关
    stripe_product_id = Column(String(100), comment="Stripe产品ID")
    stripe_monthly_price_id = Column(String(100), comment="Stripe月费价格ID")
    stripe_yearly_price_id = Column(String(100), comment="Stripe年费价格ID")
    
    # 状态
    is_active = Column(Boolean, default=True, comment="是否可用")
    is_popular = Column(Boolean, default=False, comment="是否热门")
    
    # 时间戳
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    def __repr__(self) -> str:
        """字符串表示."""
        return f"<Plan {self.name}>"


class Subscription(Base):
    """用户订阅模型."""
    
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 用户和套餐关联
    user_id = Column(Integer, nullable=False, index=True, comment="用户ID")
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False, comment="套餐ID")
    
    # 订阅信息
    status = Column(
        SQLEnum(SubscriptionStatus),
        default=SubscriptionStatus.TRIAL,
        nullable=False,
        comment="订阅状态"
    )
    billing_cycle = Column(String(20), default="monthly", comment="计费周期")
    
    # 时间信息
    trial_ends_at = Column(DateTime(timezone=True), comment="试用结束时间")
    current_period_start = Column(DateTime(timezone=True), comment="当前周期开始")
    current_period_end = Column(DateTime(timezone=True), comment="当前周期结束")
    canceled_at = Column(DateTime(timezone=True), comment="取消时间")
    ended_at = Column(DateTime(timezone=True), comment="结束时间")
    
    # Stripe相关
    stripe_subscription_id = Column(String(100), unique=True, comment="Stripe订阅ID")
    stripe_customer_id = Column(String(100), comment="Stripe客户ID")
    
    # 使用情况
    tokens_used = Column(Integer, default=0, comment="已使用Token数")
    conversations_count = Column(Integer, default=0, comment="对话数量")
    files_uploaded = Column(Integer, default=0, comment="上传文件数")
    
    # 时间戳
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # 关系
    plan = relationship("Plan", backref="subscriptions")
    
    def __repr__(self) -> str:
        """字符串表示."""
        return f"<Subscription user={self.user_id} plan={self.plan_id}>"
    
    @property
    def is_active(self) -> bool:
        """是否为活跃订阅."""
        return self.status in [SubscriptionStatus.TRIAL, SubscriptionStatus.ACTIVE]
    
    @property
    def is_expired(self) -> bool:
        """是否已过期."""
        if not self.current_period_end:
            return False
        return datetime.utcnow() > self.current_period_end


class Payment(Base):
    """支付记录模型."""
    
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 关联信息
    user_id = Column(Integer, nullable=False, index=True, comment="用户ID")
    subscription_id = Column(
        Integer,
        ForeignKey("subscriptions.id"),
        comment="订阅ID"
    )
    
    # 支付信息
    amount = Column(Float, nullable=False, comment="金额")
    currency = Column(String(10), default="USD", comment="货币")
    status = Column(
        SQLEnum(PaymentStatus),
        default=PaymentStatus.PENDING,
        nullable=False,
        comment="支付状态"
    )
    
    # Stripe相关
    stripe_payment_intent_id = Column(String(100), unique=True, comment="Stripe支付意图ID")
    stripe_invoice_id = Column(String(100), comment="Stripe发票ID")
    stripe_charge_id = Column(String(100), comment="Stripe收费ID")
    
    # 支付方式
    payment_method = Column(String(50), comment="支付方式")
    card_last4 = Column(String(4), comment="卡号后4位")
    card_brand = Column(String(20), comment="卡品牌")
    
    # 描述信息
    description = Column(Text, comment="支付描述")
    receipt_url = Column(String(500), comment="收据URL")
    
    # 退款信息
    refund_amount = Column(Float, comment="退款金额")
    refund_reason = Column(Text, comment="退款原因")
    refunded_at = Column(DateTime(timezone=True), comment="退款时间")
    
    # 时间戳
    paid_at = Column(DateTime(timezone=True), comment="支付时间")
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # 关系
    subscription = relationship("Subscription", backref="payments")
    
    def __repr__(self) -> str:
        """字符串表示."""
        return f"<Payment {self.stripe_payment_intent_id}>"


class UsageRecord(Base):
    """使用记录模型."""
    
    __tablename__ = "usage_records"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 关联信息
    user_id = Column(Integer, nullable=False, index=True, comment="用户ID")
    subscription_id = Column(
        Integer,
        ForeignKey("subscriptions.id"),
        comment="订阅ID"
    )
    
    # 使用类型
    usage_type = Column(String(50), nullable=False, comment="使用类型")
    
    # 使用量
    tokens_used = Column(Integer, default=0, comment="Token使用量")
    conversations_created = Column(Integer, default=0, comment="创建对话数")
    files_uploaded = Column(Integer, default=0, comment="上传文件数")
    
    # 时间信息
    period_start = Column(DateTime(timezone=True), comment="周期开始")
    period_end = Column(DateTime(timezone=True), comment="周期结束")
    
    # 元数据
    metadata = Column(JSON, comment="元数据")
    
    # 时间戳
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    # 关系
    subscription = relationship("Subscription", backref="usage_records")
    
    def __repr__(self) -> str:
        """字符串表示."""
        return f"<UsageRecord user={self.user_id} type={self.usage_type}>"