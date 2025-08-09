# Jina Search 迁移指南

本文档说明如何从之前的多搜索引擎模式迁移到 Jina-only 模式。

## 迁移概述

从 v2.1.0 开始，TradeFlowAgent 只支持 Jina Search API，不再提供 DuckDuckGo 或其他搜索引擎作为降级方案。

## 主要变更

### 1. 配置变更

**之前**：
- `JINA_API_KEY` 是可选的
- 未配置时自动降级到 DuckDuckGo

**现在**：
- `JINA_API_KEY` 是必需的
- 未配置时直接抛出 `ConfigurationError`

### 2. 错误处理变更

**之前**：
```python
try:
    # 尝试 Jina
except:
    try:
        # 降级到 DuckDuckGo
    except:
        # 返回错误
```

**现在**：
```python
try:
    # 只使用 Jina
except ConfigurationError:
    # 提示配置 API Key
except APIError:
    # 提示 API 相关错误
except NetworkError:
    # 自动重试，最终抛出网络错误
except ParseError:
    # 提示解析错误
```

### 3. 返回格式变更

错误返回格式从：
```json
{
    "status": "error",
    "error": "搜索服务暂时不可用"
}
```

变更为直接抛出异常，包含详细的错误信息和解决方案。

## 迁移步骤

### 步骤 1：获取 Jina API Key

1. 访问 https://jina.ai
2. 注册账号
3. 获取 API Key

### 步骤 2：更新配置

更新 `.env` 文件：
```bash
# 之前（可选）
# JINA_API_KEY=your-jina-api-key

# 现在（必需）
JINA_API_KEY=your-actual-jina-api-key
```

### 步骤 3：更新错误处理代码

如果您有自定义的错误处理逻辑，需要更新为处理新的错误类型：

```python
from trade_flow.tools.web_search import (
    web_search,
    ConfigurationError,
    APIError,
    NetworkError,
    ParseError
)

try:
    result = await web_search("查询内容")
except ConfigurationError as e:
    # 处理配置错误
    print(f"请配置 API Key: {e}")
except APIError as e:
    # 处理 API 错误
    print(f"API 调用失败: {e}")
except NetworkError as e:
    # 处理网络错误
    print(f"网络连接问题: {e}")
except ParseError as e:
    # 处理解析错误
    print(f"响应解析失败: {e}")
```

### 步骤 4：测试验证

运行测试脚本验证配置：
```bash
python test/test_jina_only_search.py
```

## 优势

1. **更高的搜索质量**：Jina Search 提供更准确的搜索结果
2. **更好的错误处理**：明确的错误类型和解决方案
3. **自动重试机制**：提高系统稳定性
4. **质量评估指标**：帮助 ReAct Agent 做出更好的决策

## 常见问题

### Q: 为什么移除了 DuckDuckGo？
A: 为了提供一致的高质量搜索体验，避免因降级导致的结果质量下降。

### Q: 如果 Jina API 暂时不可用怎么办？
A: 系统会自动重试 3 次，如果仍然失败，会抛出明确的错误信息。建议：
1. 检查网络连接
2. 确认 API Key 有效
3. 查看 Jina 服务状态

### Q: 是否会支持其他搜索 API？
A: 未来可能会支持，但会作为独立的配置选项，而不是降级方案。

## 需要帮助？

如果在迁移过程中遇到问题：
1. 查看错误信息中的解决建议
2. 参考 `docs/search_configuration.md`
3. 提交 Issue 到项目仓库