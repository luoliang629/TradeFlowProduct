"""
Artifacts 读取工具

提供独立的工具供智能体读取已保存的贸易数据 Artifacts
"""

import logging
from typing import Dict, Any, List, Optional
from .artifacts_manager import load_trade_data_artifact, artifacts_manager

logger = logging.getLogger(__name__)


async def read_trade_data_artifact(
    artifact_id: str,
) -> Dict[str, Any]:
    """
    读取贸易数据 Artifact
    
    这是一个 ADK 工具函数，供智能体调用读取已保存的贸易数据
    
    Args:
        artifact_id: Artifact ID 或文件名
        
    Returns:
        包含贸易数据和元数据的结果字典
        {
            "success": bool,
            "artifact_id": str,
            "csv_content": str,  # CSV 格式的数据
            "metadata": dict,    # 文件元数据（如果有）
            "size_bytes": int,   # 文件大小
            "error": str         # 错误信息（如果失败）
        }
    """
    try:
        logger.info(f"尝试读取贸易数据 Artifact: {artifact_id}")
        
        result = await load_trade_data_artifact(
            artifact_id=artifact_id,
        )
        
        if result.get("success"):
            csv_content = result.get("csv_content", "")
            size_bytes = len(csv_content.encode('utf-8')) if csv_content else result.get("size_bytes", 0)
            logger.info(f"成功读取 Artifact: {artifact_id}, 大小: {size_bytes} bytes")
            return {
                "success": True,
                "artifact_id": artifact_id,
                "csv_content": csv_content,
                "metadata": result.get("metadata", {}),
                "size_bytes": size_bytes
            }
        else:
            logger.warning(f"读取 Artifact 失败: {artifact_id}, 错误: {result.get('error')}")
            return {
                "success": False,
                "artifact_id": artifact_id,
                "error": result.get("error", "未知错误")
            }
            
    except Exception as e:
        logger.error(f"读取贸易数据 Artifact 时发生异常: {str(e)}")
        return {
            "success": False,
            "artifact_id": artifact_id,
            "error": f"读取异常: {str(e)}"
        }


async def list_trade_data_artifacts() -> Dict[str, Any]:
    """
    列出所有可用的贸易数据 Artifacts
    
    Returns:
        包含 Artifact 列表的结果字典
        {
            "success": bool,
            "artifacts": List[Dict],  # Artifact 列表
            "count": int,             # 总数量
            "error": str              # 错误信息（如果失败）
        }
    """
    try:
        artifacts_list = artifacts_manager.list_artifacts()
        
        return {
            "success": True,
            "artifacts": artifacts_list,
            "count": len(artifacts_list)
        }
        
    except Exception as e:
        logger.error(f"列出贸易数据 Artifacts 时发生异常: {str(e)}")
        return {
            "success": False,
            "error": f"列出失败: {str(e)}",
            "artifacts": [],
            "count": 0
        }


async def analyze_artifact_csv(
    artifact_id: str,
    analysis_type: str = "summary",
) -> Dict[str, Any]:
    """
    分析 Artifact 中的 CSV 数据
    
    Args:
        artifact_id: Artifact ID 或文件名
        analysis_type: 分析类型 ("summary", "statistics", "preview")
        
    Returns:
        分析结果字典
    """
    try:
        # 读取 Artifact 数据
        read_result = await read_trade_data_artifact(artifact_id)
        
        if not read_result.get("success"):
            return read_result
        
        csv_content = read_result.get("csv_content", "")
        if not csv_content:
            return {
                "success": False,
                "error": "CSV 内容为空"
            }
        
        # 基础分析
        lines = csv_content.split('\n')
        header_line = lines[0] if lines else ""
        data_lines = [line for line in lines[1:] if line.strip()]
        
        result = {
            "success": True,
            "artifact_id": artifact_id,
            "analysis_type": analysis_type
        }
        
        if analysis_type == "summary":
            result.update({
                "total_rows": len(data_lines),
                "columns": header_line.split(',') if header_line else [],
                "column_count": len(header_line.split(',')) if header_line else 0,
                "file_size_bytes": len(csv_content.encode('utf-8'))
            })
            
        elif analysis_type == "preview":
            # 返回前5行数据预览
            preview_lines = lines[:6]  # 表头 + 前5行数据
            result.update({
                "preview": '\n'.join(preview_lines),
                "total_rows": len(data_lines),
                "showing_rows": min(5, len(data_lines))
            })
            
        elif analysis_type == "statistics":
            # 简单统计信息
            columns = header_line.split(',') if header_line else []
            result.update({
                "total_rows": len(data_lines),
                "columns": columns,
                "column_count": len(columns),
                "sample_data": data_lines[:3] if data_lines else []
            })
        
        return result
        
    except Exception as e:
        logger.error(f"分析 Artifact CSV 时发生异常: {str(e)}")
        return {
            "success": False,
            "error": f"分析异常: {str(e)}"
        }


# 导出工具函数，供 ADK 注册使用
read_trade_data_artifact_tool = read_trade_data_artifact
list_trade_data_artifacts_tool = list_trade_data_artifacts
analyze_artifact_csv_tool = analyze_artifact_csv