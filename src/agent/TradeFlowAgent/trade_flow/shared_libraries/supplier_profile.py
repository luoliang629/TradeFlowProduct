"""
供应商档案数据结构
企业信息的标准化数据模型，支持多源数据整合和结构化管理
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum


class VerificationStatus(Enum):
    """验证状态枚举"""
    VERIFIED = "verified"
    PENDING = "pending"
    UNVERIFIED = "unverified"
    FAILED = "failed"


class DataSource(Enum):
    """数据源枚举"""
    ALIBABA = "alibaba"
    MADE_IN_CHINA = "made-in-china"
    GLOBAL_SOURCES = "global-sources"
    COMPANY_WEBSITE = "company-website"
    B2B_PLATFORM = "b2b-platform"
    MANUAL_INPUT = "manual-input"
    TENDATA = "tendata"


class CompanyType(Enum):
    """企业类型枚举"""
    MANUFACTURER = "manufacturer"
    TRADING_COMPANY = "trading-company"
    FACTORY = "factory"
    WHOLESALER = "wholesaler"
    DISTRIBUTOR = "distributor"
    AGENT = "agent"
    BRAND_OWNER = "brand-owner"


@dataclass
class ContactInfo:
    """联系信息结构"""
    contact_person: Optional[str] = None  # "张总（销售总监）"
    title: Optional[str] = None  # "销售总监"
    phone: Optional[str] = None  # "138-0571-xxxx"
    mobile: Optional[str] = None  # "手机号码"
    email: Optional[str] = None  # "zhang@company.com"
    wechat: Optional[str] = None  # "微信号或二维码"
    whatsapp: Optional[str] = None  # "WhatsApp号码"
    skype: Optional[str] = None  # "Skype账号"
    qq: Optional[str] = None  # "QQ号码"
    verified: bool = False  # 联系信息是否已验证
    confidence_score: float = 0.0  # 置信度评分 (0-1)
    last_verified: Optional[datetime] = None


@dataclass
class AddressInfo:
    """地址信息结构"""
    company_address: Optional[str] = None  # "浙江杭州市西湖区文三路xxx号"
    factory_address: Optional[str] = None  # "工厂地址（如果不同）"
    city: Optional[str] = None  # "杭州"
    province: Optional[str] = None  # "浙江"
    country: Optional[str] = None  # "中国"
    postal_code: Optional[str] = None  # "310000"
    coordinates: Optional[Dict[str, float]] = None  # {"lat": 30.0, "lng": 120.0}


@dataclass
class BusinessInfo:
    """业务信息结构"""
    main_products: List[str] = field(default_factory=list)  # ["真丝围巾", "丝绸面料", "床上用品"]
    product_categories: List[str] = field(default_factory=list)  # ["纺织品", "家居用品"]
    keywords: List[str] = field(default_factory=list)  # ["丝绸", "真丝", "围巾"]
    moq: Optional[str] = None  # "500件起订"
    moq_value: Optional[int] = None  # 500 (数字形式)
    moq_unit: Optional[str] = None  # "件"
    lead_time: Optional[str] = None  # "15-20天"
    lead_time_days: Optional[int] = None  # 20 (最大天数)
    payment_terms: List[str] = field(default_factory=list)  # ["T/T", "L/C", "PayPal"]
    shipping_methods: List[str] = field(default_factory=list)  # ["海运", "空运", "快递"]
    sample_policy: Optional[str] = None  # "免费样品，运费到付"
    customization: bool = False  # 是否支持定制
    oem_odm: bool = False  # 是否支持OEM/ODM


@dataclass
class QualificationInfo:
    """资质认证信息"""
    certifications: List[str] = field(default_factory=list)  # ["ISO9001", "OEKO-TEX", "BSCI"]
    export_licenses: List[str] = field(default_factory=list)  # 出口资质
    patents: List[str] = field(default_factory=list)  # 专利信息
    awards: List[str] = field(default_factory=list)  # 获得奖项
    quality_control: Optional[str] = None  # 质量控制体系描述


@dataclass
class CompanyScale:
    """企业规模信息"""
    establishment_year: Optional[int] = None  # 成立年份
    employee_count: Optional[str] = None  # "50-100人"
    employee_count_min: Optional[int] = None  # 50
    employee_count_max: Optional[int] = None  # 100
    annual_revenue: Optional[str] = None  # "1000万-5000万"
    annual_revenue_usd: Optional[int] = None  # 年收入（美元）
    export_percentage: Optional[str] = None  # "出口占比60%"
    export_percentage_value: Optional[float] = None  # 0.6
    main_markets: List[str] = field(default_factory=list)  # ["美国", "欧盟", "东南亚"]
    factory_size: Optional[str] = None  # "工厂面积10000平方米"
    production_capacity: Optional[str] = None  # "年产能100万件"


@dataclass
class QualityScores:
    """质量评分信息"""
    overall_score: float = 0.0  # 综合评分 (0-10)
    trade_capacity_score: float = 0.0  # 贸易能力评分 (0-10)
    quality_reputation_score: float = 0.0  # 质量信誉评分 (0-10)
    market_performance_score: float = 0.0  # 市场表现评分 (0-10)
    risk_control_score: float = 0.0  # 风险控制评分 (0-10)
    matching_score: float = 0.0  # 匹配度评分 (0-10)
    
    # 评分依据
    scoring_basis: Dict[str, Any] = field(default_factory=dict)
    last_scored: Optional[datetime] = None


@dataclass
class OnlinePresence:
    """在线展示信息"""
    website: Optional[str] = None  # "www.company.com"
    alibaba_url: Optional[str] = None  # 阿里巴巴店铺链接
    made_in_china_url: Optional[str] = None  # Made-in-China链接
    social_media: Dict[str, str] = field(default_factory=dict)  # {"linkedin": "url", "facebook": "url"}
    company_video: Optional[str] = None  # 企业视频链接
    product_gallery: List[str] = field(default_factory=list)  # 产品图片链接


@dataclass
class TradeHistory:
    """贸易历史信息"""
    export_countries: List[str] = field(default_factory=list)  # 出口国家列表
    import_countries: List[str] = field(default_factory=list)  # 进口国家列表
    trade_volume_usd: Optional[int] = None  # 年贸易额（美元）
    major_customers: List[str] = field(default_factory=list)  # 主要客户
    trade_frequency: Optional[str] = None  # 贸易频率
    customs_data: Dict[str, Any] = field(default_factory=dict)  # 海关数据


@dataclass
class MetaData:
    """元数据信息"""
    data_source: DataSource = DataSource.MANUAL_INPUT
    source_url: Optional[str] = None  # 数据来源URL
    crawl_time: Optional[datetime] = None  # 抓取时间
    last_updated: datetime = field(default_factory=datetime.now)
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED
    confidence_level: float = 0.0  # 整体数据置信度 (0-1)
    data_completeness: float = 0.0  # 数据完整度 (0-1)
    notes: Optional[str] = None  # 备注信息


@dataclass
class SupplierProfile:
    """
    供应商档案主结构
    整合所有供应商相关信息的核心数据模型
    """
    # 基本标识信息
    company_name: str  # "杭州丝绸有限公司" (必填)
    english_name: Optional[str] = None  # "Hangzhou Silk Co., Ltd."
    company_id: Optional[str] = None  # 内部唯一标识
    unified_social_credit_code: Optional[str] = None  # 统一社会信用代码
    registration_number: Optional[str] = None  # 工商注册号
    company_type: Optional[CompanyType] = None
    
    # 组合信息结构
    contact_info: ContactInfo = field(default_factory=ContactInfo)
    address_info: AddressInfo = field(default_factory=AddressInfo)
    business_info: BusinessInfo = field(default_factory=BusinessInfo)
    qualification_info: QualificationInfo = field(default_factory=QualificationInfo)
    company_scale: CompanyScale = field(default_factory=CompanyScale)
    quality_scores: QualityScores = field(default_factory=QualityScores)
    online_presence: OnlinePresence = field(default_factory=OnlinePresence)
    trade_history: TradeHistory = field(default_factory=TradeHistory)
    meta_data: MetaData = field(default_factory=MetaData)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        def convert_dataclass(obj):
            if hasattr(obj, '__dict__'):
                result = {}
                for key, value in obj.__dict__.items():
                    if isinstance(value, datetime):
                        result[key] = value.isoformat() if value else None
                    elif isinstance(value, Enum):
                        result[key] = value.value
                    elif hasattr(value, '__dict__'):
                        result[key] = convert_dataclass(value)
                    elif isinstance(value, list):
                        result[key] = [convert_dataclass(item) if hasattr(item, '__dict__') else item for item in value]
                    elif isinstance(value, dict):
                        result[key] = {k: convert_dataclass(v) if hasattr(v, '__dict__') else v for k, v in value.items()}
                    else:
                        result[key] = value
                return result
            return obj
        
        return convert_dataclass(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SupplierProfile':
        """从字典创建实例"""
        # 这里可以实现复杂的反序列化逻辑
        # 暂时简化实现
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
    
    def calculate_completeness(self) -> float:
        """计算数据完整度"""
        total_fields = 0
        filled_fields = 0
        
        def check_dataclass(obj, prefix=""):
            nonlocal total_fields, filled_fields
            for field_name, field_type in obj.__dataclass_fields__.items():
                total_fields += 1
                value = getattr(obj, field_name)
                if value is not None:
                    if isinstance(value, str) and value.strip():
                        filled_fields += 1
                    elif isinstance(value, (int, float)) and value > 0:
                        filled_fields += 1
                    elif isinstance(value, list) and len(value) > 0:
                        filled_fields += 1
                    elif isinstance(value, dict) and len(value) > 0:
                        filled_fields += 1
                    elif hasattr(value, '__dataclass_fields__'):
                        # 递归检查嵌套的dataclass
                        check_dataclass(value, f"{prefix}{field_name}.")
                        total_fields -= 1  # 不重复计算父级字段
        
        check_dataclass(self)
        return filled_fields / total_fields if total_fields > 0 else 0.0
    
    def get_display_summary(self) -> str:
        """获取用于显示的企业摘要信息"""
        summary_parts = []
        
        # 企业名称和评分
        score_text = f"(评分: {self.quality_scores.overall_score:.1f}/10)" if self.quality_scores.overall_score > 0 else ""
        summary_parts.append(f"🏆 {self.company_name} {score_text}")
        
        # 地址信息
        if self.address_info.company_address:
            summary_parts.append(f"📍 地址: {self.address_info.company_address}")
        
        # 联系信息
        contact_parts = []
        if self.contact_info.contact_person:
            contact_parts.append(f"👤 {self.contact_info.contact_person}")
        if self.contact_info.phone:
            contact_parts.append(f"📞 {self.contact_info.phone}")
        if self.contact_info.email:
            contact_parts.append(f"📧 {self.contact_info.email}")
        
        if contact_parts:
            summary_parts.append(" | ".join(contact_parts))
        
        # 网站信息
        if self.online_presence.website:
            summary_parts.append(f"🌐 网站: {self.online_presence.website}")
        
        # 主营产品
        if self.business_info.main_products:
            products = ", ".join(self.business_info.main_products[:3])  # 最多显示3个产品
            summary_parts.append(f"💼 主营: {products}")
        
        # 业务信息
        business_parts = []
        if self.business_info.moq:
            business_parts.append(f"📦 起订量: {self.business_info.moq}")
        if self.business_info.lead_time:
            business_parts.append(f"⏰ 交期: {self.business_info.lead_time}")
        
        if business_parts:
            summary_parts.append(" | ".join(business_parts))
        
        # 认证信息
        if self.qualification_info.certifications:
            certs = ", ".join(self.qualification_info.certifications)
            summary_parts.append(f"✅ 认证: {certs}")
        
        return "\n".join(summary_parts)
    
    def is_verified(self) -> bool:
        """检查供应商信息是否已验证"""
        return self.meta_data.verification_status == VerificationStatus.VERIFIED
    
    def has_contact_info(self) -> bool:
        """检查是否有有效的联系信息"""
        return (
            self.contact_info.phone is not None or 
            self.contact_info.email is not None or 
            self.contact_info.contact_person is not None
        )


# 辅助函数
def create_empty_supplier_profile(company_name: str) -> SupplierProfile:
    """创建空的供应商档案"""
    return SupplierProfile(
        company_name=company_name,
        meta_data=MetaData(
            data_source=DataSource.MANUAL_INPUT,
            verification_status=VerificationStatus.PENDING
        )
    )


def merge_supplier_profiles(primary: SupplierProfile, secondary: SupplierProfile) -> SupplierProfile:
    """合并两个供应商档案，以primary为主，secondary补充缺失信息"""
    merged = SupplierProfile(**primary.__dict__)
    
    # 这里可以实现复杂的合并逻辑
    # 暂时简化：只补充缺失的基本信息
    if not merged.english_name and secondary.english_name:
        merged.english_name = secondary.english_name
    
    if not merged.contact_info.email and secondary.contact_info.email:
        merged.contact_info.email = secondary.contact_info.email
    
    if not merged.contact_info.phone and secondary.contact_info.phone:
        merged.contact_info.phone = secondary.contact_info.phone
    
    # 合并产品列表
    merged.business_info.main_products = list(set(
        merged.business_info.main_products + secondary.business_info.main_products
    ))
    
    # 更新元数据
    merged.meta_data.last_updated = datetime.now()
    
    return merged