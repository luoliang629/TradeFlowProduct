"""
企业发现专用Agent
专门负责发现具体的供应商企业，而非区域性建议
解决"只有区域供应商，没有具体某某公司"的核心问题
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from google.adk import Agent
from google.adk.tools import FunctionTool

from trade_flow.tools.enterprise_discovery import discover_suppliers
from trade_flow.config import get_model_config
from trade_flow.shared_libraries.supplier_profile import SupplierProfile

# 配置日志
logger = logging.getLogger(__name__)


class EnterpriseDiscoveryAgent:
    """企业发现Agent - 专门发现具体企业而非区域建议"""
    
    def __init__(self):
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """创建企业发现Agent"""
        
        # 定义工具
        tools = [
            self._create_discover_suppliers_tool(),
            self._create_extract_contact_tool(),
            self._create_enhance_supplier_profile_tool()
        ]
        
        # 企业发现专用指令
        instruction = """
你是企业发现专家，专门负责发现具体的供应商企业。你的核心任务是：

🎯 **核心目标**：
将用户的需求转化为具体的企业推荐，而非区域性建议。
必须返回具体的"某某公司"，包含完整联系信息。

📋 **工作流程**：
1. **需求理解**：准确理解用户的产品需求、质量要求、数量规模
2. **企业发现**：从多个B2B平台搜索相关的具体企业
3. **联系信息提取**：获取企业的详细联系信息（电话、邮箱、联系人）
4. **企业档案构建**：整合企业的完整信息档案
5. **质量排序**：按照匹配度和质量对企业进行排序
6. **结果输出**：返回TOP企业列表，包含完整联系信息

⚠️ **重要原则**：
- 绝对不要返回"某个地区的供应商"这样的泛泛建议
- 必须返回具体的企业名称和联系方式
- 如果无法找到具体企业，要明确说明并提供搜索建议
- 优先提供已验证的联系信息

🎨 **输出格式**：
对于每个推荐的企业，必须包含：
- 🏆 企业名称和评分
- 📍 详细地址
- 👤 联系人姓名和职位
- 📞 电话号码
- 📧 邮箱地址
- 🌐 网站链接（如有）
- 💼 主营产品
- 📦 起订量和交期
- ✅ 认证资质

📊 **质量标准**：
- 联系信息完整度 >80%
- 企业信息真实性验证
- 与用户需求的匹配度评估
- 企业规模和能力评估

记住：你的价值在于提供可直接联系的具体企业，让用户能够立即开展商务沟通！
"""
        
        return Agent(
            name="enterprise_discovery_agent",
            model=get_model_config(),
            tools=tools,
            instruction=instruction,
            output_key="enterprise_discovery_result"
        )
    
    def _create_discover_suppliers_tool(self) -> FunctionTool:
        """创建企业发现工具"""
        
        async def discover_suppliers_handler(
            product_query: str,
            region: Optional[str] = None,
            max_results: int = 10,
            platforms: Optional[List[str]] = None
        ) -> Dict[str, Any]:
            """
            发现供应商企业
            
            Args:
                product_query: 产品查询关键词，如"丝绸围巾"、"电子产品"
                region: 地区限制，如"杭州"、"浙江"、"广东"
                max_results: 最大返回结果数，默认10
                platforms: 搜索平台列表，如["alibaba", "made_in_china"]
            
            Returns:
                发现的供应商企业列表和统计信息
            """
            try:
                logger.info(f"开始企业发现：产品={product_query}, 地区={region}")
                
                result = await discover_suppliers(
                    product_query=product_query,
                    region=region,
                    max_results=max_results,
                    platforms=platforms or ["alibaba", "made_in_china"]
                )
                
                logger.info(f"企业发现完成：找到 {result['stats']['total_found']} 家企业")
                return result
                
            except Exception as e:
                logger.error(f"企业发现失败: {e}")
                return {
                    "status": "error",
                    "error": str(e),
                    "suppliers": [],
                    "stats": {"total_found": 0}
                }
        
        return FunctionTool(func=discover_suppliers_handler)
    
    def _create_extract_contact_tool(self) -> FunctionTool:
        """创建联系信息提取工具"""
        
        async def extract_contact_handler(
            company_name: str,
            source_url: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            提取企业的详细联系信息
            
            Args:
                company_name: 企业名称
                source_url: 源URL，用于进一步提取信息
            
            Returns:
                企业的详细联系信息
            """
            try:
                logger.info(f"开始提取联系信息：{company_name}")
                
                result = await extract_contact_information(
                    company_name=company_name,
                    source_url=source_url
                )
                
                logger.info(f"联系信息提取完成：{company_name}")
                return result
                
            except Exception as e:
                logger.error(f"联系信息提取失败: {company_name}, {e}")
                return {
                    "status": "error",
                    "error": str(e),
                    "company_name": company_name,
                    "contact_info": {}
                }
        
        return FunctionTool(func=extract_contact_handler)
    
    def _create_enhance_supplier_profile_tool(self) -> FunctionTool:
        """创建供应商档案增强工具"""
        
        async def enhance_profile_handler(
            suppliers_data: List[Dict[str, Any]]
        ) -> Dict[str, Any]:
            """
            增强供应商档案信息
            
            Args:
                suppliers_data: 供应商数据列表
            
            Returns:
                增强后的供应商档案信息
            """
            try:
                enhanced_suppliers = []
                
                for supplier_data in suppliers_data[:5]:  # 限制处理数量
                    supplier = SupplierProfile.from_dict(supplier_data)
                    
                    # 如果缺少联系信息，尝试提取
                    if not supplier.has_contact_info():
                        contact_result = await extract_contact_information(
                            company_name=supplier.company_name
                        )
                        
                        if contact_result["status"] == "success":
                            contact_info = contact_result["contact_info"]
                            supplier.contact_info.contact_person = contact_info.get("contact_person")
                            supplier.contact_info.phone = contact_info.get("phone")
                            supplier.contact_info.email = contact_info.get("email")
                            supplier.contact_info.confidence_score = contact_info.get("confidence_score", 0.0)
                    
                    # 计算数据完整度
                    completeness = supplier.calculate_completeness()
                    supplier.meta_data.data_completeness = completeness
                    
                    enhanced_suppliers.append(supplier.to_dict())
                
                return {
                    "status": "success",
                    "enhanced_suppliers": enhanced_suppliers,
                    "enhancement_count": len(enhanced_suppliers)
                }
                
            except Exception as e:
                logger.error(f"供应商档案增强失败: {e}")
                return {
                    "status": "error",
                    "error": str(e),
                    "enhanced_suppliers": suppliers_data
                }
        
        return FunctionTool(func=enhance_profile_handler)
    
    async def discover_enterprises(
        self, 
        user_query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        企业发现的主要接口
        
        Args:
            user_query: 用户查询
            context: 上下文信息
        
        Returns:
            企业发现结果
        """
        try:
            logger.info(f"企业发现Agent开始处理：{user_query}")
            
            # 使用Agent处理查询
            response = await self.agent.run(user_query, context=context or {})
            
            logger.info("企业发现Agent处理完成")
            return {
                "status": "success",
                "agent_response": response,
                "discovery_type": "enterprise_specific"
            }
            
        except Exception as e:
            logger.error(f"企业发现Agent处理失败: {e}")
            return {
                "status": "error",
                "error": str(e),
                "discovery_type": "enterprise_specific"
            }


# 创建全局企业发现Agent实例
enterprise_discovery_agent = EnterpriseDiscoveryAgent().agent


async def test_enterprise_discovery_agent():
    """测试企业发现Agent"""
    print("🤖 测试企业发现Agent...")
    
    agent = EnterpriseDiscoveryAgent()
    
    test_queries = [
        "我需要找到具体的丝绸围巾供应商，要有联系方式",
        "寻找杭州地区的纺织品制造商，需要具体的公司信息",
        "请推荐几家电子产品供应商，要有详细联系信息"
    ]
    
    for query in test_queries:
        print(f"\n🔍 查询: {query}")
        result = await agent.discover_enterprises(query)
        
        if result["status"] == "success":
            print("✅ 企业发现成功")
        else:
            print(f"❌ 企业发现失败: {result.get('error', '未知错误')}")


if __name__ == "__main__":
    # 运行测试
    asyncio.run(test_enterprise_discovery_agent())