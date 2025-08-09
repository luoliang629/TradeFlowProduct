"""
企业发现工具
多源企业数据聚合器，从各B2B平台发现具体企业信息
这是解决"只有区域建议，没有具体企业"问题的核心工具
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
import aiohttp
import json
import re
from urllib.parse import quote, urljoin
from datetime import datetime

from trade_flow.shared_libraries.supplier_profile import (
    SupplierProfile, ContactInfo, AddressInfo, BusinessInfo, 
    OnlinePresence, MetaData, DataSource, VerificationStatus,
    CompanyType, create_empty_supplier_profile
)
from trade_flow.config import get_setting

# 配置日志
logger = logging.getLogger(__name__)


class EnterpriseDiscovery:
    """企业发现引擎 - 从多个B2B平台发现具体企业"""
    
    def __init__(self):
        self.jina_api_key = get_setting("JINA_API_KEY")
        self.session: Optional[aiohttp.ClientSession] = None
        
        # B2B平台搜索端点配置
        self.search_endpoints = {
            "alibaba": {
                "search_url": "https://s.jina.ai/https://www.alibaba.com/trade/search?SearchText={query}",
                "headers": {"Authorization": f"Bearer {self.jina_api_key}"},
                "platform": DataSource.ALIBABA
            },
            "made_in_china": {
                "search_url": "https://s.jina.ai/https://www.made-in-china.com/productdirectory.do?word={query}",
                "headers": {"Authorization": f"Bearer {self.jina_api_key}"},
                "platform": DataSource.MADE_IN_CHINA
            },
            "global_sources": {
                "search_url": "https://s.jina.ai/https://www.globalsources.com/gsol/I/",
                "headers": {"Authorization": f"Bearer {self.jina_api_key}"},
                "platform": DataSource.GLOBAL_SOURCES
            }
        }
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()
    
    async def discover_suppliers(
        self, 
        product_query: str, 
        region: Optional[str] = None,
        max_results: int = 20,
        platforms: Optional[List[str]] = None
    ) -> List[SupplierProfile]:
        """
        发现供应商企业
        
        Args:
            product_query: 产品查询关键词，如"丝绸围巾"
            region: 地区限制，如"杭州"、"浙江"
            max_results: 最大返回结果数
            platforms: 指定搜索的平台列表，如["alibaba", "made_in_china"]
        
        Returns:
            List[SupplierProfile]: 发现的供应商列表
        """
        if not self.session:
            raise RuntimeError("必须在异步上下文中使用 EnterpriseDiscovery")
        
        # 构建搜索查询
        search_query = self._build_search_query(product_query, region)
        logger.info(f"开始企业发现：查询='{search_query}', 地区='{region}', 最大结果数={max_results}")
        
        # 确定要搜索的平台
        target_platforms = platforms or ["alibaba", "made_in_china"]
        
        # 并行搜索多个平台
        search_tasks = []
        for platform in target_platforms:
            if platform in self.search_endpoints:
                task = self._search_platform(platform, search_query, max_results // len(target_platforms))
                search_tasks.append(task)
        
        # 等待所有搜索完成
        platform_results = await asyncio.gather(*search_tasks, return_exceptions=True)
        
        # 合并和去重结果
        all_suppliers = []
        for result in platform_results:
            if isinstance(result, Exception):
                logger.error(f"平台搜索失败: {result}")
                continue
            if isinstance(result, list):
                all_suppliers.extend(result)
        
        # 去重和排序
        unique_suppliers = self._deduplicate_suppliers(all_suppliers)
        sorted_suppliers = self._sort_suppliers(unique_suppliers, product_query, region)
        
        logger.info(f"企业发现完成：找到 {len(sorted_suppliers)} 家企业")
        return sorted_suppliers[:max_results]
    
    def _build_search_query(self, product_query: str, region: Optional[str] = None) -> str:
        """构建搜索查询字符串"""
        query_parts = [product_query]
        
        if region:
            query_parts.append(region)
        
        # 添加供应商相关关键词
        query_parts.extend(["supplier", "manufacturer", "factory"])
        
        return " ".join(query_parts)
    
    async def _search_platform(self, platform: str, query: str, max_results: int) -> List[SupplierProfile]:
        """搜索单个B2B平台"""
        endpoint_config = self.search_endpoints[platform]
        
        try:
            # 使用Jina Search搜索B2B平台
            search_url = endpoint_config["search_url"].format(query=quote(query))
            headers = endpoint_config["headers"]
            
            logger.info(f"搜索平台 {platform}: {search_url}")
            
            async with self.session.get(search_url, headers=headers) as response:
                if response.status == 200:
                    content = await response.text()
                    suppliers = await self._extract_suppliers_from_content(
                        content, platform, endpoint_config["platform"]
                    )
                    logger.info(f"从 {platform} 提取到 {len(suppliers)} 家企业")
                    return suppliers[:max_results]
                else:
                    logger.error(f"搜索平台 {platform} 失败: HTTP {response.status}")
                    return []
        
        except Exception as e:
            logger.error(f"搜索平台 {platform} 异常: {e}")
            return []
    
    async def _extract_suppliers_from_content(
        self, 
        content: str, 
        platform: str, 
        data_source: DataSource
    ) -> List[SupplierProfile]:
        """从网页内容中提取供应商信息"""
        suppliers = []
        
        try:
            # 使用正则表达式和文本分析提取企业信息
            if platform == "alibaba":
                suppliers = self._extract_alibaba_suppliers(content, data_source)
            elif platform == "made_in_china":
                suppliers = self._extract_made_in_china_suppliers(content, data_source)
            elif platform == "global_sources":
                suppliers = self._extract_global_sources_suppliers(content, data_source)
            
            # 为每个供应商添加基础信息
            for supplier in suppliers:
                supplier.meta_data.data_source = data_source
                supplier.meta_data.crawl_time = datetime.now()
                supplier.meta_data.verification_status = VerificationStatus.PENDING
            
        except Exception as e:
            logger.error(f"从 {platform} 内容提取企业信息失败: {e}")
        
        return suppliers
    
    def _extract_alibaba_suppliers(self, content: str, data_source: DataSource) -> List[SupplierProfile]:
        """从阿里巴巴搜索结果提取供应商信息"""
        suppliers = []
        
        # 查找企业信息模式（简化版）
        company_patterns = [
            r'title="([^"]*?(?:Company|Co\.|Ltd\.|Inc\.|Corp\.|Limited)[^"]*?)"',
            r'company-name[^>]*>([^<]*?(?:Company|Co\.|Ltd\.|Inc\.|Corp\.|Limited)[^<]*?)</[^>]*>',
            r'supplier[^>]*>([^<]*?(?:Company|Co\.|Ltd\.|Inc\.|Corp\.|Limited)[^<]*?)</[^>]*>'
        ]
        
        found_companies = set()
        for pattern in company_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                company_name = match.strip()
                if len(company_name) > 3 and company_name not in found_companies:
                    found_companies.add(company_name)
        
        # 创建供应商档案
        for company_name in list(found_companies)[:10]:  # 限制数量
            supplier = create_empty_supplier_profile(company_name)
            supplier.meta_data.data_source = data_source
            supplier.company_type = CompanyType.MANUFACTURER  # 默认类型
            
            # 尝试提取联系信息
            self._extract_contact_info_from_text(supplier, content, company_name)
            
            suppliers.append(supplier)
        
        return suppliers
    
    def _extract_made_in_china_suppliers(self, content: str, data_source: DataSource) -> List[SupplierProfile]:
        """从Made-in-China搜索结果提取供应商信息"""
        suppliers = []
        
        # Made-in-China特定的企业信息提取模式
        company_patterns = [
            r'company[^>]*>([^<]*?(?:Company|Co\.|Ltd\.|Inc\.|Corp\.|Limited|Manufacturer)[^<]*?)</[^>]*>',
            r'supplier[^>]*title="([^"]*?(?:Company|Co\.|Ltd\.|Inc\.|Corp\.|Limited)[^"]*?)"',
            r'manufacturer[^>]*>([^<]*?(?:Company|Co\.|Ltd\.|Inc\.|Corp\.|Limited)[^<]*?)</[^>]*>'
        ]
        
        found_companies = set()
        for pattern in company_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                company_name = match.strip()
                if len(company_name) > 3 and company_name not in found_companies:
                    found_companies.add(company_name)
        
        # 创建供应商档案
        for company_name in list(found_companies)[:10]:
            supplier = create_empty_supplier_profile(company_name)
            supplier.meta_data.data_source = data_source
            supplier.company_type = CompanyType.MANUFACTURER
            
            # 提取联系信息
            self._extract_contact_info_from_text(supplier, content, company_name)
            
            suppliers.append(supplier)
        
        return suppliers
    
    def _extract_global_sources_suppliers(self, content: str, data_source: DataSource) -> List[SupplierProfile]:
        """从Global Sources搜索结果提取供应商信息"""
        suppliers = []
        
        # Global Sources特定的企业信息提取模式
        company_patterns = [
            r'company[^>]*>([^<]*?(?:Company|Co\.|Ltd\.|Inc\.|Corp\.|Limited|Mfg|Manufacturing)[^<]*?)</[^>]*>',
            r'supplier[^>]*>([^<]*?(?:Company|Co\.|Ltd\.|Inc\.|Corp\.|Limited)[^<]*?)</[^>]*>'
        ]
        
        found_companies = set()
        for pattern in company_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                company_name = match.strip()
                if len(company_name) > 3 and company_name not in found_companies:
                    found_companies.add(company_name)
        
        # 创建供应商档案
        for company_name in list(found_companies)[:10]:
            supplier = create_empty_supplier_profile(company_name)
            supplier.meta_data.data_source = data_source
            supplier.company_type = CompanyType.TRADING_COMPANY
            
            # 提取联系信息
            self._extract_contact_info_from_text(supplier, content, company_name)
            
            suppliers.append(supplier)
        
        return suppliers
    
    def _extract_contact_info_from_text(self, supplier: SupplierProfile, content: str, company_name: str):
        """从文本中提取联系信息"""
        # 查找公司名称附近的联系信息
        company_section = self._find_company_section(content, company_name)
        
        # 提取电话号码
        phone_patterns = [
            r'(\+?\d{1,3}[-.\s]?\d{3,4}[-.\s]?\d{3,4}[-.\s]?\d{3,4})',
            r'phone[^:]*:[\s]*([+\d\s\-\(\)]+)',
            r'tel[^:]*:[\s]*([+\d\s\-\(\)]+)'
        ]
        for pattern in phone_patterns:
            match = re.search(pattern, company_section, re.IGNORECASE)
            if match:
                supplier.contact_info.phone = match.group(1).strip()
                break
        
        # 提取邮箱
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, company_section)
        if email_match:
            supplier.contact_info.email = email_match.group(0)
        
        # 提取联系人姓名
        contact_patterns = [
            r'contact[^:]*:[\s]*([A-Za-z\s]+)',
            r'manager[^:]*:[\s]*([A-Za-z\s]+)',
            r'sales[^:]*:[\s]*([A-Za-z\s]+)'
        ]
        for pattern in contact_patterns:
            match = re.search(pattern, company_section, re.IGNORECASE)
            if match:
                contact_name = match.group(1).strip()
                if len(contact_name) < 50:  # 避免提取过长的文本
                    supplier.contact_info.contact_person = contact_name
                    break
        
        # 提取地址信息
        address_patterns = [
            r'address[^:]*:[\s]*([^\n]{10,100})',
            r'location[^:]*:[\s]*([^\n]{10,100})'
        ]
        for pattern in address_patterns:
            match = re.search(pattern, company_section, re.IGNORECASE)
            if match:
                address = match.group(1).strip()
                supplier.address_info.company_address = address
                break
    
    def _find_company_section(self, content: str, company_name: str) -> str:
        """查找公司名称附近的内容段落"""
        # 查找公司名称在内容中的位置
        company_pos = content.lower().find(company_name.lower())
        if company_pos == -1:
            return content[:1000]  # 如果找不到，返回前1000字符
        
        # 提取公司名称前后各500字符的内容
        start = max(0, company_pos - 500)
        end = min(len(content), company_pos + len(company_name) + 500)
        
        return content[start:end]
    
    def _deduplicate_suppliers(self, suppliers: List[SupplierProfile]) -> List[SupplierProfile]:
        """去重供应商列表"""
        seen_names = set()
        unique_suppliers = []
        
        for supplier in suppliers:
            # 标准化公司名称用于比较
            normalized_name = supplier.company_name.lower().strip()
            normalized_name = re.sub(r'\s+', ' ', normalized_name)  # 标准化空格
            
            if normalized_name not in seen_names:
                seen_names.add(normalized_name)
                unique_suppliers.append(supplier)
        
        return unique_suppliers
    
    def _sort_suppliers(
        self, 
        suppliers: List[SupplierProfile], 
        product_query: str, 
        region: Optional[str]
    ) -> List[SupplierProfile]:
        """根据相关性和质量对供应商排序"""
        
        def calculate_relevance_score(supplier: SupplierProfile) -> float:
            score = 0.0
            
            # 公司名称相关性
            if product_query.lower() in supplier.company_name.lower():
                score += 2.0
            
            # 地区相关性
            if region and supplier.address_info.company_address:
                if region.lower() in supplier.address_info.company_address.lower():
                    score += 1.5
            
            # 联系信息完整性
            if supplier.contact_info.phone:
                score += 1.0
            if supplier.contact_info.email:
                score += 1.0
            if supplier.contact_info.contact_person:
                score += 0.5
            
            # 地址信息完整性
            if supplier.address_info.company_address:
                score += 0.5
            
            # 数据来源可信度
            if supplier.meta_data.data_source == DataSource.ALIBABA:
                score += 1.0
            elif supplier.meta_data.data_source == DataSource.MADE_IN_CHINA:
                score += 0.8
            
            return score
        
        # 计算每个供应商的相关性得分
        for supplier in suppliers:
            relevance_score = calculate_relevance_score(supplier)
            supplier.quality_scores.matching_score = relevance_score
            supplier.quality_scores.overall_score = relevance_score  # 临时使用相关性作为总评分
        
        # 按相关性得分排序
        return sorted(suppliers, key=lambda s: s.quality_scores.overall_score, reverse=True)


# 工具接口函数
async def discover_suppliers(
    product_query: str,
    region: Optional[str] = None,
    max_results: int = 10,
    platforms: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    企业发现工具的主要接口
    
    Args:
        product_query: 产品查询关键词
        region: 地区限制（可选）
        max_results: 最大返回结果数
        platforms: 指定搜索平台（可选）
    
    Returns:
        Dict包含发现的供应商列表和统计信息
    """
    try:
        async with EnterpriseDiscovery() as discovery:
            suppliers = await discovery.discover_suppliers(
                product_query=product_query,
                region=region,
                max_results=max_results,
                platforms=platforms
            )
            
            # 统计信息
            stats = {
                "total_found": len(suppliers),
                "with_contact_info": sum(1 for s in suppliers if s.has_contact_info()),
                "verified": sum(1 for s in suppliers if s.is_verified()),
                "data_sources": list(set(s.meta_data.data_source.value for s in suppliers))
            }
            
            return {
                "status": "success",
                "suppliers": [supplier.to_dict() for supplier in suppliers],
                "stats": stats,
                "query_info": {
                    "product_query": product_query,
                    "region": region,
                    "max_results": max_results,
                    "search_time": datetime.now().isoformat()
                }
            }
    
    except Exception as e:
        logger.error(f"企业发现失败: {e}")
        return {
            "status": "error",
            "error": str(e),
            "suppliers": [],
            "stats": {"total_found": 0}
        }


# 测试和示例用法
async def test_enterprise_discovery():
    """测试企业发现功能"""
    print("🔍 测试企业发现功能...")
    
    result = await discover_suppliers(
        product_query="丝绸围巾",
        region="杭州",
        max_results=5,
        platforms=["alibaba", "made_in_china"]
    )
    
    print(f"发现结果: {result['stats']}")
    
    for i, supplier_dict in enumerate(result['suppliers'][:3], 1):
        supplier = SupplierProfile.from_dict(supplier_dict)
        print(f"\n🏆 TOP {i}:")
        print(supplier.get_display_summary())


if __name__ == "__main__":
    # 运行测试
    asyncio.run(test_enterprise_discovery())