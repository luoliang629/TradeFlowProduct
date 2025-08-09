"""
代码执行工具接口定义

定义代码执行器的标准接口和数据结构
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List
from enum import Enum


class ExecutionStatus(Enum):
    """执行状态枚举"""
    SUCCESS = "success"
    ERROR = "error" 
    TIMEOUT = "timeout"
    SECURITY_VIOLATION = "security_violation"
    RESOURCE_EXCEEDED = "resource_exceeded"


@dataclass
class ExecutionLimits:
    """执行限制配置"""
    timeout_seconds: int = 30  # 执行超时时间
    memory_mb: int = 256       # 内存限制（MB）
    cpu_time_seconds: int = 10  # CPU时间限制
    max_output_size: int = 10 * 1024 * 1024  # 最大输出大小（10MB）
    allow_network: bool = False  # 是否允许网络访问
    allow_file_system: bool = False  # 是否允许文件系统访问


@dataclass
class ExecutionResult:
    """代码执行结果"""
    status: ExecutionStatus
    stdout: str = ""
    stderr: str = ""
    return_value: Any = None
    execution_time: float = 0.0
    memory_used: int = 0
    error_message: str = ""
    generated_files: List[str] = field(default_factory=list)
    plots: List[bytes] = field(default_factory=list)  # 生成的图表数据
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CodeExecutionRequest:
    """代码执行请求"""
    code: str
    language: str = "python"
    limits: ExecutionLimits = field(default_factory=ExecutionLimits)
    context_data: Dict[str, Any] = field(default_factory=dict)  # 上下文数据
    artifacts_access: List[str] = field(default_factory=list)  # 允许访问的artifact IDs
    preload_functions: bool = True  # 是否预加载函数库


class CodeExecutor(ABC):
    """代码执行器抽象基类"""
    
    @abstractmethod
    async def execute(self, request: CodeExecutionRequest) -> ExecutionResult:
        """
        执行代码
        
        Args:
            request: 代码执行请求
            
        Returns:
            执行结果
        """
        pass
    
    @abstractmethod
    async def setup(self) -> bool:
        """
        设置执行环境
        
        Returns:
            是否设置成功
        """
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """清理执行环境"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """获取执行器名称"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查执行器是否可用"""
        pass


class ExecutionEnvironment(Enum):
    """执行环境类型"""
    LANGCHAIN_SANDBOX = "langchain_sandbox"
    DOCKER_JUPYTER = "docker_jupyter"
    SIMPLE_SUBPROCESS = "simple_subprocess"
    

@dataclass
class ExecutorConfig:
    """执行器配置"""
    environment: ExecutionEnvironment
    default_limits: ExecutionLimits = field(default_factory=ExecutionLimits)
    extra_config: Dict[str, Any] = field(default_factory=dict)


class SecurityValidator(ABC):
    """安全验证器抽象基类"""
    
    @abstractmethod
    def validate_code(self, code: str) -> tuple[bool, str]:
        """
        验证代码安全性
        
        Args:
            code: 要验证的代码
            
        Returns:
            (是否安全, 错误信息)
        """
        pass


class ResultProcessor(ABC):
    """结果处理器抽象基类"""
    
    @abstractmethod
    async def process(self, result: ExecutionResult, context: Any = None) -> ExecutionResult:
        """
        处理执行结果
        
        Args:
            result: 原始执行结果
            context: 上下文对象
            
        Returns:
            处理后的结果
        """
        pass