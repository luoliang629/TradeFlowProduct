# 搜索功能配置指南

TradeFlowAgent 的搜索功能完全依赖 Jina Search API，提供高质量的搜索结果。

## 配置要求

### 必需配置：Jina Search API

系统只支持 Jina Search，不提供降级方案。如果未配置或配置错误，搜索功能将直接抛出错误。

1. **获取 API Key**：
   - 访问 https://jina.ai
   - 注册账号并获取 API Key

2. **配置环境变量**：
   ```bash
   # .env 文件
   JINA_API_KEY=your-actual-jina-api-key
   ```

3. **验证配置**：
   ```bash
   # 运行测试脚本
   python test/test_jina_only_search.py
   ```

## 使用示例

### 基础搜索
```python
from trade_flow.tools.web_search import web_search

# 基础搜索
result = await web_search("贸易政策", num_results=10)

# 中文搜索
result = await web_search("中国进出口数据", num_results=5)
```

### 站内搜索
```python
# 搜索特定网站
result = await web_search(
    "产品价格",
    sites=["alibaba.com", "made-in-china.com"]
)

# 搜索政府网站
result = await web_search(
    "关税政策",
    sites=["mofcom.gov.cn", "customs.gov.cn"]
)
```

## 错误处理

系统定义了明确的错误类型，便于问题定位：

### 1. ConfigurationError（配置错误）
```
缺少 JINA_API_KEY 配置。
请按以下步骤配置：
1. 访问 https://jina.ai 获取 API Key
2. 设置环境变量：export JINA_API_KEY='your-actual-api-key'
3. 或在 .env 文件中添加：JINA_API_KEY=your-actual-api-key
```

### 2. APIError（API错误）
- **认证失败**：请检查 API Key 是否正确
- **请求限流**：请稍后再试，或升级 API 计划
- **服务器错误**：服务端临时问题，请稍后重试

### 3. NetworkError（网络错误）
- **连接超时**：检查网络连接稳定性
- **请求失败**：检查防火墙或代理设置

### 4. ParseError（解析错误）
- 响应格式异常，可能是 API 返回格式变更

## 高级特性

### 1. 自动重试机制
- 对网络错误和超时自动重试
- 使用指数退避策略（1秒、2秒、4秒）
- 最多重试 3 次

### 2. 质量评估
```python
# 返回结果包含质量指标
{
    "quality_metrics": {
        "score": 0.85,           # 综合质量分 (0-1)
        "result_count": 10,      # 结果数量
        "confidence": "high",    # 置信度 (high/medium/low)
        "source_diversity": 0.8, # 来源多样性
        "relevance_estimate": "high"  # 相关性估计
    }
}
```

### 3. 响应解析
- 主解析方法支持标准 Jina 格式
- 备用解析方法处理格式变化
- 自动提取域名和摘要信息

## 搜索结果格式

```json
{
    "status": "success",
    "query": "搜索关键词",
    "results": [
        {
            "title": "结果标题",
            "url": "https://example.com/page",
            "snippet": "结果摘要...",
            "displayLink": "example.com"
        }
    ],
    "total": 10,
    "source": "jina_api",
    "quality_metrics": {
        "score": 0.85,
        "result_count": 10,
        "confidence": "high",
        "source_diversity": 0.8,
        "relevance_estimate": "high"
    }
}
```

## 注意事项

1. **无降级方案**：系统不再提供 DuckDuckGo 或其他搜索引擎作为备选
2. **错误即停止**：任何错误都会直接抛出，不会尝试其他方法
3. **配置验证**：启动时会验证 API Key 配置，无效配置会立即报错
4. **日志记录**：所有搜索请求和错误都会记录在日志中

## 相关文件

- 搜索工具实现：`trade_flow/tools/web_search.py`
- 搜索 Agent：`trade_flow/agents/search_agent.py`
- 测试脚本：`test/test_jina_only_search.py`
- 配置文件：`.env.example`