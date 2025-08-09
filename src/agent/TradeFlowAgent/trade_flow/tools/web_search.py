"""
Web Search Tool - ADK 规范实现
只支持 Jina Search API，不提供降级方案
"""

from typing import Dict, Any, List, Optional
import os
import httpx
from urllib.parse import quote
from loguru import logger
import asyncio


# 自定义错误类
class SearchError(Exception):
    """搜索错误基类"""

    pass


class ConfigurationError(SearchError):
    """配置错误：缺少必要的配置"""

    pass


class APIError(SearchError):
    """API调用错误：认证、限流等"""

    pass


class NetworkError(SearchError):
    """网络错误：连接失败、超时等"""

    pass


class ParseError(SearchError):
    """解析错误：响应格式异常"""

    pass


def _preprocess_query(query: str) -> str:
    """
    预处理查询字符串，处理可能导致 API 错误的情况
    
    Args:
        query: 原始查询字符串
        
    Returns:
        处理后的查询字符串
    """
    # 去除多余的空格
    query = " ".join(query.split())
    
    # 如果查询包含中英文混合，可能需要特殊处理
    # 检查是否同时包含中文和英文
    has_chinese = any('\u4e00' <= char <= '\u9fff' for char in query)
    has_english = any(char.isalpha() and ord(char) < 128 for char in query)
    
    if has_chinese and has_english:
        # 如果是中英文混合，考虑只保留主要语言部分
        # 或者添加引号来明确搜索意图
        # 这里暂时保持原样，但记录警告
        logger.warning(f"查询包含中英文混合，可能影响搜索结果: {query}")
    
    # 限制查询长度（Jina API 可能对长查询有限制）
    max_length = 200  # 根据经验设置的合理长度
    if len(query) > max_length:
        query = query[:max_length].strip()
        logger.warning(f"查询过长，已截断至 {max_length} 字符")
    
    # 移除可能导致问题的特殊字符（保留基本的标点符号）
    # 保留中文、英文、数字、空格和常见标点
    import re
    query = re.sub(r'[^\u4e00-\u9fff\w\s\-.,，。、]', ' ', query, flags=re.UNICODE)
    query = " ".join(query.split())  # 再次清理空格
    
    return query


async def web_search(
    query: str,
    num_results: int = 10,
    language: str = "zh-CN",
    region: str = "cn",
    sites: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    执行网页搜索，使用 Jina Search API

    如果出现任何错误，将主动抛出异常，不进行降级处理

    Args:
        query: 搜索关键词
        num_results: 返回结果数量（默认10个）
        language: 搜索语言（默认中文）
        region: 搜索地区（默认中国）
        sites: 限定搜索的网站列表（可选）

    Returns:
        搜索结果字典

    Raises:
        ConfigurationError: 缺少必要的API配置
        APIError: API调用相关错误
        NetworkError: 网络连接错误
        ParseError: 响应解析错误
    """
    # 检查 Jina API key 配置
    jina_api_key = os.getenv("JINA_API_KEY")

    if not jina_api_key or jina_api_key == "your-jina-api-key":
        raise ConfigurationError(
            "缺少 JINA_API_KEY 配置。\n"
            "请按以下步骤配置：\n"
            "1. 访问 https://jina.ai 获取 API Key\n"
            "2. 设置环境变量：export JINA_API_KEY='your-actual-api-key'\n"
            "3. 或在 .env 文件中添加：JINA_API_KEY=your-actual-api-key"
        )

    # 记录搜索请求
    logger.info(f"使用 Jina Search API 搜索: '{query}'")

    try:
        # 调用 Jina API，包含重试机制
        return await _jina_search_with_retry(
            query=query, num_results=num_results, sites=sites, api_key=jina_api_key
        )
    except SearchError:
        # 直接抛出自定义错误
        raise
    except Exception as e:
        # 包装未预期的错误
        logger.error(f"搜索过程中出现未预期错误: {str(e)}")
        raise SearchError(f"搜索失败: {str(e)}")


async def _jina_search_with_retry(
    query: str,
    num_results: int,
    sites: Optional[List[str]],
    api_key: str,
    max_retries: int = 3,
    retry_delay: float = 1.0,
) -> Dict[str, Any]:
    """
    带重试机制的 Jina Search API 调用

    使用指数退避策略，对临时性错误进行重试
    """
    last_error = None

    for attempt in range(max_retries):
        try:
            return await _jina_search(
                query=query, num_results=num_results, sites=sites, api_key=api_key
            )
        except (NetworkError, httpx.TimeoutException) as e:
            # 网络错误和超时可以重试
            last_error = e
            if attempt < max_retries - 1:
                delay = retry_delay * (2**attempt)  # 指数退避
                logger.warning(
                    f"搜索请求失败 (尝试 {attempt + 1}/{max_retries})，"
                    f"{delay}秒后重试: {str(e)}"
                )
                await asyncio.sleep(delay)
            else:
                logger.error(f"搜索请求在 {max_retries} 次尝试后仍然失败")
        except Exception:
            # 其他错误不重试，直接抛出
            raise

    # 所有重试都失败了
    if isinstance(last_error, NetworkError):
        raise last_error
    else:
        raise NetworkError(f"网络请求在 {max_retries} 次尝试后失败: {str(last_error)}")


async def _jina_search(
    query: str, num_results: int, sites: Optional[List[str]], api_key: str
) -> Dict[str, Any]:
    """
    使用 Jina Search API 进行搜索

    文档: https://github.com/jina-ai/reader
    """
    # 预处理查询字符串
    processed_query = _preprocess_query(query)
    
    # 构建 URL - 使用 safe='' 确保所有字符都被编码
    encoded_query = quote(processed_query, safe='')
    base_url = f"https://s.jina.ai/{encoded_query}"
    
    # 记录查询信息用于调试
    logger.debug(f"Jina API 查询: 原始='{query}', 处理后='{processed_query}', 编码后='{encoded_query}'")

    # 添加站点筛选参数
    params = {}
    if sites:
        # Jina Search 支持多个 site 参数
        params = {"site": sites}

    results: List[Dict[str, str]] = []

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # 构建请求头
            headers = {
                "Accept": "text/plain",
                "User-Agent": "TradeFlowAgent/1.0",
                "Authorization": f"Bearer {api_key}",
            }

            # 发送请求
            response = await client.get(base_url, params=params, headers=headers)

            # 处理响应状态
            if response.status_code == 200:
                # 成功响应
                content = response.text
                results = _parse_jina_response(content, num_results)
            elif response.status_code == 401:
                raise APIError(
                    "Jina API 认证失败。\n"
                    "请检查您的 API Key 是否正确。\n"
                    "如需新的 API Key，请访问: https://jina.ai"
                )
            elif response.status_code == 422:
                # 处理 422 错误 - 通常是查询格式问题
                error_detail = response.text[:500]
                if "No search results available" in error_detail:
                    # 没有搜索结果，返回空结果而不是报错
                    logger.warning(f"Jina API 未找到结果: {processed_query}")
                    results = []
                else:
                    raise APIError(
                        f"Jina API 无法处理查询 (状态码: 422)。\n"
                        f"查询: {processed_query}\n"
                        f"可能的原因：\n"
                        "1. 查询格式不正确\n"
                        "2. 查询包含不支持的字符\n"
                        "3. 查询过于复杂\n"
                        f"错误详情: {error_detail}"
                    )
            elif response.status_code == 429:
                raise APIError(
                    "Jina API 请求频率限制。\n"
                    "请稍后再试，或升级您的 API 计划以获得更高的配额。"
                )
            elif response.status_code >= 500:
                raise APIError(
                    f"Jina API 服务器错误 ({response.status_code})。\n"
                    "这是服务端的临时问题，请稍后再试。"
                )
            else:
                error_detail = response.text[:200]
                raise APIError(
                    f"Jina API 请求失败 (状态码: {response.status_code})。\n"
                    f"错误详情: {error_detail}"
                )

        except httpx.TimeoutException:
            raise NetworkError(
                "Jina API 请求超时。\n"
                "可能的原因：\n"
                "1. 网络连接不稳定\n"
                "2. Jina 服务响应缓慢\n"
                "请检查网络连接并稍后重试。"
            )
        except httpx.RequestError as e:
            raise NetworkError(
                f"网络请求失败: {str(e)}\n"
                "请检查：\n"
                "1. 网络连接是否正常\n"
                "2. 是否可以访问 https://jina.ai\n"
                "3. 防火墙或代理设置"
            )

    # 验证解析结果
    if not results:
        logger.warning(f"Jina API 返回了空结果，查询: '{query}'")
        # 返回空结果而不是抛出错误，因为这可能是合法的搜索结果

    # 计算质量评估指标
    quality_score = _evaluate_search_quality(results, query)

    return {
        "status": "success",
        "query": query,
        "results": results,
        "total": len(results),
        "source": "jina_api",
        "quality_metrics": {
            "score": quality_score,
            "result_count": len(results),
            "confidence": (
                "high"
                if quality_score > 0.8
                else "medium" if quality_score > 0.5 else "low"
            ),
            "source_diversity": _calculate_source_diversity(results),
            "relevance_estimate": (
                "high"
                if len(results) >= 5
                else "medium" if len(results) >= 2 else "low"
            ),
        },
    }


def _parse_jina_response(content: str, num_results: int) -> List[Dict[str, str]]:
    """
    解析 Jina Search 返回的内容

    Jina Search 返回格式：
    [n] Title: 标题
    [n] URL Source: URL
    [n] Description: 描述
    [n] Date: 日期（可选）

    Args:
        content: Jina 返回的内容
        num_results: 需要的结果数量

    Returns:
        解析后的搜索结果列表

    Raises:
        ParseError: 解析失败时抛出
    """
    try:
        results: List[Dict[str, str]] = []
        lines = content.split("\n")

        current_result: Dict[str, str] = {}
        current_index = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 检查是否是新的结果项标记 [n] Title:
            if line.startswith("[") and "] Title:" in line:
                # 保存之前的结果
                if current_result and "title" in current_result:
                    results.append(current_result)
                    if len(results) >= num_results:
                        break

                # 开始新的结果
                bracket_end = line.find("]")
                if bracket_end > 0:
                    try:
                        current_index = int(line[1:bracket_end])
                        title = line[line.find("] Title:") + 8:].strip()
                        current_result = {
                            "title": title,
                            "url": "",
                            "snippet": "",
                            "displayLink": "",
                        }
                    except ValueError:
                        continue

            # 检查是否是 URL 行
            elif current_index and line.startswith(f"[{current_index}] URL Source:"):
                url = line[line.find("] URL Source:") + 13:].strip()
                current_result["url"] = url
                # 从 URL 提取域名
                if url.startswith("http"):
                    try:
                        domain_start = url.find("://") + 3
                        domain_end = url.find("/", domain_start)
                        if domain_end == -1:
                            domain_end = len(url)
                        display_link = url[domain_start:domain_end]
                        current_result["displayLink"] = display_link
                    except Exception:
                        current_result["displayLink"] = "unknown"

            # 检查是否是描述行
            elif current_index and line.startswith(f"[{current_index}] Description:"):
                description = line[line.find("] Description:") + 14:].strip()
                current_result["snippet"] = description

        # 保存最后一个结果
        if current_result and "title" in current_result:
            results.append(current_result)

        # 如果没有解析到任何结果，可能是格式变化
        if not results and content.strip():
            # 尝试备用解析方法
            logger.warning("Jina 响应格式可能已变化，尝试备用解析方法")
            results = _parse_jina_response_fallback(content, num_results)

        return results[:num_results]

    except Exception as e:
        logger.error(f"解析 Jina 响应时出错: {str(e)}")
        raise ParseError(
            f"无法解析 Jina Search 响应。\n"
            f"错误: {str(e)}\n"
            f"响应预览: {content[:200]}..."
        )


def _parse_jina_response_fallback(
    content: str, num_results: int
) -> List[Dict[str, str]]:
    """
    备用的 Jina 响应解析方法

    用于处理格式变化或特殊情况
    """
    results: List[Dict[str, str]] = []

    # 简单的行匹配方法
    lines = content.split("\n")
    for i, line in enumerate(lines):
        if "Title:" in line and len(results) < num_results:
            title_start = line.find("Title:") + 6
            title = line[title_start:].strip()

            # 尝试在接下来的几行找 URL
            url = ""
            snippet = ""
            for j in range(i + 1, min(i + 5, len(lines))):
                if "URL" in lines[j] or "http" in lines[j]:
                    url_line = lines[j]
                    # 提取 URL
                    import re

                    url_match = re.search(r"https?://[^\s]+", url_line)
                    if url_match:
                        url = url_match.group(0)
                        break

            if title:
                results.append(
                    {
                        "title": title,
                        "url": url or f"https://s.jina.ai/search?q={quote(title[:50])}",
                        "snippet": snippet or "Jina Search 结果",
                        "displayLink": "jina.ai" if not url else url.split("/")[2],
                    }
                )

    return results


def _evaluate_search_quality(results: List[Dict[str, str]], query: str) -> float:
    """
    评估搜索结果质量（供系统级ReAct观察使用）

    Args:
        results: 搜索结果列表
        query: 原始查询

    Returns:
        质量得分 (0.0-1.0)
    """
    if not results:
        return 0.0

    score = 0.0

    # 1. 结果数量评分 (0.3权重)
    result_count = len(results)
    count_score = min(result_count / 8, 1.0)  # 8个结果得满分
    score += count_score * 0.3

    # 2. 标题完整性评分 (0.2权重)
    valid_titles = sum(
        1 for r in results if r.get("title") and len(r["title"].strip()) > 10
    )
    title_score = valid_titles / len(results) if results else 0
    score += title_score * 0.2

    # 3. 描述质量评分 (0.3权重)
    valid_snippets = sum(
        1 for r in results if r.get("snippet") and len(r["snippet"].strip()) > 20
    )
    snippet_score = valid_snippets / len(results) if results else 0
    score += snippet_score * 0.3

    # 4. URL有效性评分 (0.2权重)
    valid_urls = sum(1 for r in results if r.get("url") and r["url"].startswith("http"))
    url_score = valid_urls / len(results) if results else 0
    score += url_score * 0.2

    return min(score, 1.0)


def _calculate_source_diversity(results: List[Dict[str, str]]) -> float:
    """
    计算搜索结果来源多样性

    Returns:
        多样性得分 (0.0-1.0)
    """
    if not results:
        return 0.0

    # 提取域名
    domains = set()
    for result in results:
        display_link = result.get("displayLink", "")
        if display_link and display_link != "unknown":
            domains.add(display_link)
        elif result.get("url", "").startswith("http"):
            try:
                # 从 URL 提取域名作为备用
                url = result["url"]
                domain = url.split("//")[1].split("/")[0]
                domains.add(domain)
            except Exception:
                pass

    # 多样性得分：不同域名数 / 结果总数
    return min(len(domains) / len(results), 1.0) if results else 0.0


# 导出函数作为工具
web_search_tool = web_search
