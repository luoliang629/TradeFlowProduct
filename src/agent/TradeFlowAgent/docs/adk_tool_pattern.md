# ADK 工具模式最佳实践

## 背景

在研究 Google ADK (Agent Development Kit) 的文档和实际使用后，我们发现了正确的工具定义模式。

## 工具函数签名

### 标准模式（推荐）

基于代码库的分析，ADK 工具应该**不包含** context 参数：

```python
async def tool_name(
    required_param: str,
    optional_param: Optional[str] = None,
) -> Dict[str, Any]:
    """
    工具描述
    
    Args:
        required_param: 必需参数
        optional_param: 可选参数
        
    Returns:
        结果字典
    """
    # 实现代码
    pass
```

### 为什么不需要 context 参数？

1. **一致性**：代码库中的大部分工具（web_search_tool、company_info_tool 等）都没有 context 参数
2. **简洁性**：减少参数复杂度，让工具更易于理解和使用
3. **兼容性**：避免 LLM function call 的限制问题

## 处理需要状态存储的场景

如果工具需要保存状态（如 Artifacts），可以使用以下方案：

### 方案1：内存存储（当前实现）

```python
class TradeDataArtifactsManager:
    def __init__(self):
        self.artifacts = {}  # 内存存储
    
    async def save_trade_data_csv(self, trade_records, query_params):
        # 保存到内存
        artifact_id = f"temp_{filename}"
        self.artifacts[artifact_id] = {
            "content": csv_content,
            "metadata": metadata
        }
        return {"success": True, "artifact_id": artifact_id}

# 全局实例
artifacts_manager = TradeDataArtifactsManager()
```

### 方案2：使用外部存储服务

在生产环境中，可以使用：
- Redis/Memcached 进行临时存储
- S3/GCS 进行持久化存储
- 数据库进行元数据管理

## 工具注册

ADK 支持两种工具注册方式：

### 方式1：直接函数引用（推荐）

```python
from ..tools import web_search_tool, get_trade_data_tool

agent = Agent(
    name="my_agent",
    tools=[web_search_tool, get_trade_data_tool],
)
```

### 方式2：FunctionTool 包装器

```python
from google.adk.tools import FunctionTool

def create_custom_tool() -> FunctionTool:
    async def handler(param: str) -> Dict[str, Any]:
        # 实现
        pass
    return FunctionTool(func=handler)
```

## 最佳实践总结

1. **不要在工具函数中包含 context 参数**
2. **使用全局实例或外部服务处理状态存储**
3. **保持工具函数签名简洁明了**
4. **使用类型提示和详细的文档字符串**
5. **返回标准化的结果格式（Dict[str, Any]）**

## 示例：正确的工具实现

```python
# tools/my_tool.py
from typing import Dict, Any, Optional

async def my_analysis_tool(
    data_source: str,
    analysis_type: str = "summary",
    limit: int = 10,
) -> Dict[str, Any]:
    """
    执行数据分析
    
    Args:
        data_source: 数据源标识
        analysis_type: 分析类型
        limit: 结果数量限制
        
    Returns:
        分析结果字典
    """
    try:
        # 执行分析
        results = perform_analysis(data_source, analysis_type, limit)
        
        # 如果需要保存结果，使用全局服务
        if needs_persistence:
            artifact_id = await global_storage.save(results)
            return {
                "success": True,
                "results": results,
                "artifact_id": artifact_id
            }
        
        return {
            "success": True,
            "results": results
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# 导出为工具
my_analysis_tool = my_analysis_tool
```

这种模式使工具更加简洁、易于测试，并且完全兼容 ADK 框架的要求。