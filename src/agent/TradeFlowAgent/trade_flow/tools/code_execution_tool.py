"""
代码执行工具

为智能体提供安全的Python代码执行环境，特别优化贸易数据分析场景
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from .code_execution.interfaces import (
    CodeExecutor, ExecutionResult, ExecutionStatus, 
    CodeExecutionRequest, ExecutionLimits
)
from .code_execution.simple_executor import SimpleInProcessExecutor, SimpleSubprocessExecutor
from .artifacts_manager import artifacts_manager

logger = logging.getLogger(__name__)


class CodeExecutionTool:
    """代码执行工具主类"""
    
    def __init__(self):
        self.available_executors: Dict[str, CodeExecutor] = {}
        self.current_executor: Optional[CodeExecutor] = None
        self.default_limits = ExecutionLimits(
            timeout_seconds=30,
            memory_mb=256,
            cpu_time_seconds=15,
            max_output_size=5 * 1024 * 1024,  # 5MB
            allow_network=False,
            allow_file_system=False
        )
        
    async def setup(self) -> bool:
        """设置代码执行环境"""
        try:
            # 注册可用的执行器
            await self._register_executors()
            
            # 选择最佳执行器
            self.current_executor = self._select_best_executor()
            
            if not self.current_executor:
                logger.error("没有可用的代码执行器")
                return False
                
            # 设置选择的执行器
            setup_success = await self.current_executor.setup()
            if setup_success:
                logger.info(f"代码执行工具已设置，使用执行器: {self.current_executor.get_name()}")
                return True
            else:
                logger.error(f"执行器设置失败: {self.current_executor.get_name()}")
                return False
                
        except Exception as e:
            logger.error(f"代码执行工具设置失败: {str(e)}")
            return False
    
    async def _register_executors(self) -> None:
        """注册所有可用的执行器"""
        # 注册简单执行器
        in_process = SimpleInProcessExecutor()
        if in_process.is_available():
            self.available_executors[in_process.get_name()] = in_process
            
        subprocess_exec = SimpleSubprocessExecutor()
        if subprocess_exec.is_available():
            self.available_executors[subprocess_exec.get_name()] = subprocess_exec
        
        # TODO: 未来可以添加 LangChain Sandbox 和 Docker 执行器
        
        logger.info(f"已注册 {len(self.available_executors)} 个执行器: {list(self.available_executors.keys())}")
    
    def _select_best_executor(self) -> Optional[CodeExecutor]:
        """选择最佳的执行器"""
        # 优先级：子进程 > 进程内 （出于安全考虑）
        if "simple_subprocess" in self.available_executors:
            return self.available_executors["simple_subprocess"]
        elif "simple_inprocess" in self.available_executors:
            return self.available_executors["simple_inprocess"]
        else:
            return None
    
    async def cleanup(self) -> None:
        """清理代码执行环境"""
        if self.current_executor:
            await self.current_executor.cleanup()
        
        for executor in self.available_executors.values():
            await executor.cleanup()
    
    async def execute_code(
        self,
        code: str,
        context: Any = None,
        limits: Optional[ExecutionLimits] = None,
        artifacts_access: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        执行Python代码
        
        Args:
            code: 要执行的Python代码
            context: ADK上下文对象
            limits: 执行限制
            artifacts_access: 允许访问的artifact IDs列表
            
        Returns:
            执行结果字典
        """
        try:
            if not self.current_executor:
                return {
                    "success": False,
                    "error": "代码执行器未初始化",
                    "status": "error"
                }
            
            # 准备执行限制
            exec_limits = limits or self.default_limits
            
            # 准备上下文数据
            context_data = await self._prepare_context_data(artifacts_access)
            
            # 创建执行请求
            request = CodeExecutionRequest(
                code=code,
                language="python",
                limits=exec_limits,
                context_data=context_data,
                artifacts_access=artifacts_access or [],
                preload_functions=True
            )
            
            # 执行代码
            logger.info(f"开始执行代码，长度: {len(code)} 字符")
            result = await self.current_executor.execute(request)
            
            # 转换为标准格式
            return self._format_result(result)
            
        except Exception as e:
            logger.error(f"代码执行失败: {str(e)}")
            return {
                "success": False,
                "error": f"代码执行失败: {str(e)}",
                "status": "error",
                "execution_time": 0.0
            }
    
    async def _prepare_context_data(self, artifacts_access: Optional[List[str]]) -> Dict[str, Any]:
        """准备执行上下文数据"""
        context_data = {
            "timestamp": datetime.now().isoformat(),
            "artifacts_data": {}
        }
        
        # 加载允许访问的artifacts数据
        if artifacts_access:
            for artifact_id in artifacts_access:
                try:
                    # 从artifacts管理器获取数据
                    if artifact_id in artifacts_manager.artifacts:
                        artifact_data = artifacts_manager.artifacts[artifact_id]
                        csv_content = artifact_data.get("content", "")
                        if csv_content:
                            context_data["artifacts_data"][artifact_id] = csv_content
                            logger.info(f"已加载 Artifact 数据: {artifact_id}")
                        else:
                            logger.warning(f"Artifact {artifact_id} 内容为空")
                    else:
                        logger.warning(f"未找到 Artifact: {artifact_id}")
                        
                except Exception as e:
                    logger.error(f"加载 Artifact {artifact_id} 失败: {str(e)}")
        
        return context_data
    
    def _format_result(self, result: ExecutionResult) -> Dict[str, Any]:
        """格式化执行结果"""
        return {
            "success": result.status == ExecutionStatus.SUCCESS,
            "status": result.status.value,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "error": result.error_message,
            "execution_time": result.execution_time,
            "memory_used": result.memory_used,
            "return_value": result.return_value,
            "generated_files": result.generated_files,
            "metadata": result.metadata
        }
    
    def get_available_executors(self) -> List[str]:
        """获取可用执行器列表"""
        return list(self.available_executors.keys())
    
    def get_current_executor(self) -> Optional[str]:
        """获取当前使用的执行器名称"""
        return self.current_executor.get_name() if self.current_executor else None


# 全局代码执行工具实例
_code_execution_tool = None


async def get_code_execution_tool() -> CodeExecutionTool:
    """获取代码执行工具实例"""
    global _code_execution_tool
    
    if _code_execution_tool is None:
        _code_execution_tool = CodeExecutionTool()
        await _code_execution_tool.setup()
    
    return _code_execution_tool


async def execute_python_code(
    code: str,
    context: Any = None,
    timeout_seconds: int = 30,
    artifacts_access: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    执行Python代码的便捷函数
    
    Args:
        code: 要执行的Python代码
        context: ADK上下文对象
        timeout_seconds: 超时时间（秒）
        artifacts_access: 允许访问的artifact IDs列表
        
    Returns:
        执行结果字典
    """
    try:
        tool = await get_code_execution_tool()
        
        # 创建执行限制
        limits = ExecutionLimits(
            timeout_seconds=timeout_seconds,
            memory_mb=256,
            cpu_time_seconds=min(timeout_seconds, 15),
            max_output_size=5 * 1024 * 1024,
            allow_network=False,
            allow_file_system=False
        )
        
        return await tool.execute_code(
            code=code,
            context=context,
            limits=limits,
            artifacts_access=artifacts_access
        )
        
    except Exception as e:
        logger.error(f"代码执行便捷函数失败: {str(e)}")
        return {
            "success": False,
            "error": f"代码执行失败: {str(e)}",
            "status": "error",
            "execution_time": 0.0
        }


# ADK工具函数
async def code_execution_tool(
    code: str,
    timeout_seconds: int = 30,
    artifacts_access: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    代码执行工具（ADK工具接口）
    
    这是供智能体调用的主要接口
    
    Args:
        code: 要执行的Python代码
        timeout_seconds: 执行超时时间（秒，默认30秒）
        artifacts_access: 可访问的artifact IDs列表
        
    Returns:
        代码执行结果
        {
            "success": bool,           # 是否执行成功
            "status": str,             # 执行状态
            "stdout": str,             # 标准输出
            "stderr": str,             # 错误输出  
            "error": str,              # 错误信息
            "execution_time": float,   # 执行时间（秒）
            "memory_used": int,        # 内存使用（字节）
        }
    """
    return await execute_python_code(
        code=code,
        context=None,  # 我们不使用 context
        timeout_seconds=timeout_seconds,
        artifacts_access=artifacts_access
    )