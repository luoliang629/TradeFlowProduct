"""
简单代码执行器

使用本地Python环境执行代码（仅适用于开发和测试）
"""

import asyncio
import subprocess
import sys
import tempfile
import os
import time
import logging
from typing import Any, Dict
from pathlib import Path
import traceback
from contextlib import contextmanager, redirect_stdout, redirect_stderr
from io import StringIO

from .interfaces import CodeExecutor, ExecutionResult, ExecutionStatus, CodeExecutionRequest
from .security import PythonSecurityValidator
from .prebuilt_functions import get_prebuilt_functions_code, set_execution_context

logger = logging.getLogger(__name__)


class SimpleSubprocessExecutor(CodeExecutor):
    """简单子进程执行器"""
    
    def __init__(self):
        self.name = "simple_subprocess"
        self.validator = PythonSecurityValidator()
        self._temp_dir = None
        
    async def setup(self) -> bool:
        """设置执行环境"""
        try:
            # 创建临时目录
            self._temp_dir = tempfile.mkdtemp(prefix="trade_code_exec_")
            logger.info(f"创建临时执行目录: {self._temp_dir}")
            return True
        except Exception as e:
            logger.error(f"设置执行环境失败: {str(e)}")
            return False
    
    async def cleanup(self) -> None:
        """清理执行环境"""
        if self._temp_dir and os.path.exists(self._temp_dir):
            import shutil
            try:
                shutil.rmtree(self._temp_dir)
                logger.info(f"清理临时目录: {self._temp_dir}")
            except Exception as e:
                logger.error(f"清理临时目录失败: {str(e)}")
    
    def get_name(self) -> str:
        """获取执行器名称"""
        return self.name
    
    def is_available(self) -> bool:
        """检查执行器是否可用"""
        return sys.executable is not None
    
    async def execute(self, request: CodeExecutionRequest) -> ExecutionResult:
        """
        执行代码
        
        Args:
            request: 代码执行请求
            
        Returns:
            执行结果
        """
        start_time = time.time()
        
        try:
            # 安全性检查
            is_safe, error_msg = self.validator.validate_code(request.code)
            if not is_safe:
                return ExecutionResult(
                    status=ExecutionStatus.SECURITY_VIOLATION,
                    error_message=f"代码安全检查失败: {error_msg}"
                )
            
            # 准备执行代码
            full_code = self._prepare_code(request)
            
            # 执行代码
            result = await self._execute_with_subprocess(full_code, request)
            
            # 记录执行时间
            result.execution_time = time.time() - start_time
            
            return result
            
        except Exception as e:
            logger.error(f"代码执行异常: {str(e)}")
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                error_message=f"执行异常: {str(e)}",
                execution_time=time.time() - start_time
            )
    
    def _prepare_code(self, request: CodeExecutionRequest) -> str:
        """准备执行代码"""
        code_parts = []
        
        # 添加基础导入
        code_parts.append("""
import sys
import warnings
import traceback
warnings.filterwarnings('ignore')
""")
        
        # 如果需要预加载函数库
        if request.preload_functions:
            # 设置上下文
            code_parts.append(f"""
# 设置执行上下文
_artifacts_data = {repr(request.context_data.get('artifacts_data', {}))}
_context = {repr(request.context_data)}
""")
            
            # 添加预定义函数
            code_parts.append(get_prebuilt_functions_code())
            
            # 重写load_trade_data函数
            code_parts.append("""
def load_trade_data(artifact_id):
    \"\"\"从上下文数据加载贸易数据\"\"\"
    import pandas as pd
    from io import StringIO
    
    if artifact_id not in _artifacts_data:
        raise ValueError(f"未找到 Artifact: {artifact_id}")
    
    csv_content = _artifacts_data[artifact_id]
    if not csv_content:
        raise ValueError(f"Artifact {artifact_id} 内容为空")
    
    df = pd.read_csv(StringIO(csv_content))
    
    # 数据类型优化
    for col in df.columns:
        if col in ['quantity', 'sumOfUSD', 'unitPrice', 'weight']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        elif col == 'date':
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    print(f"✅ 成功加载贸易数据: {len(df)} 条记录, {len(df.columns)} 个字段")
    return df
""")
        
        # 添加用户代码
        code_parts.append("""
# === 用户代码开始 ===
""")
        code_parts.append(request.code)
        
        return '\n'.join(code_parts)
    
    async def _execute_with_subprocess(self, code: str, request: CodeExecutionRequest) -> ExecutionResult:
        """使用子进程执行代码"""
        
        # 创建临时Python文件
        temp_file = os.path.join(self._temp_dir, "code_exec.py")
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(code)
        
        try:
            # 执行子进程
            process = await asyncio.create_subprocess_exec(
                sys.executable, temp_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self._temp_dir
            )
            
            # 等待执行完成，带超时
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=request.limits.timeout_seconds
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return ExecutionResult(
                    status=ExecutionStatus.TIMEOUT,
                    error_message=f"代码执行超时 ({request.limits.timeout_seconds}秒)"
                )
            
            # 处理输出
            stdout_text = stdout.decode('utf-8', errors='ignore') if stdout else ""
            stderr_text = stderr.decode('utf-8', errors='ignore') if stderr else ""
            
            # 检查输出大小限制
            total_output_size = len(stdout_text.encode()) + len(stderr_text.encode())
            if total_output_size > request.limits.max_output_size:
                return ExecutionResult(
                    status=ExecutionStatus.RESOURCE_EXCEEDED,
                    error_message=f"输出大小超限: {total_output_size} > {request.limits.max_output_size}"
                )
            
            # 确定执行状态
            if process.returncode == 0:
                status = ExecutionStatus.SUCCESS
            else:
                status = ExecutionStatus.ERROR
            
            return ExecutionResult(
                status=status,
                stdout=stdout_text,
                stderr=stderr_text,
                error_message=stderr_text if process.returncode != 0 else ""
            )
            
        except Exception as e:
            logger.error(f"子进程执行失败: {str(e)}")
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                error_message=f"子进程执行失败: {str(e)}"
            )
        
        finally:
            # 清理临时文件
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception:
                pass


class SimpleInProcessExecutor(CodeExecutor):
    """简单进程内执行器（更高风险，但性能更好）"""
    
    def __init__(self):
        self.name = "simple_inprocess" 
        self.validator = PythonSecurityValidator()
        
    async def setup(self) -> bool:
        """设置执行环境"""
        return True
    
    async def cleanup(self) -> None:
        """清理执行环境"""
        pass
    
    def get_name(self) -> str:
        """获取执行器名称"""
        return self.name
    
    def is_available(self) -> bool:
        """检查执行器是否可用"""
        return True
    
    async def execute(self, request: CodeExecutionRequest) -> ExecutionResult:
        """
        在当前进程中执行代码
        
        Args:
            request: 代码执行请求
            
        Returns:
            执行结果
        """
        start_time = time.time()
        
        try:
            # 安全性检查
            is_safe, error_msg = self.validator.validate_code(request.code)
            if not is_safe:
                return ExecutionResult(
                    status=ExecutionStatus.SECURITY_VIOLATION,
                    error_message=f"代码安全检查失败: {error_msg}"
                )
            
            # 准备执行代码
            full_code = self._prepare_code(request)
            
            # 捕获输出
            stdout_buffer = StringIO()
            stderr_buffer = StringIO()
            
            execution_globals = {}
            
            try:
                with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
                    # 编译代码
                    compiled_code = compile(full_code, '<code_execution>', 'exec')
                    
                    # 执行代码
                    exec(compiled_code, execution_globals)
                
                # 获取输出
                stdout_text = stdout_buffer.getvalue()
                stderr_text = stderr_buffer.getvalue()
                
                result = ExecutionResult(
                    status=ExecutionStatus.SUCCESS,
                    stdout=stdout_text,
                    stderr=stderr_text,
                    execution_time=time.time() - start_time
                )
                
                return result
                
            except Exception as e:
                # 执行异常
                error_traceback = traceback.format_exc()
                stderr_text = stderr_buffer.getvalue()
                
                return ExecutionResult(
                    status=ExecutionStatus.ERROR,
                    stdout=stdout_buffer.getvalue(),
                    stderr=stderr_text,
                    error_message=f"代码执行错误: {str(e)}\\n{error_traceback}",
                    execution_time=time.time() - start_time
                )
                
        except Exception as e:
            logger.error(f"代码执行异常: {str(e)}")
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                error_message=f"执行异常: {str(e)}",
                execution_time=time.time() - start_time
            )
    
    def _prepare_code(self, request: CodeExecutionRequest) -> str:
        """准备执行代码"""
        code_parts = []
        
        # 添加基础导入
        code_parts.append("""
import sys
import warnings
import pandas as pd
import numpy as np
from io import StringIO
warnings.filterwarnings('ignore')
""")
        
        # 如果需要预加载函数库
        if request.preload_functions:
            # 设置artifacts数据
            artifacts_data = request.context_data.get('artifacts_data', {})
            code_parts.append(f"_artifacts_data = {repr(artifacts_data)}")
            
            # 添加load_trade_data函数
            code_parts.append("""
def load_trade_data(artifact_id):
    \"\"\"从上下文数据加载贸易数据\"\"\"
    if artifact_id not in _artifacts_data:
        raise ValueError(f"未找到 Artifact: {artifact_id}")
    
    csv_content = _artifacts_data[artifact_id]
    if not csv_content:
        raise ValueError(f"Artifact {artifact_id} 内容为空")
    
    df = pd.read_csv(StringIO(csv_content))
    
    # 数据类型优化
    for col in df.columns:
        if col in ['quantity', 'sumOfUSD', 'unitPrice', 'weight']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        elif col == 'date':
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    print(f"✅ 成功加载贸易数据: {len(df)} 条记录, {len(df.columns)} 个字段")
    return df

def analyze_trade_trends(df, period='month', value_col='sumOfUSD'):
    \"\"\"分析贸易趋势\"\"\"
    df_copy = df.copy()
    df_copy['date'] = pd.to_datetime(df_copy['date'])
    
    if period == 'month':
        df_copy['period'] = df_copy['date'].dt.to_period('M')
    elif period == 'quarter':
        df_copy['period'] = df_copy['date'].dt.to_period('Q')
    elif period == 'year':
        df_copy['period'] = df_copy['date'].dt.year
    
    trends = df_copy.groupby('period').agg({
        value_col: ['sum', 'mean', 'count'],
        'quantity': 'sum'
    }).round(2)
    
    trends.columns = ['总额', '平均值', '交易次数', '总数量']
    return trends.reset_index()

def top_importers(df, top_n=10, value_col='sumOfUSD'):
    \"\"\"分析最活跃的进口商\"\"\"
    importers = df.groupby('importer').agg({
        value_col: 'sum',
        'quantity': 'sum',
        'id': 'count'
    }).round(2)
    importers.columns = ['总交易额', '总数量', '交易次数']
    return importers.sort_values('总交易额', ascending=False).head(top_n).reset_index()

def top_exporters(df, top_n=10, value_col='sumOfUSD'):
    \"\"\"分析最活跃的出口商\"\"\"
    exporters = df.groupby('exporter').agg({
        value_col: 'sum',
        'quantity': 'sum',
        'id': 'count'
    }).round(2)
    exporters.columns = ['总交易额', '总数量', '交易次数']
    return exporters.sort_values('总交易额', ascending=False).head(top_n).reset_index()

def generate_summary_report(df):
    \"\"\"生成贸易数据摘要报告\"\"\"
    report = {}
    report['总记录数'] = len(df)
    if 'sumOfUSD' in df.columns:
        report['总交易额'] = f"${df['sumOfUSD'].sum():,.2f}"
        report['平均交易额'] = f"${df['sumOfUSD'].mean():,.2f}"
    if 'importer' in df.columns:
        report['不重复进口商数量'] = df['importer'].nunique()
    if 'exporter' in df.columns:
        report['不重复出口商数量'] = df['exporter'].nunique()
    return report

print("✅ 贸易数据分析函数库已加载")
""")
        
        # 添加用户代码
        code_parts.append("""
# === 用户代码开始 ===
""")
        code_parts.append(request.code)
        
        return '\n'.join(code_parts)