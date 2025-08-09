# TradeFlow Agent API 规范文档

## 文档信息
- **版本**: v1.0
- **创建日期**: 2025-01-09  
- **文档类型**: API规范
- **OpenAPI版本**: 3.0.3

---

## 1. 概述

本文档定义了TradeFlow后端与Agent服务之间的API接口规范，以及前端调用Agent相关功能的API规范。

### 1.1 基础信息
- **Agent服务地址**: `http://localhost:8001` (开发环境)
- **API版本**: v1
- **认证方式**: Bearer Token (JWT)
- **响应格式**: JSON / Server-Sent Events

### 1.2 通信模式
- **同步查询**: REST API (JSON响应)
- **流式对话**: Server-Sent Events (SSE)
- **文件生成**: 异步任务 + 回调

---

## 2. Agent服务API（内部）

### 2.1 查询处理接口

#### POST /query
处理用户查询请求

**请求体**:
```json
{
  "query": "分析这个商品的供应商：https://www.walmart.com/ip/Apple-iPhone-15",
  "user_id": 12345,
  "session_id": "uuid-session-id",
  "context": {
    "conversation_id": "uuid-conversation-id",
    "language": "zh-CN",
    "market": "US",
    "product_category": "electronics",
    "previous_messages": [
      {
        "role": "user",
        "content": "我想找手机供应商"
      }
    ]
  },
  "options": {
    "stream": true,
    "max_tokens": 2000,
    "temperature": 0.7,
    "tools": ["web_search", "trade_data", "company_info"]
  }
}
```

**响应（流式SSE）**:
```
event: message
data: {"type": "thinking", "content": "正在分析商品页面..."}

event: message  
data: {"type": "chunk", "content": "根据分析，这款iPhone 15"}

event: message
data: {"type": "tool_use", "tool": "web_search", "query": "iPhone 15 supplier"}

event: message
data: {"type": "final", "content": "完整分析结果...", "metadata": {...}}

event: done
data: {"tokens_used": 1500, "tools_called": 3, "duration_ms": 3200}
```

---

### 2.2 工具调用接口

#### POST /tools/execute
直接调用特定工具

**请求体**:
```json
{
  "tool": "trade_data_query",
  "parameters": {
    "product": "smartphone",
    "market": "US",
    "year": 2024,
    "data_type": "export"
  },
  "user_id": 12345
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "total_export": 45000000000,
    "top_exporters": [
      {"country": "China", "amount": 34000000000, "share": 0.76},
      {"country": "Vietnam", "amount": 6000000000, "share": 0.13}
    ],
    "trend": "increasing",
    "yoy_growth": 0.12
  },
  "tool": "trade_data_query",
  "execution_time_ms": 450
}
```

---

### 2.3 健康检查接口

#### GET /health
检查Agent服务状态

**响应**:
```json
{
  "status": "healthy",
  "agent": "ready",
  "version": "1.0.0",
  "model": "claude-3-opus",
  "tools_available": [
    "web_search",
    "trade_data_query",
    "company_info",
    "enterprise_discovery"
  ],
  "uptime_seconds": 3600
}
```

---

## 3. 后端暴露给前端的API

### 3.1 对话管理

#### POST /api/v1/agent/conversations
创建新的Agent对话

**请求体**:
```json
{
  "title": "寻找手机供应商",
  "type": "supplier_search",
  "initial_context": {
    "product": "smartphone",
    "market": "Europe"
  }
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "conversation_id": "conv-uuid-12345",
    "title": "寻找手机供应商",
    "created_at": "2025-01-09T10:00:00Z",
    "status": "active"
  }
}
```

---

#### GET /api/v1/agent/conversations/{conversation_id}
获取对话详情

**响应**:
```json
{
  "success": true,
  "data": {
    "conversation_id": "conv-uuid-12345",
    "title": "寻找手机供应商",
    "messages": [
      {
        "id": "msg-001",
        "role": "user",
        "content": "我想找欧洲的手机供应商",
        "timestamp": "2025-01-09T10:00:00Z"
      },
      {
        "id": "msg-002",
        "role": "assistant",
        "content": "我帮您搜索欧洲的手机供应商...",
        "timestamp": "2025-01-09T10:00:05Z",
        "metadata": {
          "tokens_used": 500,
          "tools_called": ["enterprise_discovery", "trade_data_query"]
        }
      }
    ],
    "status": "active",
    "tokens_total": 500,
    "created_at": "2025-01-09T10:00:00Z",
    "updated_at": "2025-01-09T10:00:05Z"
  }
}
```

---

### 3.2 流式对话接口

#### POST /api/v1/agent/chat
发送消息并接收流式响应

**请求体**:
```json
{
  "conversation_id": "conv-uuid-12345",
  "message": "分析这个商品的供应商：https://www.walmart.com/ip/Apple-iPhone-15",
  "options": {
    "stream": true,
    "include_sources": true
  }
}
```

**响应（SSE流）**:
```
event: start
data: {"conversation_id": "conv-uuid-12345", "message_id": "msg-003"}

event: thinking
data: {"content": "正在分析您提供的商品链接..."}

event: tool_use
data: {"tool": "jina_reader", "purpose": "提取商品信息"}

event: chunk
data: {"content": "根据分析，这是一款Apple iPhone 15 Pro"}

event: chunk
data: {"content": "，主要供应商包括：\n1. 富士康科技集团"}

event: source
data: {"type": "trade_data", "url": "tendata.com/...", "title": "2024年苹果供应链报告"}

event: final
data: {
  "complete": true,
  "tokens_used": 1200,
  "sources": ["tendata", "jina_search"],
  "confidence": 0.92
}

event: end
data: {"message_id": "msg-003", "duration_ms": 3500}
```

---

### 3.3 快捷查询接口

#### POST /api/v1/agent/quick-query/{type}
执行预定义的快捷查询

**类型选项**:
- `buyer_recommendation` - 买家推荐
- `supplier_search` - 供应商搜索  
- `market_analysis` - 市场分析
- `trade_data` - 贸易数据查询
- `company_profile` - 企业背景调查

**请求体（供应商搜索示例）**:
```json
{
  "product": "LED灯",
  "quantity": "10000 units/month",
  "target_price": "$5-8/unit",
  "certifications": ["CE", "RoHS"],
  "preferred_countries": ["China", "Vietnam"],
  "language": "zh-CN"
}
```

**响应**:
```json
{
  "success": true,
  "query_type": "supplier_search",
  "data": {
    "suppliers": [
      {
        "company_name": "深圳市光明电子有限公司",
        "match_score": 0.95,
        "location": "深圳市宝安区",
        "contact": {
          "name": "张经理",
          "phone": "+86-755-12345678",
          "email": "sales@guangming.com",
          "wechat": "gm_sales_01"
        },
        "capabilities": {
          "monthly_capacity": "50000 units",
          "moq": "5000 units",
          "lead_time": "15-20 days",
          "price_range": "$4.5-7.5/unit"
        },
        "certifications": ["CE", "RoHS", "ISO9001"],
        "trade_data": {
          "annual_export": "$25M",
          "main_markets": ["Europe", "North America"],
          "years_in_business": 12
        },
        "verification_status": "verified",
        "data_sources": ["alibaba", "tendata", "company_website"]
      }
    ],
    "total_found": 15,
    "query_id": "query-uuid-789"
  },
  "metadata": {
    "execution_time_ms": 2800,
    "tokens_used": 1500,
    "confidence": 0.88
  }
}
```

---

### 3.4 文件生成接口

#### POST /api/v1/agent/generate-report
生成分析报告

**请求体**:
```json
{
  "type": "supplier_analysis",
  "query_id": "query-uuid-789",
  "format": "pdf",
  "language": "zh-CN",
  "include_sections": [
    "executive_summary",
    "supplier_comparison",
    "risk_assessment",
    "recommendations"
  ]
}
```

**响应**:
```json
{
  "success": true,
  "task_id": "task-uuid-456",
  "status": "processing",
  "estimated_time_seconds": 30,
  "webhook_url": "/api/v1/agent/tasks/task-uuid-456/status"
}
```

---

#### GET /api/v1/agent/tasks/{task_id}/status
获取任务状态

**响应（处理中）**:
```json
{
  "task_id": "task-uuid-456",
  "status": "processing",
  "progress": 0.65,
  "message": "正在生成供应商对比分析..."
}
```

**响应（完成）**:
```json
{
  "task_id": "task-uuid-456",
  "status": "completed",
  "result": {
    "file_id": "file-uuid-789",
    "file_name": "供应商分析报告_20250109.pdf",
    "file_size": 245678,
    "download_url": "/api/v1/files/file-uuid-789/download",
    "preview_url": "/api/v1/files/file-uuid-789/preview",
    "expires_at": "2025-01-16T10:00:00Z"
  }
}
```

---

## 4. 错误响应规范

### 4.1 错误响应格式
```json
{
  "success": false,
  "error": {
    "code": "AGENT_TIMEOUT",
    "message": "Agent响应超时",
    "details": "查询处理时间超过30秒限制",
    "request_id": "req-uuid-123",
    "timestamp": "2025-01-09T10:00:00Z"
  }
}
```

### 4.2 错误码定义

| 错误码 | HTTP状态码 | 说明 |
|--------|-----------|------|
| AGENT_UNAVAILABLE | 503 | Agent服务不可用 |
| AGENT_TIMEOUT | 504 | Agent响应超时 |
| INVALID_QUERY | 400 | 查询格式无效 |
| RATE_LIMIT_EXCEEDED | 429 | 超出调用频率限制 |
| TOKEN_LIMIT_EXCEEDED | 402 | Token额度不足 |
| TOOL_ERROR | 500 | 工具调用失败 |
| CONTEXT_TOO_LARGE | 413 | 上下文超出限制 |
| UNAUTHORIZED | 401 | 未授权访问 |
| CONVERSATION_NOT_FOUND | 404 | 对话不存在 |

---

## 5. 限流和配额

### 5.1 API限流规则
```yaml
rate_limits:
  chat:
    requests_per_minute: 20
    requests_per_hour: 500
    concurrent_streams: 3
  
  quick_query:
    requests_per_minute: 30
    requests_per_hour: 1000
  
  report_generation:
    requests_per_day: 50
    concurrent_tasks: 2
```

### 5.2 Token配额
```yaml
token_quotas:
  free_tier:
    daily_tokens: 10000
    max_tokens_per_request: 2000
    
  pro_tier:
    daily_tokens: 100000
    max_tokens_per_request: 4000
    
  enterprise:
    daily_tokens: unlimited
    max_tokens_per_request: 8000
```

---

## 6. Webhook规范

### 6.1 任务完成通知
```json
{
  "event": "task.completed",
  "task_id": "task-uuid-456",
  "user_id": 12345,
  "result": {
    "status": "success",
    "file_id": "file-uuid-789",
    "metadata": {
      "type": "supplier_analysis",
      "pages": 15,
      "generation_time_ms": 28000
    }
  },
  "timestamp": "2025-01-09T10:00:00Z"
}
```

### 6.2 错误通知
```json
{
  "event": "task.failed",
  "task_id": "task-uuid-456",
  "user_id": 12345,
  "error": {
    "code": "GENERATION_FAILED",
    "message": "报告生成失败",
    "retry_after": 300
  },
  "timestamp": "2025-01-09T10:00:00Z"
}
```

---

## 7. 数据模型定义

### 7.1 Message对象
```typescript
interface Message {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  metadata?: {
    tokens_used?: number;
    tools_called?: string[];
    sources?: string[];
    confidence?: number;
    files?: string[];
  };
}
```

### 7.2 Conversation对象
```typescript
interface Conversation {
  id: string;
  user_id: number;
  title: string;
  type: 'general' | 'buyer_dev' | 'supplier_search' | 'market_analysis';
  messages: Message[];
  status: 'active' | 'archived' | 'deleted';
  tokens_total: number;
  created_at: string;
  updated_at: string;
  metadata?: {
    language?: string;
    market?: string;
    product_category?: string;
  };
}
```

### 7.3 Supplier对象
```typescript
interface Supplier {
  company_name: string;
  match_score: number;
  location: string;
  contact: {
    name?: string;
    phone?: string;
    email?: string;
    wechat?: string;
    whatsapp?: string;
  };
  capabilities: {
    monthly_capacity?: string;
    moq?: string;
    lead_time?: string;
    price_range?: string;
  };
  certifications: string[];
  trade_data?: {
    annual_export?: string;
    main_markets?: string[];
    years_in_business?: number;
  };
  verification_status: 'verified' | 'unverified' | 'pending';
  data_sources: string[];
}
```

---

## 8. 安全规范

### 8.1 认证要求
- 所有API调用需要Bearer Token
- Token有效期：24小时
- 支持Token刷新机制

### 8.2 数据加密
- HTTPS传输加密
- 敏感数据字段加密存储
- 日志脱敏处理

### 8.3 输入验证
- 查询长度限制：5000字符
- 文件大小限制：10MB
- XSS/SQL注入防护

---

## 9. 性能SLA

| 指标 | 目标值 | 测量方法 |
|------|--------|----------|
| API可用性 | 99.9% | 每月统计 |
| 平均响应时间 | <200ms | P50 |
| 流式响应首字节 | <1s | P95 |
| Agent查询完成 | <5s | P95 |
| 报告生成 | <30s | P95 |

---

## 10. 版本管理

### 10.1 版本策略
- 当前版本：v1
- 版本格式：`/api/v{major}/...`
- 向后兼容：至少支持2个大版本

### 10.2 弃用通知
- 提前3个月通知
- 文档标注弃用字段
- 提供迁移指南

---

## 附录

### A. 示例代码

#### TypeScript客户端
```typescript
class AgentAPIClient {
  private baseURL = '/api/v1/agent';
  
  async chat(conversationId: string, message: string): Promise<EventSource> {
    const response = await fetch(`${this.baseURL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.token}`
      },
      body: JSON.stringify({
        conversation_id: conversationId,
        message: message,
        options: { stream: true }
      })
    });
    
    return new EventSource(response.url);
  }
  
  async quickQuery(type: string, params: any): Promise<any> {
    const response = await fetch(`${this.baseURL}/quick-query/${type}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.token}`
      },
      body: JSON.stringify(params)
    });
    
    return response.json();
  }
}
```

#### Python客户端
```python
import httpx
import json
from typing import AsyncGenerator

class AgentAPIClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        self.client = httpx.AsyncClient()
    
    async def chat_stream(
        self, 
        conversation_id: str, 
        message: str
    ) -> AsyncGenerator:
        """流式对话"""
        async with self.client.stream(
            "POST",
            f"{self.base_url}/chat",
            json={
                "conversation_id": conversation_id,
                "message": message,
                "options": {"stream": True}
            },
            headers=self.headers
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    yield json.loads(line[6:])
    
    async def quick_query(self, query_type: str, params: dict) -> dict:
        """快捷查询"""
        response = await self.client.post(
            f"{self.base_url}/quick-query/{query_type}",
            json=params,
            headers=self.headers
        )
        return response.json()
```

---

*本文档为TradeFlow Agent API的正式规范，最后更新：2025-01-09*