"""
Jina Reader Tool - 网页内容提取工具
支持普通网页、SPA 应用和 Hash 路由的内容提取
"""

from typing import Dict, Any, Optional, List
import os
import httpx
from urllib.parse import quote, urlparse
from loguru import logger


async def browse_webpage(
    url: str,
    wait_for_selector: Optional[str] = None,
    timeout: Optional[int] = None,
    extract_type: str = "content",
    use_post: bool = False,
) -> Dict[str, Any]:
    """
    浏览网页并提取内容

    Args:
        url: 目标 URL
        wait_for_selector: 等待特定 CSS 选择器出现（用于 SPA）
        timeout: 等待超时时间（秒）
        extract_type: 提取类型 (content, summary, structured)
        use_post: 是否使用 POST 方法（用于 Hash 路由）

    Returns:
        网页内容提取结果
    """
    try:
        return await _jina_reader_api(url, wait_for_selector, timeout, extract_type, use_post)
    except Exception as e:
        logger.error(f"网页浏览API调用失败: {str(e)}")
        return {
            "status": "error",
            "url": url,
            "title": "网页内容提取失败",
            "content": "",
            "extracted_info": {
                "type": extract_type,
                "summary": "",
                "key_points": [],
                "entities": {},
                "links": [],
            },
            "content_length": 0,
            "source": "error",
            "error": f"网页内容提取失败: {str(e)}",
        }


async def _jina_reader_api(
    url: str,
    wait_for_selector: Optional[str],
    timeout: Optional[int],
    extract_type: str,
    use_post: bool,
) -> Dict[str, Any]:
    """
    调用 Jina Reader API 提取网页内容
    """
    base_url = "https://r.jina.ai"

    # 构建请求头
    headers = {
        "Accept": "text/plain",
        "User-Agent": "TradeFlowAgent/1.0",
    }

    # 添加特殊头部
    if wait_for_selector:
        headers["x-wait-for-selector"] = wait_for_selector

    if timeout:
        headers["x-timeout"] = str(timeout)

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            if use_post:
                # 使用 POST 方法（用于 Hash 路由）
                response = await client.post(base_url, data={"url": url}, headers=headers)
            else:
                # 使用 GET 方法（普通网页）
                full_url = f"{base_url}/{url}"
                response = await client.get(full_url, headers=headers)

            response.raise_for_status()
            content = response.text

            # 解析提取的内容
            return _parse_jina_reader_response(url, content, extract_type)

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise Exception("请求频率限制")
            elif e.response.status_code == 404:
                raise Exception(f"无法访问 URL: {url}")
            else:
                error_text = e.response.text[:200] if e.response.text else ""
                raise Exception(f"API 请求失败: {e.response.status_code} - {error_text}")
        except Exception as e:
            raise Exception(f"网页内容提取异常: {str(e)}")


def _parse_jina_reader_response(url: str, content: str, extract_type: str) -> Dict[str, Any]:
    """
    解析 Jina Reader 返回的内容

    Args:
        url: 原始 URL
        content: Jina Reader 返回的 markdown 内容
        extract_type: 提取类型

    Returns:
        解析后的结果
    """
    lines = content.split("\n")

    # 提取基本信息
    title = ""
    url_source = ""
    main_content = []

    capture_content = False

    for line in lines:
        line = line.strip()

        # 提取标题
        if line.startswith("Title:"):
            title = line[6:].strip()

        # 提取 URL 来源
        elif line.startswith("URL Source:"):
            url_source = line[11:].strip()

        # 开始捕获主要内容
        elif line.startswith("Markdown Content:"):
            capture_content = True
            continue

        # 捕获内容
        elif capture_content and line:
            main_content.append(line)

    # 合并内容
    content_text = "\n".join(main_content)

    # 根据提取类型处理内容
    extracted_info = _extract_structured_info(content_text, extract_type)

    return {
        "status": "success",
        "url": url_source or url,
        "title": title,
        "content": content_text,
        "extracted_info": extracted_info,
        "content_length": len(content_text),
        "source": "jina_reader",
    }


def _extract_structured_info(content: str, extract_type: str) -> Dict[str, Any]:
    """
    从内容中提取结构化信息

    Args:
        content: 网页内容文本
        extract_type: 提取类型

    Returns:
        结构化信息
    """
    extracted = {
        "type": extract_type,
        "summary": "",
        "key_points": [],
        "entities": {},
        "links": [],
    }

    if not content:
        return extracted

    # 生成摘要（取前200字）
    extracted["summary"] = content[:200] + "..." if len(content) > 200 else content

    # 提取链接
    import re

    link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"
    links = re.findall(link_pattern, content)
    extracted["links"] = [{"text": text, "url": url} for text, url in links]

    # 根据提取类型进行特定处理
    if extract_type == "structured":
        extracted.update(_extract_trade_info(content))
    elif extract_type == "summary":
        extracted["key_points"] = _extract_key_points(content)

    return extracted


def _extract_trade_info(content: str) -> Dict[str, Any]:
    """
    提取贸易相关信息

    Args:
        content: 网页内容

    Returns:
        贸易信息字典
    """
    trade_info = {
        "companies": [],
        "products": [],
        "prices": [],
        "contacts": [],
        "trade_terms": [],
    }

    # 简单的关键词匹配（实际应用中可能需要更复杂的 NLP）
    content_lower = content.lower()

    # 提取公司信息
    company_keywords = [
        "company",
        "corporation",
        "ltd",
        "inc",
        "co.",
        "企业",
        "公司",
        "集团",
    ]
    for keyword in company_keywords:
        if keyword in content_lower:
            # 这里可以实现更复杂的公司名提取逻辑
            pass

    # 提取产品信息
    product_keywords = ["product", "goods", "merchandise", "产品", "商品", "货物"]
    for keyword in product_keywords:
        if keyword in content_lower:
            # 这里可以实现更复杂的产品信息提取逻辑
            pass

    # 提取价格信息
    import re

    price_patterns = [
        r"\$[\d,]+\.?\d*",  # 美元
        r"¥[\d,]+\.?\d*",  # 人民币
        r"€[\d,]+\.?\d*",  # 欧元
        r"[\d,]+\.?\d*\s*USD",  # USD
        r"[\d,]+\.?\d*\s*CNY",  # CNY
    ]

    for pattern in price_patterns:
        matches = re.findall(pattern, content)
        trade_info["prices"].extend(matches)

    # 提取联系信息
    contact_patterns = [
        r"[\w\.-]+@[\w\.-]+\.\w+",  # 邮箱
        r"\+?[\d\s\-\(\)]{10,}",  # 电话
    ]

    for pattern in contact_patterns:
        matches = re.findall(pattern, content)
        trade_info["contacts"].extend(matches)

    return trade_info


def _extract_key_points(content: str) -> List[str]:
    """
    提取关键要点

    Args:
        content: 内容文本

    Returns:
        关键要点列表
    """
    # 按段落分割
    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]

    # 选择前几个段落作为关键要点
    key_points = []
    for paragraph in paragraphs[:5]:  # 最多5个要点
        if len(paragraph) > 20:  # 过滤太短的段落
            # 限制每个要点的长度
            point = paragraph[:150] + "..." if len(paragraph) > 150 else paragraph
            key_points.append(point)

    return key_points


# 导出函数作为工具
browse_webpage_tool = browse_webpage

# 向后兼容的别名
jina_reader_tool = browse_webpage
jina_reader = browse_webpage
