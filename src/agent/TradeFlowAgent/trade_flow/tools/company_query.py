"""
Company Query Tool - Tendata 公司查询 ADK 规范实现
"""

from typing import Dict, Any, Optional, List
import logging
from .tendata_api import (
    make_tendata_request,
    validate_api_response,
    create_error_response,
    create_success_response
)

logger = logging.getLogger(__name__)


async def search_company(
    company_name: str,
    page_no: int = 1,
    page_size: int = 20,
    country_code: Optional[str] = None,
) -> Dict[str, Any]:
    """
    搜索公司名称
    
    功能: 根据公司名称关键词搜索相关公司列表
    逻辑:
    1. 验证输入参数的有效性
    2. 构建 Tendata API 查询参数
    3. 调用 /v2/company/list 接口
    4. 处理和格式化返回结果
    
    Args:
        company_name: 公司名称关键词（支持模糊匹配）
        page_no: 页码，默认第1页
        page_size: 每页结果数量，最大20，默认20
        country_code: 国家三位代码，可选过滤条件
        
    Returns:
        Dict[str, Any]: 搜索结果，包含以下字段：
        {
            "status": "success" | "error",
            "companies": [  # 公司列表
                {
                    "id": str,  # 公司ID
                    "name": str,  # 公司名称
                    "country": str,  # 国家代码
                    "country_name": str  # 国家名称（如果可获取）
                }
            ],
            "pagination": {  # 分页信息
                "page_no": int,
                "page_size": int,
                "total": int,
                "has_more": bool
            },
            "query_params": {...},  # 查询参数
            "error_message": str  # 错误信息（仅在出错时）
        }
    """
    # 参数验证
    if not company_name or not company_name.strip():
        return create_error_response("公司名称不能为空")
    
    if page_size > 20:
        logger.warning(f"页面大小 {page_size} 超过最大值 20，已调整为 20")
        page_size = 20
    
    if page_no < 1:
        page_no = 1
    
    # 构建查询参数
    query_params = {
        "name": company_name.strip(),
        "pageNo": page_no,
        "pageSize": page_size
    }
    
    if country_code:
        # 验证国家代码格式（应该是3位字母）
        if len(country_code) == 3 and country_code.isalpha():
            query_params["countryCode3"] = country_code.upper()
        else:
            logger.warning(f"无效的国家代码格式: {country_code}，已忽略")
    
    try:
        # 调用 Tendata API
        response = await make_tendata_request(
            method="GET",
            endpoint="/v2/company/list",
            params=query_params
        )
        
        # 验证响应格式
        validated_response = validate_api_response(response, "公司搜索")
        data = validated_response.get("data", {})
        
        # 提取公司列表
        companies_raw = data.get("records", data.get("content", []))
        
        # 格式化公司信息
        companies = []
        for company in companies_raw:
            formatted_company = {
                "id": str(company.get("id", "")),
                "name": company.get("name", ""),
                "country": company.get("country", ""),
            }
            
            # 尝试获取国家名称（如果有映射的话）
            country_name = _get_country_name(company.get("country", ""))
            if country_name:
                formatted_company["country_name"] = country_name
                
            companies.append(formatted_company)
        
        # 构建分页信息
        total = data.get("total", len(companies))
        pagination = {
            "page_no": page_no,
            "page_size": page_size,
            "total": total,
            "has_more": (page_no * page_size) < total
        }
        
        return create_success_response({
            "companies": companies,
            "pagination": pagination
        }, query_params)
        
    except Exception as e:
        logger.error(f"公司搜索失败: {str(e)}")
        return create_error_response(
            f"公司搜索失败: {str(e)}，请检查网络连接或API配置",
            query_params
        )


async def get_company_detail(
    company_name: Optional[str] = None,
    company_id: Optional[str] = None,
    country_code: Optional[str] = None,
) -> Dict[str, Any]:
    """
    获取公司详细信息
    
    功能: 根据公司名称或ID获取公司的详细信息
    逻辑:
    1. 验证至少提供公司名称或ID之一
    2. 构建 Tendata API 查询参数
    3. 调用 /v2/company 接口
    4. 处理和格式化返回的详细信息
    
    Args:
        company_name: 公司名称（可选，但与 company_id 至少提供一个）
        company_id: 公司ID（可选，但与 company_name 至少提供一个）
        country_code: 国家三位代码，可选的辅助过滤条件
        
    Returns:
        Dict[str, Any]: 公司详细信息，包含以下字段：
        {
            "status": "success" | "error",
            "company": {  # 公司详细信息
                "id": str,
                "name": str,
                "website": str,
                "country": str,
                "country_name": str,
                "address": str,
                "industry": str,
                "legal_representative": str,
                "contact": {
                    "phone": str,
                    "email": str,
                    "fax": str
                },
                "trade_stats": {  # 贸易统计信息
                    "total_transactions": int,
                    "main_products": List[str],
                    "main_markets": List[str]
                }
            },
            "query_params": {...},
            "error_message": str  # 错误信息（仅在出错时）
        }
    """
    # 参数验证
    if not company_name and not company_id:
        return create_error_response("请至少提供公司名称或公司ID之一")
    
    if company_name and not company_name.strip():
        return create_error_response("公司名称不能为空")
    
    # 构建查询参数
    query_params = {}
    
    if company_name:
        query_params["name"] = company_name.strip()
    
    if company_id:
        query_params["companyId"] = str(company_id)
    
    if country_code:
        # 验证国家代码格式
        if len(country_code) == 3 and country_code.isalpha():
            query_params["countryCode3"] = country_code.upper()
        else:
            logger.warning(f"无效的国家代码格式: {country_code}，已忽略")

    query_params["filterBlank"] = "TRUE"
    
    try:
        # 调用 Tendata API
        response = await make_tendata_request(
            method="GET",
            endpoint="/v2/company",
            params=query_params
        )
        
        # 验证响应格式
        validated_response = validate_api_response(response, "公司详情查询")
        company_data = validated_response.get("data", {})
        
        # 格式化公司详细信息
        company_detail = company_data
        # company_detail = _format_company_detail(company_data)
        
        return create_success_response({
            "company": company_detail
        }, query_params)
        
    except Exception as e:
        logger.error(f"公司详情查询失败: {str(e)}")
        return create_error_response(
            f"公司详情查询失败: {str(e)}，请检查网络连接或API配置",
            query_params
        )


def _format_company_detail(company_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    格式化公司详细信息
    
    功能: 将 Tendata API 返回的原始数据转换为标准格式
    
    Args:
        company_data: Tendata API 返回的原始公司数据
        
    Returns:
        Dict[str, Any]: 格式化后的公司详细信息
    """
    formatted = {
        "id": str(company_data.get("id", "")),
        "name": company_data.get("name", ""),
        "website": company_data.get("website", ""),
        "country": company_data.get("country", ""),
        "address": company_data.get("address", ""),
        "industry": company_data.get("industry", ""),
        "legal_representative": company_data.get("legalRepresentative", ""),
    }
    
    # 添加国家名称
    country_name = _get_country_name(company_data.get("country", ""))
    if country_name:
        formatted["country_name"] = country_name
    
    # 格式化联系信息
    formatted["contact"] = {
        "phone": company_data.get("phone", ""),
        "email": company_data.get("email", ""),
        "fax": company_data.get("fax", "")
    }
    
    # 格式化贸易统计信息
    formatted["trade_stats"] = {
        "total_transactions": company_data.get("totalTransactions", 0),
        "main_products": company_data.get("mainProducts", []),
        "main_markets": company_data.get("mainMarkets", [])
    }
    
    return formatted


def _get_country_name(country_code: str) -> Optional[str]:
    """
    根据国家代码获取中文国家名称
    
    功能: 提供常用国家代码到中文名称的映射
    
    Args:
        country_code: 三位字母国家代码
        
    Returns:
        Optional[str]: 中文国家名称，未找到则返回 None
    """
    country_mapping = {
        "CHN": "中国",
        "USA": "美国",
        "DEU": "德国", 
        "JPN": "日本",
        "GBR": "英国",
        "FRA": "法国",
        "ITA": "意大利",
        "CAN": "加拿大",
        "KOR": "韩国",
        "NLD": "荷兰",
        "BEL": "比利时",
        "ESP": "西班牙",
        "AUS": "澳大利亚",
        "BRA": "巴西",
        "IND": "印度",
        "RUS": "俄罗斯",
        "MEX": "墨西哥",
        "SGP": "新加坡",
        "THA": "泰国",
        "VNM": "越南",
        "MYS": "马来西亚",
        "IDN": "印度尼西亚",
        "PHL": "菲律宾",
        "ARE": "阿联酋",
        "SAU": "沙特阿拉伯",
        "TUR": "土耳其",
        "POL": "波兰",
        "CZE": "捷克",
        "HUN": "匈牙利",
        "SWE": "瑞典",
        "NOR": "挪威",
        "DNK": "丹麦",
        "FIN": "芬兰",
        "CHE": "瑞士",
        "AUT": "奥地利",
        "PRT": "葡萄牙",
        "GRC": "希腊",
        "ZAF": "南非",
        "EGY": "埃及",
        "ISR": "以色列",
        "ARG": "阿根廷",
        "CHL": "智利",
        "COL": "哥伦比亚",
        "PER": "秘鲁",
        "NZL": "新西兰",
        "TWN": "中国台湾",
        "HKG": "中国香港",
        "MAC": "中国澳门",
    }
    
    return country_mapping.get(country_code.upper()) if country_code else None


# 导出函数作为工具
search_company_tool = search_company
get_company_detail_tool = get_company_detail