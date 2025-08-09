"""
Artifacts 管理工具

用于管理贸易数据的 Artifacts 存储和读取
"""

import logging
from typing import Dict, List, Any
from trade_flow.shared_libraries.csv_converter import (
    trade_records_to_csv, 
    generate_csv_filename,
    create_csv_metadata
)

logger = logging.getLogger(__name__)


class TradeDataArtifactsManager:
    """贸易数据 Artifacts 管理器"""
    
    def __init__(self):
        """初始化 Artifacts 管理器"""
        self.artifacts = {}  # 临时存储，实际使用时会用 InMemoryArtifactService
    
    async def save_trade_data_csv(
        self,
        trade_records: List[Dict[str, Any]], 
        query_params: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        将贸易数据保存为 CSV 格式的 Artifact
        
        Args:
            trade_records: 贸易记录列表
            query_params: 查询参数
            
        Returns:
            包含 artifact 信息的字典
        """
        try:
            if not trade_records:
                return {
                    "success": False,
                    "error": "没有贸易记录可保存"
                }
            
            # 转换为 CSV 格式
            csv_content = trade_records_to_csv(trade_records)
            
            if not csv_content:
                return {
                    "success": False, 
                    "error": "CSV 转换失败"
                }
            
            # 生成文件名和元数据
            filename = generate_csv_filename(query_params)
            metadata = create_csv_metadata(query_params, len(trade_records), filename)
            
            # 临时存储模式
            # 注意：在实际的 ADK 环境中，这里应该使用 ADK 的 artifact service
            # 但由于我们的工具不接收 context 参数，所以使用内存存储
            artifact_id = f"temp_{filename}"
            self.artifacts[artifact_id] = {
                "content": csv_content,
                "metadata": metadata
            }
            
            return {
                "success": True,
                "artifact_id": artifact_id,
                "filename": filename,
                "metadata": metadata,
                "records_count": len(trade_records),
                "csv_size_bytes": len(csv_content.encode('utf-8'))
            }
                
        except Exception as e:
            logger.error(f"保存贸易数据 Artifact 失败: {str(e)}")
            return {
                "success": False,
                "error": f"保存失败: {str(e)}"
            }
    
    async def load_trade_data_csv(
        self, 
        artifact_id: str,
    ) -> Dict[str, Any]:
        """
        从 Artifact 加载贸易数据 CSV
        
        Args:
            artifact_id: Artifact ID 或文件名
            
        Returns:
            包含 CSV 内容和元数据的字典
        """
        try:
            # 临时存储模式
            # 注意：在实际的 ADK 环境中，这里应该使用 ADK 的 artifact service
            if artifact_id in self.artifacts:
                artifact_data = self.artifacts[artifact_id]
                return {
                    "success": True,
                    "artifact_id": artifact_id,
                    "csv_content": artifact_data["content"],
                    "metadata": artifact_data["metadata"]
                }
            else:
                return {
                    "success": False,
                    "error": f"未找到 Artifact: {artifact_id}"
                }
                    
        except Exception as e:
            logger.error(f"加载贸易数据 Artifact 失败: {str(e)}")
            return {
                "success": False,
                "error": f"加载失败: {str(e)}"
            }
    
    def list_artifacts(self) -> List[Dict[str, Any]]:
        """
        列出所有贸易数据 Artifacts
        
        Returns:
            Artifact 列表
        """
        if self.artifacts:
            # 临时存储模式
            return [
                {
                    "artifact_id": aid,
                    "metadata": data.get("metadata", {})
                }
                for aid, data in self.artifacts.items()
            ]
        else:
            # 实际使用时需要通过 context 查询
            return []


# 全局实例
artifacts_manager = TradeDataArtifactsManager()


async def save_trade_data_artifact(
    trade_records: List[Dict[str, Any]], 
    query_params: Dict[str, Any],
) -> Dict[str, Any]:
    """
    保存贸易数据到 Artifacts
    
    这是一个便捷函数，供其他模块直接调用
    """
    return await artifacts_manager.save_trade_data_csv(
        trade_records=trade_records,
        query_params=query_params,
    )


async def load_trade_data_artifact(artifact_id: str) -> Dict[str, Any]:
    """
    从 Artifacts 加载贸易数据
    
    这是一个便捷函数，供其他模块直接调用
    """
    return await artifacts_manager.load_trade_data_csv(
        artifact_id=artifact_id,
    )