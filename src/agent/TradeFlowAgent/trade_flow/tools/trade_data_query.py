"""
Trade Data Query Tool - ADK 规范实现
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
from .tendata_api import (
    make_tendata_request,
    validate_api_response,
    create_error_response,
    create_success_response,
    get_tendata_auth
)
from .tendata_auth import TendataAuth
from .artifacts_manager import save_trade_data_artifact

# 配置日志
logger = logging.getLogger(__name__)


async def get_trade_data(
    product_desc: Optional[str] = None,
    hs_code: Optional[str] = None,
    importer: Optional[str] = None,
    exporter: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    origin_country: Optional[str] = None,
    destination_country: Optional[str] = None,
) -> Dict[str, Any]:
    """
    获取贸易数据

    Args:
        product_desc: 产品描述（如：电子产品、纺织品、机械设备）
        hs_code: HS编码（海关商品编码，如：8517、6109）
        importer: 进口商名称（支持模糊匹配）
        exporter: 出口商名称（支持模糊匹配）
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
        origin_country: 原产国（支持中文名如"中国"或三位代码如"CHN"）
        destination_country: 目的国（支持中文名如"美国"或三位代码如"USA"）

    Returns:
        贸易数据查询结果
    """
    # 验证至少有一个查询条件
    if not product_desc and not hs_code and not importer and not exporter:
        return create_error_response("请至少提供产品描述、HS编码、进口商或出口商之一作为查询条件")
    
    # 验证 API 配置
    auth = get_tendata_auth()
    if not auth:
        return create_error_response("Tendata API 未配置，请设置 TENDATA_API_KEY")

    try:        
        # 调用 Tendata API
        result = await _get_trade_data_list(
            auth,
            product_desc=product_desc,
            hs_code=hs_code,
            importer=importer,
            exporter=exporter,
            start_date=start_date,
            end_date=end_date,
            origin_country=origin_country,
            destination_country=destination_country,
        )
                
        return result
    except Exception as e:
        # API调用失败，返回明确错误
        logger.error(f"Tendata API 调用失败: {str(e)}")
        return create_error_response(
            f"贸易数据查询失败: {str(e)}，请检查网络连接或API配置",
            {
                "product_desc": product_desc,
                "hs_code": hs_code,
                "importer": importer,
                "exporter": exporter,
                "start_date": start_date,
                "end_date": end_date,
                "origin_country": origin_country,
                "destination_country": destination_country,
            }
        )


async def get_trade_data_count(
    product_desc: Optional[str] = None,
    hs_code: Optional[str] = None,
    importer: Optional[str] = None,
    exporter: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    origin_country: Optional[str] = None,
    destination_country: Optional[str] = None,
) -> Dict[str, Any]:
    """
    获取贸易数据记录数量
    
    功能: 查询符合条件的贸易记录总数，不获取具体的贸易数据内容
    用途: 用于快速评估查询结果规模，优化后续查询策略
    
    Args:
        product_desc: 产品描述（如：电子产品、纺织品、机械设备）
        hs_code: HS编码（海关商品编码，如：8517、6109）
        importer: 进口商名称（支持模糊匹配）
        exporter: 出口商名称（支持模糊匹配）
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
        origin_country: 原产国（支持中文名如"中国"或三位代码如"CHN"）
        destination_country: 目的国（支持中文名如"美国"或三位代码如"USA"）

    Returns:
        包含记录数量信息的字典，格式如下：
        {
            "status": "success" | "error",
            "total_count": int,  # 总记录数
            "query_params": {...},  # 查询参数
            "count_by_type": {...},  # 按贸易类型分组的数量（如果是both）
            "error_message": str  # 错误信息（仅在出错时）
        }
    """
    # 验证至少有一个查询条件
    if not product_desc and not hs_code and not importer and not exporter:
        return create_error_response("请至少提供产品描述、HS编码、进口商或出口商之一作为查询条件")
        
    # 验证 API 配置
    auth = get_tendata_auth()
    if not auth:
        return create_error_response("Tendata API 未配置，请设置 TENDATA_API_KEY")

    try:
        # 获取记录数量
        result = await _get_trade_data_count(
            auth,
            product_desc=product_desc,
            hs_code=hs_code,
            importer=importer,
            exporter=exporter,
            start_date=start_date,
            end_date=end_date,
            origin_country=origin_country,
            destination_country=destination_country,
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Tendata API 调用失败: {str(e)}")
        return create_error_response(
            f"贸易数据数量查询失败: {str(e)}，请检查网络连接或API配置",
            {
                "product_desc": product_desc,
                "hs_code": hs_code,
                "importer": importer,
                "exporter": exporter,
                "start_date": start_date,
                "end_date": end_date,
                "origin_country": origin_country,
                "destination_country": destination_country,
            }
        )


async def _get_trade_data_count(
    auth: TendataAuth,
    product_desc: Optional[str],
    hs_code: Optional[str],
    importer: Optional[str],
    exporter: Optional[str],
    start_date: str,
    end_date: str,
    origin_country: Optional[str],
    destination_country: Optional[str],
) -> Dict[str, Any]:
    """
    获取贸易记录数量（内部函数）

    Args:
        auth: Tendata 认证实例
        product_desc: 产品描述
        hs_code: HS编码
        importer: 进口商名称
        exporter: 出口商名称
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
        origin_country: 原产国代码
        destination_country: 目的国代码

    Returns:
        包含记录数量的结果字典
    """

    # 准备返回结果
    result = {
        "status": "success",
        "query_params": {
            "product_desc": product_desc,
            "hs_code": hs_code,
            "importer": importer,
            "exporter": exporter,
            "start_date": start_date,
            "end_date": end_date,
            "origin_country": origin_country,
            "destination_country": destination_country,
        }
    }

    total_count = 0

    try:
        query_params = _build_tendata_query_params(
            product_desc=product_desc,
            hs_code=hs_code,
            importer=importer,
            exporter=exporter,
            start_date=start_date,
            end_date=end_date,
            origin_country=origin_country,
            destination_country=destination_country,
            trade_type="imports"
        )
                
        count_response = await make_tendata_request(
            "POST", "/v2/trade/row-count", json_data=query_params
        )
        total_count = count_response.get("data", {}).get("total", 0)

        # 组装结果
        result["total_count"] = total_count

        return result

    except Exception as e:
        logger.error(f"查询记录数量失败，错误: {str(e)}")
        raise

async def _get_trade_data_list(
    auth: TendataAuth,
    product_desc: Optional[str],
    hs_code: Optional[str],
    importer: Optional[str],
    exporter: Optional[str],
    start_date: str,
    end_date: str,
    origin_country: Optional[str],
    destination_country: Optional[str],
) -> Dict[str, Any]:
    """
    查询 Tendata API 获取贸易数据

    Args:
        auth: Tendata 认证实例
        product_desc: 产品描述
        hs_code: HS编码
        importer: 进口商名称
        exporter: 出口商名称
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
        origin_country: 原产国代码
        destination_country: 目的国代码

    Returns:
        查询结果
    """
    # 构建查询参数
    query_params = _build_tendata_query_params(
        product_desc=product_desc,
        hs_code=hs_code,
        importer=importer,
        exporter=exporter,
        start_date=start_date,
        end_date=end_date,
        origin_country=origin_country,
        destination_country=destination_country,
        trade_type="imports"
    )

    # 记录查询参数以便调试
    # logger.info(f"Tendata API 查询参数: {query_params}")
    
    # 查询贸易记录数量
    try:
        count_response = await make_tendata_request("POST", "/v2/trade/row-count", json_data=query_params)
        total_count = count_response.get("data", {}).get("total", 0)
    except Exception as e:
        logger.error(f"查询记录数量失败，参数: {query_params}, 错误: {str(e)}")
        raise

    # 如果没有数据，返回空结果
    if total_count == 0:
        return {
            "status": "success",
            "query_params": {
                "product_desc": product_desc,
                "hs_code": hs_code,
                "importer": importer,
                "exporter": exporter,
                "start_date": start_date,
                "end_date": end_date,
                "origin_country": origin_country,
                "destination_country": destination_country,
            },
            "data_summary": {},
            "trends": [],
            "insights": ["未找到符合条件的贸易数据"],
        }

    # 查询贸易记录（第一页）
    query_params["pageNo"] = 1
    query_params["pageSize"] = 100
    trade_response = await make_tendata_request("POST", "/v2/trade", json_data=query_params)

    # 记录API返回以便调试
    # logger.info(f"Tendata API 返回: {trade_response}")

    # 处理和分析数据
    trade_data = trade_response.get("data", {})
    records = trade_data.get("content", [])
    
    # 构建基础返回结果
    result = {
        "status": "success",
        "query_params": {
            "product_desc": product_desc,
            "hs_code": hs_code,
            "importer": importer,
            "exporter": exporter,
            "start_date": start_date,
            "end_date": end_date,
            "origin_country": origin_country,
            "destination_country": destination_country,
            "total_records": total_count,
        },
        "trade_records": records
    }
    
    # 如果有贸易记录，自动保存到 Artifacts
    if records and len(records) > 0:
        try:
            artifact_result = await save_trade_data_artifact(
                trade_records=records,
                query_params=result["query_params"],
            )
            
            if artifact_result.get("success"):
                result["artifact_info"] = {
                    "saved": True,
                    "artifact_id": artifact_result.get("artifact_id"),
                    "filename": artifact_result.get("filename"),
                    "records_count": artifact_result.get("records_count"),
                    "csv_size_bytes": artifact_result.get("csv_size_bytes")
                }
                logger.info(f"成功保存贸易数据到 Artifact: {artifact_result.get('filename')}")
            else:
                result["artifact_info"] = {
                    "saved": False,
                    "error": artifact_result.get("error", "保存失败")
                }
                logger.warning(f"保存贸易数据到 Artifact 失败: {artifact_result.get('error')}")
        except Exception as e:
            logger.error(f"保存贸易数据到 Artifact 时发生异常: {str(e)}")
            result["artifact_info"] = {
                "saved": False,
                "error": f"保存异常: {str(e)}"
            }
    
    return result


def _build_tendata_query_params(
    product_desc: Optional[str],
    hs_code: Optional[str],
    importer: Optional[str],
    exporter: Optional[str],
    start_date: str,
    end_date: str,
    origin_country: Optional[str],
    destination_country: Optional[str],
    trade_type: str,
) -> Dict[str, Any]:
    """
    构建 Tendata API 查询参数
    
    功能: 将用户输入参数转换为 Tendata API 格式的查询参数
    逻辑: 
    1. 处理日期格式，将月份转为具体的日期范围
    2. 处理产品描述和HS编码参数
    3. 处理进口商和出口商名称
    4. 根据贸易类型设置 catalog
    5. 处理原产国和目的国代码
    
    Args:
        product_desc: 产品描述（对应 Tendata API 的 productDesc）
        hs_code: HS编码（对应 Tendata API 的 hsCode）
        importer: 进口商名称（对应 Tendata API 的 importer）
        exporter: 出口商名称（对应 Tendata API 的 exporter）
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
        origin_country: 原产国代码（对应 Tendata API 的 countryOfOriginCode）
        destination_country: 目的国代码（对应 Tendata API 的 countryOfDestinationCode）
        trade_type: 贸易类型 (exports/imports)
        
    Returns:
        Dict[str, Any]: Tendata API 查询参数字典
        
    Raises:
        ValueError: 日期格式不正确时
    """

    # 日期格式验证和处理
    validated_start_date, validated_end_date = _validate_and_process_dates(start_date, end_date)
    
    params = {
        "startDate": validated_start_date,
        "endDate": validated_end_date,
    }

    # 设置贸易类型
    params["catalog"] = trade_type

    # 添加产品描述（如果提供）
    if product_desc:
        params["productDesc"] = product_desc

    # 添加HS编码（如果提供）
    if hs_code:
        # 清理HS编码格式
        cleaned_hs_code = hs_code.upper().replace("HS", "").strip()
        if cleaned_hs_code.isdigit() and len(cleaned_hs_code) >= 4:
            params["hsCode"] = cleaned_hs_code[:6]  # 使用前6位
        else:
            logger.warning(f"无效的HS编码格式: {hs_code}")

    # 添加进口商名称（如果提供）
    if importer:
        # 清理公司名称，去除可能导致问题的特殊格式
        cleaned_name = _clean_company_name(importer)
        params["importer"] = cleaned_name

    # 添加出口商名称（如果提供）
    if exporter:
        # 清理公司名称，去除可能导致问题的特殊格式
        cleaned_name = _clean_company_name(exporter)
        params["exporter"] = cleaned_name

    # 添加原产国代码（如果提供）
    if origin_country:
        # 智能处理：支持中文国家名和三位字母代码
        processed_origin = _process_country_input(origin_country)
        if processed_origin:
            params["countryOfOriginCode"] = processed_origin
        else:
            pass  # 不需要警告，因为这可能是正常的

    # 添加目的国代码（如果提供）
    if destination_country:
        # 智能处理：支持中文国家名和三位字母代码
        processed_destination = _process_country_input(destination_country)
        if processed_destination:
            params["countryOfDestinationCode"] = processed_destination
        else:
            logger.warning(f"无法识别的目的国: {destination_country}")

    return params


def _clean_company_name(company_name: str) -> str:
    """
    清理公司名称格式
    
    功能: 处理公司名称中的特殊格式，去除多余空格和格式化问题
    逻辑: 处理 DBA 格式、去除多余空格等
    
    Args:
        company_name: 原始公司名称
        
    Returns:
        str: 清理后的公司名称
    """
    cleaned_name = company_name
    
    # 处理 "DBA" (Doing Business As) 格式
    if " DBA " in cleaned_name.upper():
        # 提取实际的业务名称，保持原始大小写
        dba_index = cleaned_name.upper().find(" DBA ")
        if dba_index != -1:
            # 使用 DBA 后面的名称（实际业务名）
            cleaned_name = cleaned_name[dba_index + 5:].strip()
    
    # 去除多余的空格
    cleaned_name = " ".join(cleaned_name.split())
    
    return cleaned_name


def _validate_and_process_dates(start_date: str, end_date: str) -> tuple[str, str]:
    """
    验证和处理日期参数
    
    功能: 验证日期格式、逻辑合理性，并返回处理后的日期
    逻辑:
    1. 检查日期格式是否为 YYYY-MM-DD
    2. 验证日期的有效性（如是否存在该日期）
    3. 检查 start_date 是否在 end_date 之前
    4. 检查 end_date 是否不超过今天
    5. 返回验证通过的日期字符串
    
    Args:
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
        
    Returns:
        tuple[str, str]: (验证后的开始日期, 验证后的结束日期)
        
    Raises:
        ValueError: 日期格式错误或逻辑不合理时
    """
    from datetime import datetime, date
    
    # 日期格式正则表达式
    import re
    date_pattern = r'^\d{4}-\d{2}-\d{2}$'
    
    # 1. 检查格式
    if not re.match(date_pattern, start_date):
        raise ValueError(f"开始日期格式错误，应为 YYYY-MM-DD 格式，实际输入: {start_date}")
    
    if not re.match(date_pattern, end_date):
        raise ValueError(f"结束日期格式错误，应为 YYYY-MM-DD 格式，实际输入: {end_date}")
    
    # 2. 验证日期有效性
    try:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
    except ValueError as e:
        raise ValueError(f"开始日期无效: {start_date} ({str(e)})")
    
    try:
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError as e:
        raise ValueError(f"结束日期无效: {end_date} ({str(e)})")
    
    # 3. 检查开始日期是否在结束日期之前
    if start_date_obj > end_date_obj:
        raise ValueError(f"开始日期 ({start_date}) 不能晚于结束日期 ({end_date})")
    
    # 4. 检查结束日期是否不超过今天
    today = date.today()
    if end_date_obj > today:
        raise ValueError(f"结束日期 ({end_date}) 不能超过今天 ({today.strftime('%Y-%m-%d')})")
    
    # 5. 返回验证通过的日期
    return start_date, end_date


def _process_country_input(country_input: str) -> Optional[str]:
    """
    处理国家输入，支持中文名和三位字母代码
    
    功能: 智能识别输入的国家信息，统一转换为三位字母代码
    逻辑:
    1. 如果输入已经是三位字母代码，直接返回（验证格式）
    2. 如果输入是中文国家名，使用转换函数获取代码
    3. 支持大小写不敏感的代码输入
    
    Args:
        country_input: 国家输入（中文名或三位字母代码）
        
    Returns:
        Optional[str]: 标准的三位字母国家代码，无法识别则返回 None
    """
    if not country_input or not country_input.strip():
        return None
    
    country_input = country_input.strip()
    
    # 检查是否是三位字母代码格式（只有ASCII字母）
    if len(country_input) == 3 and country_input.isascii() and country_input.isalpha():
        # 转换为大写并验证是否为有效的国家代码
        code = country_input.upper()
        # 简单验证：检查是否在我们的映射表中存在对应的中文名
        # 通过反向查找验证代码的有效性
        if any(mapped_code == code for mapped_code in _get_country_mapping().values()):
            return code
        
        # 如果不在映射表中，但格式正确，仍然接受（可能是我们映射表未包含的国家）
        logger.info(f"接受三位字母代码（未在映射表中）: {code}")
        return code
    
    # 如果不是三位字母格式，尝试作为中文国家名处理
    return _country_name_to_code(country_input)


def _get_country_mapping() -> Dict[str, str]:
    """
    获取完整的国家映射表（用于验证和反向查询）
    
    Returns:
        Dict[str, str]: 中文国家名到三位字母代码的映射
    """
    return {
        # 主要贸易国家
        "中国": "CHN",
        "China": "CHN",  # 英文名称
        "美国": "USA",
        "United States": "USA",  # 英文名称 
        "德国": "DEU",
        "日本": "JPN",
        "英国": "GBR",
        "法国": "FRA",
        "意大利": "ITA",
        "加拿大": "CAN",
        "韩国": "KOR",
        "荷兰": "NLD",
        "比利时": "BEL",
        "西班牙": "ESP",
        "瑞士": "CHE",
        "奥地利": "AUT",
        "瑞典": "SWE",
        "丹麦": "DNK",
        "挪威": "NOR",
        "芬兰": "FIN",
        "俄罗斯": "RUS",
        "澳大利亚": "AUS",
        "新西兰": "NZL",
        "巴西": "BRA",
        "阿根廷": "ARG",
        "墨西哥": "MEX",
        "印度": "IND",
        "新加坡": "SGP",
        "马来西亚": "MYS",
        "泰国": "THA",
        "印度尼西亚": "IDN",
        "菲律宾": "PHL",
        "越南": "VNM",
        "土耳其": "TUR",
        "以色列": "ISR",
        "阿拉伯联合酋长国": "ARE",
        "沙特阿拉伯": "SAU",
        "南非": "ZAF",
        "埃及": "EGY",
        "尼日利亚": "NGA",
        "波兰": "POL",
        "捷克": "CZE",
        "匈牙利": "HUN",
        "罗马尼亚": "ROU",
        "希腊": "GRC",
        "葡萄牙": "PRT",
        "爱尔兰": "IRL",
        "智利": "CHL",
        "秘鲁": "PER",
        "哥伦比亚": "COL",
        "乌克兰": "UKR",
        "白俄罗斯": "BLR",
        "哈萨克斯坦": "KAZ",
        "巴基斯坦": "PAK",
        "孟加拉国": "BGD",
        "斯里兰卡": "LKA",
        "缅甸": "MMR",
        "柬埔寨": "KHM",
        "老挝": "LAO",
        "文莱": "BRN",
        "蒙古": "MNG",
        "朝鲜": "PRK",
        "摩洛哥": "MAR",
        "阿尔及利亚": "DZA",
        "突尼斯": "TUN",
        "利比亚": "LBY",
        "苏丹": "SDN",
        "埃塞俄比亚": "ETH",
        "肯尼亚": "KEN",
        "坦桑尼亚": "TZA",
        "乌干达": "UGA",
        "加纳": "GHA",
        "象牙海岸": "CIV",
        "塞内加尔": "SEN",
        "马达加斯加": "MDG",
        "毛里求斯": "MUS",
        "塞舌尔": "SYC",
        "约旦": "JOR",
        "黎巴嫩": "LBN",
        "叙利亚": "SYR",
        "伊拉克": "IRQ",
        "伊朗": "IRN",
        "阿富汗": "AFG",
        "乌兹别克斯坦": "UZB",
        "塔吉克斯坦": "TJK",
        "吉尔吉斯斯坦": "KGZ",
        "土库曼斯坦": "TKM",
        "格鲁吉亚": "GEO",
        "亚美尼亚": "ARM",
        "阿塞拜疆": "AZE",
        # 特殊地区和别名
        "台湾": "TWN",
        "香港": "HKG",
        "澳门": "MAC",
        "中国台湾": "TWN",
        "中国香港": "HKG",
        "中国澳门": "MAC",
        # 其他常用别名
        "俄国": "RUS",
    }


def _country_name_to_code(region: str) -> Optional[str]:
    """
    将中文国家名称转换为三位字母国家代码
    
    功能: 提供中文国家名称到 Tendata API 标准三位字母代码的映射
    逻辑: 基于 Tendata 官方国家代码表进行查询匹配
    
    注意: 此函数保留用于未来扩展和向后兼容，当前版本通过 _process_country_input 
          智能处理中文名和三位字母代码
    
    用法示例:
        code = _country_name_to_code("中国")  # 返回 "CHN"
        code = _country_name_to_code("美国")  # 返回 "USA"
        code = _country_name_to_code("德国")  # 返回 "DEU" (支持前缀处理)
    
    Args:
        region: 中文国家名称（如"美国"、"德国"、"中国"等）
        
    Returns:
        Optional[str]: 对应的三位字母国家代码（如"USA"、"DEU"、"CHN"），未找到则返回 None
    """
    # 使用共享的国家映射表
    country_code_map = _get_country_mapping()
    
    # 先尝试精确匹配
    if region in country_code_map:
        return country_code_map[region]
    
    # 如果没有找到，尝试去除常见前缀后匹配
    cleaned_region = region
    prefixes_to_remove = ["共和国", "联邦", "王国", "公国", "大公国", "酋长国"]
    for prefix in prefixes_to_remove:
        if cleaned_region.endswith(prefix):
            cleaned_region = cleaned_region[:-len(prefix)]
            if cleaned_region in country_code_map:
                return country_code_map[cleaned_region]
    
    return None


# 导出函数作为工具
get_trade_data_tool = get_trade_data
get_trade_data_count_tool = get_trade_data_count