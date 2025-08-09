# Context 参数问题解决方案

## 问题描述

在 ADK (Google Agent Development Kit) 框架中，当 LLM 进行 function call 时，只能传递可序列化的参数（字符串、数字、布尔值、简单对象等），而不能传递复杂的 Python 对象如 ADK context。

## 原始问题

`get_trade_data` 函数内部调用 `_get_trade_data_list` 时传递了 `context` 参数，但函数签名中没有定义这个参数，导致 `NameError`。

## 解决方案

### 1. 为 `get_trade_data` 添加可选的 context 参数

```python
async def get_trade_data(
    product_desc: Optional[str] = None,
    hs_code: Optional[str] = None,
    importer: Optional[str] = None,
    exporter: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    origin_country: Optional[str] = None,
    destination_country: Optional[str] = None,
    context: Optional[Any] = None,  # ADK context 对象
) -> Dict[str, Any]:
```

### 2. 在内部函数中正确定义 context 参数

```python
async def _get_trade_data_list(
    auth: TendataAuth,
    product_desc: Optional[str],
    hs_code: Optional[str],
    importer: Optional[str],
    exporter: Optional[str],
    start_date: str,
    end_date: str,
    origin_country: Optional[str],
    destination_country: Optional[str],
    context: Optional[Any] = None,  # ADK context 对象，用于 Artifacts 保存
) -> Dict[str, Any]:
```

## ADK 工具调用机制

### LLM 调用工具时

当 LLM 通过 function call 调用工具时：
- 只能传递可序列化的参数
- 不需要（也不能）传递 context 参数
- ADK 框架会自动注入 context

### 工具内部调用其他工具时

当一个工具内部调用另一个工具时：
- 需要显式传递 context 参数
- 用于保持会话状态和访问共享资源（如 Artifacts）

## 最佳实践

1. **工具函数签名**: 将 context 作为最后一个可选参数
2. **默认值**: context 参数默认值应为 None
3. **类型提示**: 使用 `Optional[Any]` 作为 context 的类型提示
4. **文档说明**: 在函数文档字符串中说明 context 参数的用途

## 示例

### 正确的工具定义

```python
async def my_tool(
    required_param: str,
    optional_param: Optional[str] = None,
    context: Optional[Any] = None,  # ADK context 对象
) -> Dict[str, Any]:
    """
    我的工具函数
    
    Args:
        required_param: 必需参数
        optional_param: 可选参数
        context: ADK context 对象（框架自动注入）
    """
    # 使用 context 保存 artifacts
    if context and hasattr(context, 'save_artifact'):
        await context.save_artifact(...)
```

### LLM 调用示例

```python
# LLM 生成的 function call（不包含 context）
result = await my_tool(
    required_param="value",
    optional_param="optional"
)
```

### 工具间调用示例

```python
# 工具内部调用其他工具（显式传递 context）
result = await another_tool(
    param1="value",
    context=context  # 传递接收到的 context
)
```

## 总结

通过将 context 作为可选参数添加到工具函数签名中，我们解决了 LLM function call 的限制，同时保持了工具间调用的灵活性。ADK 框架会在需要时自动注入 context，使得工具既可以被 LLM 调用，也可以被其他工具调用。