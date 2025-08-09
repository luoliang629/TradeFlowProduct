# TradeFlow Agent 使用指南

> **TradeFlow Agent** - 基于Google ADK的专业B2B贸易智能助手  
> 通过自然语言交互帮助用户完成买家开发、供应商采购等贸易业务

[![Agent状态](https://img.shields.io/badge/Agent-运行中-green)](http://localhost:8000/api/v1/health/detailed)
[![API接入](https://img.shields.io/badge/API-集成完成-blue)](http://localhost:8000/api/v1/docs#/agent)

## 🎯 Agent核心能力

### 🛒 商品供应商发现（核心功能）
从任意商品页面追溯完整供应链，发现真实制造商和供应商

**支持平台**：沃尔玛、亚马逊、阿里巴巴、京东、天猫、Made-in-China等20+平台

### 📊 贸易数据查询
基于真实海关数据的贸易分析，包括进出口数据、市场趋势、竞争分析

**数据来源**：Tendata官方API，非爬虫数据

### 🏢 企业背景调查
供应商资质和贸易能力评估，包括企业信息、贸易记录、风险评估

### 🔍 智能搜索分析
高质量网页搜索和内容提取，准确率95%+

**技术支持**：Jina Search API独家支持

## 🚀 快速开始

### 1. 通过API接口使用

**基础查询示例**：
```bash
curl -X POST "http://localhost:8000/api/v1/agent/query" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -d '{
    "message": "分析苹果公司的主要供应商",
    "session_id": "supplier_analysis_session",
    "stream": false
  }'
```

**流式响应示例**：
```bash
curl -X POST "http://localhost:8000/api/v1/agent/query" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -d '{
    "message": "查询2024年手机对美国的出口数据",
    "session_id": "trade_analysis_session", 
    "stream": true
  }'
```

### 2. 通过前端界面使用

```bash
# 启动前端应用
cd src/frontend
npm run dev

# 访问聊天界面
open http://localhost:3000
```

### 3. 直接访问Agent（开发调试）

```bash
cd src/agent/TradeFlowAgent
adk web
# 访问 http://localhost:8000 （Agent独立界面）
```

## 💼 核心功能使用指南

### 🛒 商品供应商发现

**功能描述**：从商品链接分析完整供应链，包括品牌方、代工厂、零部件供应商

**使用方式**：
```json
{
  "message": "分析这个商品的供应商：https://www.walmart.com/ip/Apple-iPhone-15-Pro",
  "session_id": "product_supplier_analysis"
}
```

**预期输出**：
```
✅ 商品信息：iPhone 15 Pro (苹果官方)
✅ 供应链层级：
   └── 零售商：沃尔玛
   └── 品牌方：Apple Inc. (美国)
   └── 代工厂：富士康科技集团 (台湾/大陆)
   └── 核心供应商：台积电(芯片)、立讯精密(连接器)、舜宇光学(摄像头)
✅ 贸易数据：2024年苹果代工厂出口额超200亿美元
✅ 联系建议：如需采购相似产品，推荐联系富士康、比亚迪电子等一级代工厂
```

**支持的电商平台**：
- 🇺🇸 **美国**：沃尔玛、亚马逊、eBay、Target、Best Buy
- 🇨🇳 **中国**：阿里巴巴、京东、天猫、淘宝、拼多多
- 🌐 **B2B平台**：Made-in-China、GlobalSources、TradeKey
- 🏪 **品牌官网**：各大品牌官方商城和产品页面

---

### 📊 贸易数据查询

**功能描述**：查询真实海关数据，分析贸易趋势和市场机会

**使用方式**：
```json
{
  "message": "查询2024年智能手机对欧盟的出口趋势",
  "session_id": "trade_trend_analysis"
}
```

**预期输出**：
```
📊 2024年智能手机对欧盟出口分析
✅ 总出口额：约450亿美元 (同比增长12%)
✅ 主要出口国：中国(76%)、韩国(15%)、美国(6%)
✅ 热门品牌：三星、华为、小米、OPPO
✅ 增长趋势：5G手机出口增长35%，折叠屏增长128%
✅ 贸易政策：欧盟对中国智能手机征收5-15%关税
```

**支持的查询类型**：
- 📈 **出口数据**：按国家、产品、时间维度查询出口统计
- 📉 **进口数据**：目标市场进口来源和趋势分析
- 🏭 **企业数据**：特定企业的贸易记录和主要客户
- 📍 **市场分析**：目标市场的竞争格局和准入要求
- 📊 **行业趋势**：细分行业的发展趋势和增长预测

---

### 🏢 企业背景调查

**功能描述**：全面评估供应商资质、贸易能力和合作风险

**使用方式**：
```json
{
  "message": "分析比亚迪电子的供应商资质和贸易能力",
  "session_id": "supplier_evaluation"
}
```

**预期输出**：
```
🏢 比亚迪电子有限公司 - 供应商评估报告
✅ 企业资质：AAA级供应商，ISO9001/14001认证
✅ 贸易能力：年出口额100+亿元，覆盖50+国家
✅ 主要客户：苹果、华为、vivo、小米等知名品牌
✅ 产品线：手机组装、平板电脑、智能穿戴设备
✅ 生产基地：深圳、东莞、西安、印度、越南
✅ 风险评估：财务稳健，供应链风险较低
✅ 合作建议：适合中大批量订单，MOQ通常10K+
```

**评估维度**：
- 🏅 **资质认证**：ISO认证、行业资质、政府认可
- 💰 **贸易规模**：年营收、出口额、市场份额
- 🤝 **客户网络**：主要客户、合作关系、市场声誉
- 🏭 **生产能力**：产能规模、技术水平、质量控制
- 🌍 **全球布局**：生产基地、销售网络、供应链管理
- ⚖️ **风险评估**：财务状况、合规记录、供应链风险
- 💡 **合作建议**：订单要求、付款条件、合作模式

---

### 🔍 智能搜索分析

**功能描述**：高质量网页搜索和内容分析，获取最新市场信息

**使用方式**：
```json
{
  "message": "搜索2024年新能源汽车电池行业的最新发展趋势",
  "session_id": "industry_research"
}
```

**搜索优势**：
- 🎯 **精准搜索**：Jina Search API，搜索质量远超传统搜索
- 🌐 **全网覆盖**：覆盖新闻、报告、官网、社交媒体等多源信息
- 📊 **智能筛选**：AI自动筛选相关度高的内容，去除噪音信息
- 🔄 **实时更新**：获取最新发布的市场信息和行业动态
- 📈 **趋势分析**：结合多源信息进行趋势分析和预测

## 🔧 高级使用技巧

### 1. 会话管理

**创建专题会话**：
```bash
curl -X POST "http://localhost:8000/api/v1/chat/sessions" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "苹果供应链深度分析",
    "description": "分析苹果公司全球供应链网络和主要合作伙伴"
  }'
```

**继续会话对话**：
```bash
curl -X POST "http://localhost:8000/api/v1/agent/query" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "请深入分析富士康在苹果供应链中的角色",
    "session_id": "previous_session_id"
  }'
```

### 2. 流式响应处理

**JavaScript SSE处理**：
```javascript
const eventSource = new EventSource(
  `http://localhost:8000/api/v1/agent/stream?session_id=${sessionId}&token=${jwtToken}`
);

eventSource.onmessage = function(event) {
  const data = JSON.parse(event.data);
  
  switch(data.type) {
    case 'agent_response':
      displayAgentMessage(data.content);
      break;
    case 'thinking':
      showThinkingIndicator(data.content);
      break;
    case 'tool_call':
      showToolExecution(data.tool, data.parameters);
      break;
    case 'error':
      handleError(data.error);
      break;
  }
};

eventSource.onerror = function(event) {
  console.error('SSE连接错误:', event);
  // 实现重连逻辑
};
```

**Python异步处理**：
```python
import asyncio
import aiohttp
import json

async def stream_agent_query(session_id: str, message: str, token: str):
    url = f"http://localhost:8000/api/v1/agent/stream"
    params = {"session_id": session_id, "token": token}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            async for line in response.content:
                if line.startswith(b'data: '):
                    data = json.loads(line[6:])
                    yield data

# 使用示例
async def main():
    async for chunk in stream_agent_query("test_session", "分析特斯拉供应商", "your_jwt_token"):
        print(f"收到响应: {chunk}")

asyncio.run(main())
```

### 3. 批量查询处理

**并发处理多个查询**：
```python
import asyncio
import aiohttp

async def batch_agent_queries(queries: list, base_session_id: str):
    tasks = []
    for i, query in enumerate(queries):
        session_id = f"{base_session_id}_{i}"
        task = query_agent(query, session_id)
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results

# 批量供应商分析示例
queries = [
    "分析富士康的贸易能力和主要客户",
    "分析比亚迪电子的供应商资质",
    "分析立讯精密的产品线和市场地位"
]

results = await batch_agent_queries(queries, "supplier_batch_analysis")
```

## 📊 Agent性能优化

### 1. 缓存策略

Agent服务内置智能缓存，常见查询会被缓存以提升响应速度：

```bash
# 检查缓存状态
curl http://localhost:8000/api/v1/health/detailed | jq '.agent_status.cache_hit_rate'

# 清理缓存（如果需要最新数据）
curl -X DELETE http://localhost:8000/api/v1/agent/cache \
  -H "Authorization: Bearer <token>"
```

**缓存策略**：
- ✅ **企业信息查询** - 缓存24小时
- ✅ **历史贸易数据** - 缓存7天
- ❌ **实时市场数据** - 不缓存
- ❌ **个性化分析** - 不缓存

### 2. 并发优化

系统支持多用户并发查询，使用连接池技术优化性能：

```python
# 配置优化参数（在.env文件中）
AGENT_RUNNER_POOL_SIZE=10        # 增加并发处理能力
AGENT_TIMEOUT_SECONDS=45         # 适当延长超时时间
AGENT_CACHE_TTL=7200            # 延长缓存时间
AGENT_MAX_RETRIES=5             # 增加重试次数
```

### 3. 查询优化建议

**高效查询方式**：
```json
{
  "message": "分析富士康2024年对美国的出口数据和主要产品类别",
  "session_id": "focused_analysis",
  "context": {
    "company": "富士康",
    "time_range": "2024年",
    "target_market": "美国"
  }
}
```

**避免的查询方式**：
```json
{
  "message": "告诉我所有电子制造商的所有信息",  // 过于宽泛
  "session_id": "broad_query"
}
```

## 🐛 故障排除

### 常见问题解决

**1. Agent响应超时**
```bash
# 检查Agent连接状态
curl http://localhost:8000/api/v1/health/detailed | jq '.checks.agent_runner'

# 重启Agent服务
docker-compose restart backend
```

**2. 查询结果不准确**
```bash
# 清除缓存，获取最新数据
curl -X DELETE http://localhost:8000/api/v1/agent/cache \
  -H "Authorization: Bearer <token>"
  
# 使用更具体的查询语句
"分析富士康在2024年Q3的iPhone组装业务" # 具体
vs
"分析富士康" # 过于宽泛
```

**3. 流式响应中断**
```javascript
// 实现自动重连机制
let reconnectAttempts = 0;
const maxReconnects = 3;

function connectSSE(sessionId, token) {
  const eventSource = new EventSource(`/api/v1/agent/stream?session_id=${sessionId}&token=${token}`);
  
  eventSource.onerror = function(event) {
    eventSource.close();
    
    if (reconnectAttempts < maxReconnects) {
      reconnectAttempts++;
      setTimeout(() => {
        console.log(`重连尝试 ${reconnectAttempts}/${maxReconnects}`);
        connectSSE(sessionId, token);
      }, 2000 * reconnectAttempts);
    }
  };
}
```

**4. API权限错误**
```bash
# 检查JWT token有效性
curl -X GET "http://localhost:8000/api/v1/auth/verify" \
  -H "Authorization: Bearer <your-token>"

# 重新获取token
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your-username",
    "password": "your-password"
  }'
```

### 性能调优

**优化Agent响应速度**：
```bash
# 调整环境变量
export AGENT_RUNNER_POOL_SIZE=8         # 增加连接池大小
export AGENT_ENABLE_CACHE=true          # 启用缓存
export AGENT_CACHE_TTL=3600             # 设置缓存时间
export AGENT_TIMEOUT_SECONDS=30         # 合理设置超时时间

# 重启服务应用配置
docker-compose restart backend
```

## 📚 最佳实践

### 1. 查询语句优化

**✅ 推荐的查询方式**：
- "分析富士康在苹果供应链中的具体角色和2024年业务数据"
- "查询比亚迪电子对北美市场的出口情况和主要产品"
- "从这个iPhone产品页面分析完整的供应商网络：[URL]"

**❌ 避免的查询方式**：
- "分析所有电子产品" （过于宽泛）
- "告诉我一切关于贸易的信息" （无明确目标）
- "这个网站有什么内容" （缺乏分析目标）

### 2. 会话管理策略

**专题会话**：为不同的分析主题创建独立会话
```python
sessions = {
    "supplier_research": "供应商调研专用会话",
    "market_analysis": "市场分析专用会话", 
    "product_sourcing": "产品采购专用会话"
}
```

**上下文延续**：在同一会话中逐步深入分析
```
1. "分析苹果公司的主要供应商"
2. "深入分析富士康在苹果供应链中的角色"
3. "富士康的主要竞争对手有哪些？"
4. "比较富士康和比亚迪电子的代工能力"
```

### 3. 结果整合与分析

**结构化输出处理**：
```python
def parse_agent_response(response: str) -> dict:
    """解析Agent响应，提取结构化信息"""
    result = {
        "suppliers": [],
        "trade_data": {},
        "recommendations": []
    }
    
    # 解析供应商信息
    if "供应商：" in response:
        # 提取供应商列表
        pass
    
    # 解析贸易数据
    if "出口额：" in response:
        # 提取数值数据
        pass
    
    return result
```

## 🔗 相关资源

### 文档链接
- **后端API文档**: [src/backend/README.md](../src/backend/README.md)
- **Agent独立文档**: [src/agent/TradeFlowAgent/README.md](../src/agent/TradeFlowAgent/README.md)
- **API规范文档**: [docs/api/agent_api_specification.md](api/agent_api_specification.md)

### 在线资源
- **Swagger API文档**: http://localhost:8000/api/v1/docs#/agent
- **Agent健康检查**: http://localhost:8000/api/v1/health/detailed
- **Agent独立界面**: cd src/agent/TradeFlowAgent && adk web

### 支持渠道
- **GitHub Issues**: 报告问题和bug
- **技术讨论**: 参与GitHub Discussions
- **功能建议**: 提交Feature Request

---

**TradeFlow Agent** - 让B2B贸易分析更智能，让供应商发现更精准！ 🚀

*最后更新：2025-01-09*