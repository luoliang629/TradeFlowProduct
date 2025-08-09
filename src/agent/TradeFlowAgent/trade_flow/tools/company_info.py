"""
Company Info Tool - ADK 规范实现
"""

from typing import Dict, Any, Optional, List
import os


async def company_info(
    company_name: Optional[str] = None,
    region: Optional[str] = None,
    industry: Optional[str] = None,
    limit: int = 10,
) -> Dict[str, Any]:
    """
    查询贸易公司信息

    Args:
        company_name: 公司名称（支持模糊匹配）
        region: 所在地区
        industry: 所属行业
        limit: 返回结果数量限制

    Returns:
        公司信息查询结果
    """
    # 使用真实搜索获取企业信息
    try:
        # 构建搜索查询
        search_query = _build_company_search_query(company_name, region, industry)

        # 调用web_search工具进行搜索
        from trade_flow.tools.web_search import web_search

        search_results = await web_search(search_query, num_results=10)

        if search_results["status"] == "error":
            return {
                "status": "error",
                "error_message": f"企业信息搜索失败: {search_results.get('error', '搜索服务不可用')}",
            }

        # 解析搜索结果获取企业信息
        companies = await _extract_company_info_from_search(
            search_results["results"], company_name, region, industry, limit
        )

        return {
            "status": "success",
            "query_params": {
                "company_name": company_name,
                "region": region,
                "industry": industry,
                "limit": limit,
            },
            "total": len(companies),
            "companies": companies[:limit],
            "search_query": search_query,
        }

    except Exception as e:
        return {
            "status": "error",
            "error_message": f"企业信息查询失败: {str(e)}",
            "query_params": {
                "company_name": company_name,
                "region": region,
                "industry": industry,
                "limit": limit,
            },
        }


def _build_company_search_query(company_name: Optional[str], region: Optional[str], industry: Optional[str]) -> str:
    """构建企业搜索查询词"""
    query_parts = []

    if company_name:
        query_parts.append(f'"{company_name}"')

    if industry:
        query_parts.append(f"{industry}行业")

    if region:
        query_parts.append(f"{region}地区")

    # 添加通用搜索词
    query_parts.extend(["公司", "贸易", "出口"])

    return " ".join(query_parts)


async def _extract_company_info_from_search(
    search_results: List[Dict[str, Any]],
    company_name: Optional[str],
    region: Optional[str],
    industry: Optional[str],
    limit: int,
) -> List[Dict[str, Any]]:
    """从搜索结果中提取企业信息"""
    companies = []

    # 对于每个搜索结果，尝试提取企业信息
    for result in search_results[: limit * 2]:  # 获取更多结果以便筛选
        try:
            # 使用jina_reader分析网页内容
            from trade_flow.tools.jina_reader import jina_reader

            content_result = await jina_reader(url=result["url"], extract_type="company_info")

            if content_result["status"] == "success":
                # 从内容中提取企业信息
                company_info = _parse_company_info(content_result, result, company_name, region, industry)

                if company_info:
                    companies.append(company_info)

                    # 达到限制数量就停止
                    if len(companies) >= limit:
                        break

        except Exception as e:
            # 忽略单个网页的错误，继续处理下一个
            continue

    return companies


def _parse_company_info(
    content_result: Dict[str, Any],
    search_result: Dict[str, Any],
    company_name: Optional[str],
    region: Optional[str],
    industry: Optional[str],
) -> Optional[Dict[str, Any]]:
    """解析网页内容提取企业信息"""
    try:
        # 从网页内容中提取关键信息
        title = content_result.get("title", "")
        content = content_result.get("content", "")
        extracted_info = content_result.get("extracted_info", {})

        # 基本信息提取
        basic_info = {
            "name": _extract_company_name(title, content, company_name),
            "website": search_result["url"],
            "region": region or "未知",
            "industry": industry or "未知",
            "description": search_result.get("snippet", "")[:200],
        }

        # 贸易信息提取
        trade_info = {
            "products": _extract_products(content, extracted_info),
            "markets": _extract_markets(content),
            "contact_info": _extract_contact_info(content, extracted_info),
        }

        return {"basic_info": basic_info, "trade_info": trade_info, "source": "web_search", "last_updated": "实时数据"}

    except Exception:
        return None


def _extract_company_name(title: str, content: str, hint_name: Optional[str]) -> str:
    """提取公司名称"""
    if hint_name and hint_name in title:
        return hint_name

    # 从标题中提取公司名
    if "公司" in title or "Company" in title or "Ltd" in title:
        return title.split("-")[0].strip()

    return title[:50]  # 限制长度


def _extract_products(content: str, extracted_info: Dict) -> List[str]:
    """提取产品信息"""
    products = []

    # 从提取的实体中获取产品
    entities = extracted_info.get("entities", {})
    if "products" in entities:
        products.extend(entities["products"][:5])  # 最多5个产品

    # 如果没有找到，返回通用描述
    if not products:
        products = ["贸易产品", "工业产品"]

    return products


def _extract_markets(content: str) -> List[str]:
    """提取市场信息"""
    markets = []

    # 常见市场关键词
    market_keywords = ["欧洲", "美国", "东南亚", "中东", "非洲", "南美", "日本", "韩国"]

    for keyword in market_keywords:
        if keyword in content:
            markets.append(keyword)

    return markets[:3]  # 最多3个市场


def _extract_contact_info(content: str, extracted_info: Dict) -> Dict[str, str]:
    """提取联系信息"""
    contact_info = {}

    # 从提取的实体中获取联系方式
    entities = extracted_info.get("entities", {})
    if "contacts" in entities and entities["contacts"]:
        contact_info["email"] = entities["contacts"][0]

    return contact_info


# 导出函数作为工具
company_info_tool = company_info
