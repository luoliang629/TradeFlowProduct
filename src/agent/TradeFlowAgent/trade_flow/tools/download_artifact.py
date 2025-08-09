"""
下载 Artifact 工具

允许用户下载会话中保存的贸易数据 CSV 文件
"""

import logging
from typing import Dict, Any
from pathlib import Path
from .artifacts_manager import artifacts_manager

logger = logging.getLogger(__name__)


async def download_trade_data_artifact(
    artifact_id: str,
    download_path: str = "downloads",
) -> Dict[str, Any]:
    """
    下载贸易数据 Artifact 为 CSV 文件
    
    Args:
        artifact_id: Artifact ID 或文件名
        download_path: 下载目录路径（默认为 "downloads"）
        
    Returns:
        下载结果字典
        {
            "success": bool,
            "file_path": str,     # 下载文件的完整路径
            "file_name": str,     # 文件名
            "size_bytes": int,    # 文件大小
            "error": str          # 错误信息（如果失败）
        }
    """
    try:
        logger.info(f"尝试下载贸易数据 Artifact: {artifact_id}")
        
        # 从 Artifacts 管理器获取数据
        if artifact_id not in artifacts_manager.artifacts:
            return {
                "success": False,
                "error": f"未找到 Artifact: {artifact_id}"
            }
        
        artifact_data = artifacts_manager.artifacts[artifact_id]
        csv_content = artifact_data.get("content", "")
        metadata = artifact_data.get("metadata", {})
        
        if not csv_content:
            return {
                "success": False,
                "error": "Artifact 内容为空"
            }
        
        # 创建下载目录
        download_dir = Path(download_path)
        download_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成文件名（移除 temp_ 前缀）
        file_name = artifact_id
        if file_name.startswith("temp_"):
            file_name = file_name[5:]
        
        # 确保文件名以 .csv 结尾
        if not file_name.endswith(".csv"):
            file_name += ".csv"
        
        # 完整文件路径
        file_path = download_dir / file_name
        
        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(csv_content)
        
        # 获取文件大小
        size_bytes = file_path.stat().st_size
        
        logger.info(f"成功下载 Artifact 到: {file_path}, 大小: {size_bytes} bytes")
        
        return {
            "success": True,
            "file_path": str(file_path.absolute()),
            "file_name": file_name,
            "size_bytes": size_bytes,
            "records_count": metadata.get("total_records", 0),
            "download_message": f"文件已下载到: {file_path.absolute()}"
        }
        
    except Exception as e:
        logger.error(f"下载贸易数据 Artifact 时发生异常: {str(e)}")
        return {
            "success": False,
            "error": f"下载失败: {str(e)}"
        }


async def export_all_trade_data_artifacts(
    download_path: str = "downloads",
) -> Dict[str, Any]:
    """
    导出所有贸易数据 Artifacts 为 CSV 文件
    
    Args:
        download_path: 下载目录路径（默认为 "downloads"）
        
    Returns:
        导出结果字典
    """
    try:
        artifacts_list = list(artifacts_manager.artifacts.keys())
        
        if not artifacts_list:
            return {
                "success": True,
                "message": "没有可导出的 Artifacts",
                "exported_count": 0,
                "exported_files": []
            }
        
        exported_files = []
        failed_exports = []
        
        for artifact_id in artifacts_list:
            result = await download_trade_data_artifact(artifact_id, download_path)
            
            if result["success"]:
                exported_files.append({
                    "artifact_id": artifact_id,
                    "file_name": result["file_name"],
                    "file_path": result["file_path"],
                    "size_bytes": result["size_bytes"]
                })
            else:
                failed_exports.append({
                    "artifact_id": artifact_id,
                    "error": result["error"]
                })
        
        return {
            "success": True,
            "exported_count": len(exported_files),
            "failed_count": len(failed_exports),
            "exported_files": exported_files,
            "failed_exports": failed_exports,
            "download_path": str(Path(download_path).absolute())
        }
        
    except Exception as e:
        logger.error(f"导出所有贸易数据 Artifacts 时发生异常: {str(e)}")
        return {
            "success": False,
            "error": f"导出失败: {str(e)}",
            "exported_count": 0
        }


async def get_artifact_download_info(
    artifact_id: str,
) -> Dict[str, Any]:
    """
    获取 Artifact 的下载信息
    
    这个工具提供 Artifact 的元数据和下载方式，而不需要实际下载文件。
    
    Args:
        artifact_id: Artifact ID
        
    Returns:
        包含下载信息的字典
        {
            "success": bool,
            "artifact_id": str,
            "file_size_estimate": int,    # 预估文件大小
            "records_count": int,         # 记录数量
            "query_info": dict,          # 查询信息
            "download_methods": dict     # 下载方式
        }
    """
    try:
        if artifact_id not in artifacts_manager.artifacts:
            return {
                "success": False,
                "error": f"未找到 Artifact: {artifact_id}"
            }
        
        # 获取 artifact 数据
        artifact_data = artifacts_manager.artifacts[artifact_id]
        csv_content = artifact_data.get("content", "")
        metadata = artifact_data.get("metadata", {})
        
        # 计算文件大小
        size_bytes = len(csv_content.encode('utf-8')) if csv_content else 0
        
        # 生成文件名
        file_name = artifact_id
        if file_name.startswith("temp_"):
            file_name = file_name[5:]
        if not file_name.endswith(".csv"):
            file_name += ".csv"
        
        return {
            "success": True,
            "artifact_id": artifact_id,
            "file_name": file_name,
            "file_size_estimate": size_bytes,
            "file_size_readable": f"{size_bytes / 1024:.1f} KB" if size_bytes < 1024*1024 else f"{size_bytes / 1024 / 1024:.1f} MB",
            "records_count": metadata.get("total_records", 0),
            "query_info": {
                "query_type": metadata.get("query_type"),
                "product": metadata.get("product"),
                "exporter": metadata.get("exporter"),
                "importer": metadata.get("importer"),
                "date_range": metadata.get("date_range"),
            },
            "download_methods": {
                "direct_download": f"使用 download_trade_data_artifact_tool('{artifact_id}') 下载到本地",
                "custom_path": f"使用 download_trade_data_artifact_tool('{artifact_id}', 'your/path') 下载到指定目录",
                "batch_export": "使用 export_all_trade_data_artifacts_tool() 导出所有数据"
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"获取下载信息失败: {str(e)}"
        }


# 导出工具函数
download_trade_data_artifact_tool = download_trade_data_artifact
export_all_trade_data_artifacts_tool = export_all_trade_data_artifacts
get_artifact_download_info_tool = get_artifact_download_info