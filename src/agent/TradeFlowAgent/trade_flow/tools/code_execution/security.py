"""
代码执行安全机制

提供代码安全性检查和危险操作检测
"""

import ast
import re
from typing import List, Set, Tuple
import logging
from .interfaces import SecurityValidator

logger = logging.getLogger(__name__)


class PythonSecurityValidator(SecurityValidator):
    """Python代码安全验证器"""
    
    # 危险模块黑名单
    DANGEROUS_MODULES = {
        'os', 'sys', 'subprocess', 'shutil', 'glob', 'tempfile',
        'pickle', 'marshal', 'shelve', 'dbm', 'sqlite3',
        'socket', 'urllib', 'http', 'ftplib', 'smtplib',
        'multiprocessing', 'threading', 'concurrent',
        'importlib', '__import__', 'exec', 'eval',
        'compile', 'execfile', 'reload'
    }
    
    # 危险函数黑名单
    DANGEROUS_FUNCTIONS = {
        'open', 'file', 'input', 'raw_input', 'execfile',
        'reload', 'exit', 'quit', '__import__', 'eval', 'exec',
        'compile', 'globals', 'locals', 'vars', 'dir'
    }
    
    # 危险属性访问模式
    DANGEROUS_ATTRIBUTES = {
        '__class__', '__bases__', '__subclasses__', '__mro__',
        '__globals__', '__builtins__', '__import__', '__file__',
        '__name__', '__package__'
    }
    
    # 允许的安全模块
    SAFE_MODULES = {
        'math', 'random', 'datetime', 'time', 'json', 'csv',
        'pandas', 'numpy', 'matplotlib', 'seaborn', 'plotly',
        'scipy', 'scikit-learn', 'sklearn', 'io', 'base64',
        're', 'string', 'collections', 'itertools', 'functools',
        'operator', 'statistics', 'decimal', 'fractions'
    }
    
    def __init__(self):
        self.dangerous_patterns = [
            r'__.*__',  # 魔术方法访问
            r'exec\s*\(',  # exec调用
            r'eval\s*\(',  # eval调用
            r'compile\s*\(',  # compile调用
            r'\.system\s*\(',  # system调用
            r'\.popen\s*\(',  # popen调用
            r'\.call\s*\(',  # subprocess调用
            r'\.run\s*\(',  # subprocess调用
        ]
        
    def validate_code(self, code: str) -> Tuple[bool, str]:
        """
        验证Python代码的安全性
        
        Args:
            code: 要验证的代码字符串
            
        Returns:
            (是否安全, 错误信息)
        """
        try:
            # 1. 检查危险模式
            pattern_check = self._check_dangerous_patterns(code)
            if not pattern_check[0]:
                return pattern_check
                
            # 2. AST语法检查
            ast_check = self._check_ast_security(code)
            if not ast_check[0]:
                return ast_check
                
            # 3. 检查导入语句
            import_check = self._check_imports(code)
            if not import_check[0]:
                return import_check
                
            return True, ""
            
        except SyntaxError as e:
            return False, f"代码语法错误: {str(e)}"
        except Exception as e:
            logger.error(f"代码安全检查异常: {str(e)}")
            return False, f"安全检查失败: {str(e)}"
    
    def _check_dangerous_patterns(self, code: str) -> Tuple[bool, str]:
        """检查危险的代码模式"""
        for pattern in self.dangerous_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                return False, f"检测到危险代码模式: {pattern}"
        
        return True, ""
    
    def _check_ast_security(self, code: str) -> Tuple[bool, str]:
        """使用AST检查代码安全性"""
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                # 检查函数调用
                if isinstance(node, ast.Call):
                    func_check = self._check_function_call(node)
                    if not func_check[0]:
                        return func_check
                
                # 检查属性访问
                if isinstance(node, ast.Attribute):
                    attr_check = self._check_attribute_access(node)
                    if not attr_check[0]:
                        return attr_check
                
                # 检查导入语句
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    import_check = self._check_import_node(node)
                    if not import_check[0]:
                        return import_check
            
            return True, ""
            
        except Exception as e:
            return False, f"AST分析失败: {str(e)}"
    
    def _check_function_call(self, node: ast.Call) -> Tuple[bool, str]:
        """检查函数调用的安全性"""
        func_name = None
        
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
            
        if func_name and func_name in self.DANGEROUS_FUNCTIONS:
            return False, f"禁止调用危险函数: {func_name}"
            
        return True, ""
    
    def _check_attribute_access(self, node: ast.Attribute) -> Tuple[bool, str]:
        """检查属性访问的安全性"""
        if node.attr in self.DANGEROUS_ATTRIBUTES:
            return False, f"禁止访问危险属性: {node.attr}"
            
        return True, ""
    
    def _check_import_node(self, node: ast.Import | ast.ImportFrom) -> Tuple[bool, str]:
        """检查导入节点的安全性"""
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in self.DANGEROUS_MODULES:
                    return False, f"禁止导入危险模块: {alias.name}"
                    
        elif isinstance(node, ast.ImportFrom):
            module = node.module
            if module and module in self.DANGEROUS_MODULES:
                return False, f"禁止从危险模块导入: {module}"
                
        return True, ""
    
    def _check_imports(self, code: str) -> Tuple[bool, str]:
        """检查导入语句"""
        import_lines = []
        
        for line in code.split('\n'):
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                import_lines.append(line)
        
        for import_line in import_lines:
            # 解析导入模块名
            if import_line.startswith('import '):
                module_part = import_line[7:].split(' as ')[0].split(',')[0].strip()
                base_module = module_part.split('.')[0]
            elif import_line.startswith('from '):
                parts = import_line.split(' import ')
                if len(parts) >= 2:
                    module_part = parts[0][5:].strip()
                    base_module = module_part.split('.')[0]
                else:
                    continue
            else:
                continue
                
            # 检查是否为危险模块
            if base_module in self.DANGEROUS_MODULES:
                return False, f"禁止导入危险模块: {base_module}"
            
            # 如果不在安全模块列表中，给出警告但允许执行
            if base_module not in self.SAFE_MODULES:
                logger.warning(f"导入了未知安全性的模块: {base_module}")
        
        return True, ""


class ResourceLimitValidator:
    """资源限制验证器"""
    
    @staticmethod
    def validate_memory_usage(memory_mb: int, max_memory_mb: int) -> Tuple[bool, str]:
        """验证内存使用量"""
        if memory_mb > max_memory_mb:
            return False, f"内存使用超限: {memory_mb}MB > {max_memory_mb}MB"
        return True, ""
    
    @staticmethod
    def validate_execution_time(exec_time: float, max_time: float) -> Tuple[bool, str]:
        """验证执行时间"""
        if exec_time > max_time:
            return False, f"执行时间超限: {exec_time}s > {max_time}s"
        return True, ""
    
    @staticmethod
    def validate_output_size(output_size: int, max_size: int) -> Tuple[bool, str]:
        """验证输出大小"""
        if output_size > max_size:
            return False, f"输出大小超限: {output_size} bytes > {max_size} bytes"
        return True, ""


class CodeSanitizer:
    """代码清理器"""
    
    @staticmethod
    def sanitize_code(code: str) -> str:
        """
        清理和标准化代码
        
        Args:
            code: 原始代码
            
        Returns:
            清理后的代码
        """
        # 移除多余的空白行
        lines = code.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # 移除行末空白
            cleaned_line = line.rstrip()
            cleaned_lines.append(cleaned_line)
        
        # 移除开头和结尾的空行
        while cleaned_lines and not cleaned_lines[0]:
            cleaned_lines.pop(0)
        while cleaned_lines and not cleaned_lines[-1]:
            cleaned_lines.pop()
            
        return '\n'.join(cleaned_lines)
    
    @staticmethod 
    def add_safety_imports(code: str) -> str:
        """
        添加安全导入语句
        
        Args:
            code: 原始代码
            
        Returns:
            添加了安全导入的代码
        """
        safety_imports = [
            "import sys",
            "import warnings",
            "warnings.filterwarnings('ignore')",  # 忽略警告信息
            "sys.stdout.reconfigure(encoding='utf-8', errors='ignore')",  # 设置输出编码
        ]
        
        return '\n'.join(safety_imports) + '\n\n' + code