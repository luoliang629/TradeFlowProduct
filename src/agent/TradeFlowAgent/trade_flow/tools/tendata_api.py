"""
Tendata API 公用方法
抽象出 customs_query.py 和 company_query.py 中的公用 API 调用逻辑
"""

from typing import Dict, Any, Optional
import logging
from trade_flow.config import (
    TENDATA_API_KEY,
    TENDATA_API_BASE_URL,
)
from trade_flow.tools.tendata_auth import TendataAuth, RateLimiter

logger = logging.getLogger(__name__)

# 全局认证和限流器实例
_tendata_auth: Optional[TendataAuth] = None
_rate_limiter = RateLimiter(max_requests=200, window_seconds=60)


def get_tendata_auth() -> Optional[TendataAuth]:
    """
    获取 Tendata 认证实例
    
    功能: 初始化并返回全局的 Tendata API 认证实例，采用单例模式
    
    Returns:
        Optional[TendataAuth]: 认证实例，如果未配置 API key 则返回 None
    """
    global _tendata_auth
    if _tendata_auth is None and TENDATA_API_KEY:
        _tendata_auth = TendataAuth(TENDATA_API_KEY, TENDATA_API_BASE_URL)
    return _tendata_auth


async def make_tendata_request(
    method: str,
    endpoint: str,
    params: Optional[Dict[str, Any]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    rate_limit: bool = True
) -> Dict[str, Any]:
    """
    发起 Tendata API 请求的通用方法
    
    功能: 统一处理 Tendata API 请求，包括认证、限流、错误处理
    逻辑:
    1. 获取认证实例
    2. 应用速率限制（如果启用）
    3. 发起 API 请求
    4. 处理响应和错误
    
    Args:
        method: HTTP 方法 ("GET", "POST", etc.)
        endpoint: API 端点路径 (如 "/v2/company/list")
        params: URL 查询参数（用于 GET 请求）
        json_data: JSON 请求体数据（用于 POST 请求）
        rate_limit: 是否应用速率限制，默认 True
        
    Returns:
        Dict[str, Any]: API 响应数据
        
    Raises:
        Exception: API 调用失败时抛出异常
    """
    # 获取认证实例
    auth = get_tendata_auth()
    if not auth:
        raise Exception("Tendata API 未配置，请设置 TENDATA_API_KEY")
    
    # 应用速率限制
    if rate_limit:
        await _rate_limiter.acquire()
    
    # 记录请求信息
    logger.info(f"Tendata API 请求: {method} {endpoint}\n")
    if params:
        logger.info(f"查询参数: {params}\n")
    if json_data:
        logger.info(f"请求数据: {json_data}\n")
    
    try:
        # 发起请求
        if method.upper() == "GET":
            response = await auth.make_authenticated_request(
                method, endpoint, params=params
            )
        else:
            response = await auth.make_authenticated_request(
                method, endpoint, json=json_data, params=params
            )
                
        # 记录响应
        logger.info(f"Tendata API 响应状态: 成功\n")
        # logger.info(f"Tendata API 返回: {response}")
        
        return response
        
    except Exception as e:
        logger.error(f"Tendata API 请求失败: {method} {endpoint}, 错误: {str(e)}")
        raise


def validate_api_response(response: Dict[str, Any], operation: str) -> Dict[str, Any]:
    """
    验证 Tendata API 响应格式
    
    功能: 统一验证 API 响应的有效性，确保包含必要的数据结构
    逻辑:
    1. 检查响应是否包含 'data' 字段
    2. 验证数据结构的完整性
    3. 返回标准化的结果格式
    
    Args:
        response: Tendata API 原始响应
        operation: 操作描述（用于错误日志）
        
    Returns:
        Dict[str, Any]: 标准化的响应数据
        
    Raises:
        ValueError: 响应格式无效时
    """
    if not isinstance(response, dict):
        raise ValueError(f"{operation} API 响应格式错误：不是有效的 JSON 对象")
    
    if "data" not in response:
        raise ValueError(f"{operation} API 响应格式错误：缺少 'data' 字段")
    
    data = response.get("data", {})
    
    # 记录数据统计
    if isinstance(data, dict):
        if "total" in data:
            logger.info(f"{operation} - 找到 {data.get('total', 0)} 条记录")
        elif "records" in data:
            records_count = len(data.get("records", []))
            logger.info(f"{operation} - 返回 {records_count} 条记录")
        elif "content" in data:
            content_count = len(data.get("content", []))
            logger.info(f"{operation} - 返回 {content_count} 条记录")
    
    return response


def create_error_response(error_message: str, query_params: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    创建标准化的错误响应
    
    功能: 为 API 调用失败创建统一格式的错误响应
    
    Args:
        error_message: 错误消息
        query_params: 查询参数（可选，用于调试）
        
    Returns:
        Dict[str, Any]: 标准化的错误响应
    """
    error_response = {
        "status": "error",
        "error_message": error_message
    }
    
    if query_params:
        error_response["query_params"] = query_params
    
    return error_response


def create_success_response(data: Any, query_params: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    创建标准化的成功响应
    
    功能: 为 API 调用成功创建统一格式的响应
    
    Args:
        data: 响应数据
        query_params: 查询参数（可选，用于记录）
        
    Returns:
        Dict[str, Any]: 标准化的成功响应
    """
    success_response = {
        "status": "success",
        "data": data
    }
    
    if query_params:
        success_response["query_params"] = query_params
    
    return success_response