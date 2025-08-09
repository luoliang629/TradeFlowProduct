"""
Company Trade Profile Tool - 公司贸易档案工具
整合公司基本信息和海关贸易数据，生成完整的公司贸易画像
"""

from typing import Dict, Any, Optional, List
import asyncio
from datetime import datetime, timedelta
import logging

# 配置日志
logger = logging.getLogger(__name__)


async def company_trade_profile(
    company_name: str,
    analysis_period: int = 6,  # 默认分析最近6个月
    include_competitors: bool = True,
) -> Dict[str, Any]:
    """
    生成公司贸易档案

    Args:
        company_name: 公司名称
        analysis_period: 分析周期（月）
        include_competitors: 是否包含竞争对手分析

    Returns:
        完整的公司贸易档案
    """
    try:
        # 并行获取多个数据源
        tasks = []

        # 1. 获取公司基本信息
        from trade_flow.tools.company_info import company_info

        tasks.append(company_info(company_name=company_name, limit=1))

        # 2. 获取海关贸易数据
        from trade_flow.tools.trade_data_query import customs_query

        end_date = datetime.now().strftime("%Y-%m")
        start_date = (datetime.now() - timedelta(days=30 * analysis_period)).strftime("%Y-%m")
        tasks.append(
            customs_query(company_name=company_name, start_date=start_date, end_date=end_date, trade_type="both")
        )

        # 3. 搜索公司相关新闻和动态
        from trade_flow.tools.web_search import web_search

        tasks.append(web_search(f"{company_name} 贸易 出口 新闻", num_results=5))

        # 执行所有任务
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 处理结果
        company_info_result = results[0] if not isinstance(results[0], Exception) else None
        customs_data_result = results[1] if not isinstance(results[1], Exception) else None
        news_result = results[2] if not isinstance(results[2], Exception) else None

        # 构建贸易档案
        profile = {
            "company_name": company_name,
            "analysis_period": f"最近{analysis_period}个月",
            "generated_at": datetime.now().isoformat(),
            "status": "success",
        }

        # 1. 公司基本信息
        if company_info_result and company_info_result["status"] == "success":
            companies = company_info_result.get("companies", [])
            if companies:
                company_data = companies[0]
                profile["basic_info"] = company_data.get("basic_info", {})
                profile["contact_info"] = company_data.get("trade_info", {}).get("contact_info", {})
        else:
            profile["basic_info"] = {"error": "未能获取公司基本信息"}

        # 2. 贸易数据分析
        if customs_data_result and customs_data_result["status"] == "success":
            profile["trade_analysis"] = _analyze_trade_data(customs_data_result)
        else:
            profile["trade_analysis"] = {"error": "未能获取海关贸易数据"}

        # 3. 市场动态
        if news_result and news_result["status"] == "success":
            profile["market_updates"] = _extract_market_updates(news_result)
        else:
            profile["market_updates"] = []

        # 4. 生成综合评估
        profile["comprehensive_assessment"] = _generate_assessment(profile)

        # 5. 竞争对手分析（如果需要）
        if include_competitors and customs_data_result:
            profile["competitor_analysis"] = await _analyze_competitors(customs_data_result, company_name)

        return profile

    except Exception as e:
        logger.error(f"生成公司贸易档案失败: {str(e)}")
        return {"status": "error", "error_message": f"生成贸易档案失败: {str(e)}", "company_name": company_name}


def _analyze_trade_data(customs_data: Dict[str, Any]) -> Dict[str, Any]:
    """分析海关贸易数据"""
    analysis = {
        "total_records": customs_data.get("query_params", {}).get("total_records", 0),
        "date_range": {
            "start": customs_data.get("query_params", {}).get("start_date"),
            "end": customs_data.get("query_params", {}).get("end_date"),
        },
    }

    # 提取数据摘要
    data_summary = customs_data.get("data_summary", {})

    # 进出口分析
    if "export" in data_summary:
        export_data = data_summary["export"]
        analysis["export_analysis"] = {
            "total_value_million_usd": export_data.get("total_value", 0),
            "main_destinations": export_data.get("top_destinations", []),
        }

    if "import" in data_summary:
        import_data = data_summary["import"]
        analysis["import_analysis"] = {
            "total_value_million_usd": import_data.get("total_value", 0),
            "main_sources": import_data.get("top_sources", []),
        }

    # 贸易趋势
    trends = customs_data.get("trends", [])
    if trends:
        analysis["trade_trends"] = _analyze_trends(trends)

    # 贸易伙伴
    if "top_companies" in data_summary:
        analysis["trade_partners"] = data_summary["top_companies"]

    return analysis


def _analyze_trends(trends: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析贸易趋势"""
    if not trends:
        return {}

    # 计算月度平均值和增长率
    export_values = []
    import_values = []

    for trend in trends:
        if "export_value" in trend:
            export_values.append(float(trend["export_value"]))
        if "import_value" in trend:
            import_values.append(float(trend["import_value"]))

    trend_analysis = {}

    if export_values:
        trend_analysis["export"] = {
            "average_monthly_value": round(sum(export_values) / len(export_values), 2),
            "growth_rate": _calculate_growth_rate(export_values),
            "trend": _determine_trend(export_values),
        }

    if import_values:
        trend_analysis["import"] = {
            "average_monthly_value": round(sum(import_values) / len(import_values), 2),
            "growth_rate": _calculate_growth_rate(import_values),
            "trend": _determine_trend(import_values),
        }

    return trend_analysis


def _calculate_growth_rate(values: List[float]) -> float:
    """计算增长率"""
    if len(values) < 2:
        return 0.0

    # 比较第一个月和最后一个月
    if values[0] == 0:
        return 0.0

    growth_rate = ((values[-1] - values[0]) / values[0]) * 100
    return round(growth_rate, 1)


def _determine_trend(values: List[float]) -> str:
    """判断趋势方向"""
    if len(values) < 2:
        return "稳定"

    # 简单的趋势判断
    growth_rate = _calculate_growth_rate(values)

    if growth_rate > 10:
        return "上升"
    elif growth_rate < -10:
        return "下降"
    else:
        return "稳定"


def _extract_market_updates(news_result: Dict[str, Any]) -> List[Dict[str, str]]:
    """提取市场动态信息"""
    updates = []

    results = news_result.get("results", [])
    for result in results[:3]:  # 只取前3条
        updates.append(
            {
                "title": result.get("title", ""),
                "summary": result.get("snippet", ""),
                "url": result.get("url", ""),
                "source": result.get("source", ""),
            }
        )

    return updates


def _generate_assessment(profile: Dict[str, Any]) -> Dict[str, Any]:
    """生成综合评估"""
    assessment = {"overall_rating": "待评估", "strengths": [], "risks": [], "recommendations": []}

    # 基于贸易数据的评估
    trade_analysis = profile.get("trade_analysis", {})

    # 评估贸易规模
    total_records = trade_analysis.get("total_records", 0)
    if total_records > 100:
        assessment["strengths"].append("贸易活动频繁，市场活跃度高")
        assessment["overall_rating"] = "活跃"
    elif total_records > 50:
        assessment["strengths"].append("贸易活动稳定")
        assessment["overall_rating"] = "稳定"
    else:
        assessment["risks"].append("贸易活动较少，需要扩大市场")
        assessment["overall_rating"] = "待发展"

    # 评估贸易趋势
    trends = trade_analysis.get("trade_trends", {})
    if trends:
        export_trend = trends.get("export", {})
        if export_trend.get("trend") == "上升":
            assessment["strengths"].append("出口业务呈增长趋势")
        elif export_trend.get("trend") == "下降":
            assessment["risks"].append("出口业务有下滑趋势，需要关注")

    # 生成建议
    if assessment["risks"]:
        assessment["recommendations"].append("建议制定风险应对策略")

    if total_records < 50:
        assessment["recommendations"].append("建议拓展更多贸易伙伴")

    return assessment


async def _analyze_competitors(customs_data: Dict[str, Any], target_company: str) -> Dict[str, Any]:
    """分析竞争对手"""
    competitor_analysis = {"main_competitors": [], "market_comparison": {}}

    # 从海关数据中提取其他公司
    top_companies = customs_data.get("data_summary", {}).get("top_companies", [])

    competitors = []
    for company in top_companies:
        if company["name"] != target_company:
            competitors.append(
                {
                    "name": company["name"],
                    "trade_value_million_usd": company["total_value"],
                    "trade_type": company["type"],
                    "records_count": company["records_count"],
                }
            )

    competitor_analysis["main_competitors"] = competitors[:3]  # 前3个竞争对手

    # 市场份额对比
    if competitors:
        total_value = sum(c["trade_value_million_usd"] for c in competitors)
        target_value = next((c["total_value"] for c in top_companies if c["name"] == target_company), 0)

        if total_value + target_value > 0:
            competitor_analysis["market_comparison"] = {
                "target_company_share": round(target_value / (total_value + target_value) * 100, 1),
                "market_position": _determine_market_position(target_value, total_value),
            }

    return competitor_analysis


def _determine_market_position(company_value: float, total_competitor_value: float) -> str:
    """判断市场地位"""
    if company_value == 0:
        return "新进入者"

    share = company_value / (company_value + total_competitor_value)

    if share > 0.3:
        return "市场领导者"
    elif share > 0.15:
        return "主要参与者"
    elif share > 0.05:
        return "一般参与者"
    else:
        return "小型参与者"


# 导出函数作为工具
company_trade_profile_tool = company_trade_profile
