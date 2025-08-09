"""产品管理相关模型定义."""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (
    Boolean, Column, DateTime, Enum as SQLEnum,
    Float, Integer, String, Text, JSON
)
from sqlalchemy.sql import func

from app.models.base import Base


class ProductStatus(str, Enum):
    """产品状态枚举."""
    
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class Product(Base):
    """产品模型."""
    
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 基础信息
    name = Column(String(200), nullable=False, index=True, comment="产品名称")
    sku = Column(String(100), unique=True, index=True, comment="SKU编码")
    category = Column(String(100), index=True, comment="产品分类")
    sub_category = Column(String(100), comment="子分类")
    
    # 描述信息
    description = Column(Text, comment="产品描述")
    specifications = Column(JSON, comment="产品规格")
    features = Column(JSON, comment="产品特性")
    
    # 价格信息
    price = Column(Float, comment="单价")
    currency = Column(String(10), default="USD", comment="货币")
    min_order_quantity = Column(Integer, default=1, comment="最小起订量")
    
    # 图片信息
    main_image = Column(String(500), comment="主图URL")
    images = Column(JSON, comment="产品图片列表")
    
    # 库存信息
    stock_quantity = Column(Integer, default=0, comment="库存数量")
    lead_time_days = Column(Integer, comment="交货期（天）")
    
    # 用户关联
    user_id = Column(Integer, nullable=False, index=True, comment="用户ID")
    
    # 状态
    status = Column(
        SQLEnum(ProductStatus),
        default=ProductStatus.DRAFT,
        nullable=False,
        comment="产品状态"
    )
    
    # SEO相关
    tags = Column(Text, comment="标签（逗号分隔）")
    keywords = Column(Text, comment="关键词")
    
    # 统计信息
    view_count = Column(Integer, default=0, comment="浏览次数")
    inquiry_count = Column(Integer, default=0, comment="询盘次数")
    
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
    
    def __repr__(self) -> str:
        """字符串表示."""
        return f"<Product {self.name}>"


class Buyer(Base):
    """买家信息模型."""
    
    __tablename__ = "buyers"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 基础信息
    company_name = Column(String(200), nullable=False, index=True, comment="公司名称")
    contact_name = Column(String(100), comment="联系人姓名")
    email = Column(String(255), index=True, comment="邮箱")
    phone = Column(String(50), comment="电话")
    website = Column(String(500), comment="网站")
    
    # 地址信息
    country = Column(String(100), index=True, comment="国家")
    region = Column(String(100), comment="地区/州")
    city = Column(String(100), comment="城市")
    address = Column(Text, comment="详细地址")
    
    # 业务信息
    business_type = Column(String(100), comment="业务类型")
    main_products = Column(JSON, comment="主营产品")
    annual_revenue = Column(String(50), comment="年营业额")
    employee_count = Column(String(50), comment="员工数量")
    
    # 采购信息
    purchase_categories = Column(JSON, comment="采购品类")
    purchase_frequency = Column(String(50), comment="采购频率")
    average_order_value = Column(Float, comment="平均订单价值")
    
    # 评分和标签
    quality_score = Column(Float, comment="质量评分")
    reliability_score = Column(Float, comment="可靠性评分")
    tags = Column(Text, comment="标签")
    
    # 来源信息
    source = Column(String(100), comment="信息来源")
    verified = Column(Boolean, default=False, comment="是否验证")
    
    # 用户关联
    created_by = Column(Integer, comment="创建者ID")
    
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
    
    def __repr__(self) -> str:
        """字符串表示."""
        return f"<Buyer {self.company_name}>"


class Supplier(Base):
    """供应商信息模型."""
    
    __tablename__ = "suppliers"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 基础信息
    company_name = Column(String(200), nullable=False, index=True, comment="公司名称")
    contact_name = Column(String(100), comment="联系人姓名")
    email = Column(String(255), index=True, comment="邮箱")
    phone = Column(String(50), comment="电话")
    website = Column(String(500), comment="网站")
    
    # 地址信息
    country = Column(String(100), index=True, comment="国家")
    region = Column(String(100), comment="地区/州")
    city = Column(String(100), comment="城市")
    address = Column(Text, comment="详细地址")
    
    # 业务信息
    business_type = Column(String(100), comment="业务类型")
    main_products = Column(JSON, comment="主营产品")
    production_capacity = Column(String(100), comment="生产能力")
    factory_size = Column(String(100), comment="工厂规模")
    
    # 认证信息
    certifications = Column(JSON, comment="认证列表")
    quality_control = Column(Text, comment="质量控制")
    
    # 贸易信息
    export_markets = Column(JSON, comment="出口市场")
    payment_terms = Column(JSON, comment="付款条件")
    shipping_terms = Column(JSON, comment="运输条件")
    min_order_quantity = Column(String(100), comment="最小起订量")
    
    # 评分
    quality_score = Column(Float, comment="质量评分")
    service_score = Column(Float, comment="服务评分")
    delivery_score = Column(Float, comment="交货评分")
    price_score = Column(Float, comment="价格评分")
    overall_score = Column(Float, comment="综合评分")
    
    # 验证状态
    verified = Column(Boolean, default=False, comment="是否验证")
    verification_date = Column(DateTime(timezone=True), comment="验证日期")
    
    # 用户关联
    created_by = Column(Integer, comment="创建者ID")
    
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
    
    def __repr__(self) -> str:
        """字符串表示."""
        return f"<Supplier {self.company_name}>"