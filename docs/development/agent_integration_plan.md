# TradeFlowAgent 集成方案

## 文档信息
- **版本**: v1.0
- **创建日期**: 2025-01-09
- **文档类型**: 技术集成方案
- **相关组件**: TradeFlowAgent、FastAPI后端、React前端

---

## 1. 概述

TradeFlowAgent已通过Google ADK独立开发完成，现需要将其集成到TradeFlow的前后端系统中。本文档提供详细的集成方案。

### 1.1 当前状态
- **Agent开发**: ✅ 已完成
- **后端API**: ✅ 已完成（除Agent Gateway）
- **前端界面**: 🚧 进行中
- **集成状态**: ⏳ 待实施

### 1.2 集成目标
1. 将TradeFlowAgent作为独立服务运行
2. 通过API Gateway实现前后端与Agent的通信
3. 支持SSE流式响应
4. 保持Agent的独立性和可扩展性

---

## 2. 架构设计

### 2.1 整体架构
```
┌─────────────┐     ┌──────────────┐     ┌────────────────┐
│   前端UI    │────▶│  FastAPI     │────▶│ TradeFlowAgent │
│   (React)   │◀────│   后端       │◀────│    (ADK)       │
└─────────────┘     └──────────────┘     └────────────────┘
      SSE                Gateway               gRPC/HTTP
```

### 2.2 通信方式
- **前端 → 后端**: RESTful API + SSE
- **后端 → Agent**: HTTP/gRPC（推荐）
- **响应模式**: 流式响应（Server-Sent Events）

---

## 3. Agent服务化方案

### 3.1 Agent服务封装
```python
# src/agent/TradeFlowAgent/agent_service.py
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio
from trade_flow.main_agent import root_agent

app = FastAPI(title="TradeFlow Agent Service")

@app.post("/query")
async def process_query(request: QueryRequest):
    """处理查询请求"""
    async def generate():
        # 调用TradeFlowAgent
        async for chunk in root_agent.stream(request.query):
            yield f"data: {json.dumps(chunk)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "agent": "ready"}
```

### 3.2 Agent部署配置
```yaml
# docker-compose.agent.yml
version: '3.8'
services:
  tradeflow-agent:
    build: ./src/agent/TradeFlowAgent
    ports:
      - "8001:8001"
    environment:
      - MODEL=claude-3-opus
      - JINA_API_KEY=${JINA_API_KEY}
      - TENDATA_API_KEY=${TENDATA_API_KEY}
    volumes:
      - ./data/agent:/app/data
    restart: unless-stopped
```

---

## 4. 后端集成实现

### 4.1 Agent Gateway服务
```python
# src/backend/app/services/agent_gateway.py
import httpx
import json
from typing import AsyncGenerator

class AgentGatewayService:
    """Agent网关服务"""
    
    def __init__(self):
        self.agent_url = "http://localhost:8001"
        self.client = httpx.AsyncClient()
    
    async def query_agent(
        self,
        query: str,
        user_id: int,
        session_id: str,
        context: dict = None
    ) -> AsyncGenerator:
        """查询Agent并返回流式响应"""
        
        # 构建请求
        request_data = {
            "query": query,
            "user_id": user_id,
            "session_id": session_id,
            "context": context or {}
        }
        
        # 发送请求到Agent服务
        async with self.client.stream(
            "POST",
            f"{self.agent_url}/query",
            json=request_data
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    yield data

agent_gateway = AgentGatewayService()
```

### 4.2 SSE端点实现
```python
# src/backend/app/api/v1/agent.py
from fastapi import APIRouter, Depends
from sse_starlette.sse import EventSourceResponse
from app.services.agent_gateway import agent_gateway
from app.services.conversation import conversation_service

router = APIRouter(prefix="/agent", tags=["Agent"])

@router.post("/chat")
async def chat_with_agent(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """与Agent对话"""
    
    async def event_generator():
        # 保存用户消息
        await conversation_service.add_message(
            request.conversation_id,
            request.message,
            current_user.id
        )
        
        # 查询Agent
        async for chunk in agent_gateway.query_agent(
            query=request.message,
            user_id=current_user.id,
            session_id=request.conversation_id
        ):
            # 发送SSE事件
            yield {
                "event": "message",
                "data": json.dumps(chunk)
            }
            
            # 保存Agent响应
            if chunk.get("type") == "final":
                await conversation_service.add_agent_response(
                    request.conversation_id,
                    chunk.get("content")
                )
    
    return EventSourceResponse(event_generator())
```

---

## 5. 前端集成实现

### 5.1 Agent服务调用
```typescript
// src/frontend/services/agentService.ts
export class AgentService {
  private eventSource: EventSource | null = null;

  async startChat(
    conversationId: string,
    message: string,
    onMessage: (data: any) => void,
    onError?: (error: any) => void
  ) {
    // 关闭之前的连接
    this.stopChat();

    // 创建SSE连接
    const url = `/api/v1/agent/chat`;
    this.eventSource = new EventSource(url);

    // 发送消息
    await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getToken()}`
      },
      body: JSON.stringify({
        conversation_id: conversationId,
        message: message
      })
    });

    // 监听消息
    this.eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onMessage(data);
    };

    this.eventSource.onerror = (error) => {
      if (onError) onError(error);
      this.stopChat();
    };
  }

  stopChat() {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
  }
}
```

### 5.2 React组件集成
```tsx
// src/frontend/components/ChatInterface.tsx
import React, { useState, useEffect } from 'react';
import { AgentService } from '../services/agentService';

export const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const agentService = new AgentService();

  const sendMessage = async (content: string) => {
    // 添加用户消息
    setMessages(prev => [...prev, {
      role: 'user',
      content,
      timestamp: new Date()
    }]);

    // 开始流式接收
    setIsStreaming(true);
    let assistantMessage = '';

    await agentService.startChat(
      conversationId,
      content,
      (data) => {
        if (data.type === 'chunk') {
          assistantMessage += data.content;
          // 更新助手消息
          setMessages(prev => {
            const newMessages = [...prev];
            if (newMessages[newMessages.length - 1].role === 'assistant') {
              newMessages[newMessages.length - 1].content = assistantMessage;
            } else {
              newMessages.push({
                role: 'assistant',
                content: assistantMessage,
                timestamp: new Date()
              });
            }
            return newMessages;
          });
        } else if (data.type === 'final') {
          setIsStreaming(false);
        }
      },
      (error) => {
        console.error('Chat error:', error);
        setIsStreaming(false);
      }
    );
  };

  // 组件渲染逻辑...
};
```

---

## 6. 数据流转方案

### 6.1 请求流程
```
1. 用户输入 → React前端
2. 前端构建请求 → FastAPI后端
3. 后端验证&路由 → Agent Gateway
4. Gateway转发 → TradeFlowAgent
5. Agent处理 → 返回结果
```

### 6.2 响应流程
```
1. Agent生成响应 → 流式输出
2. Gateway接收 → SSE转换
3. 后端转发 → SSE事件流
4. 前端接收 → 实时显示
5. 完成后 → 保存对话历史
```

### 6.3 数据格式定义
```typescript
// 请求格式
interface ChatRequest {
  conversation_id: string;
  message: string;
  context?: {
    product_id?: string;
    market?: string;
    language?: string;
  };
}

// 响应格式
interface ChatResponse {
  type: 'chunk' | 'final' | 'error';
  content?: string;
  metadata?: {
    sources?: string[];
    confidence?: number;
    tokens_used?: number;
  };
  error?: string;
}
```

---

## 7. 部署架构

### 7.1 开发环境
```bash
# 启动Agent服务
cd src/agent/TradeFlowAgent
adk web --port 8001

# 启动后端服务
cd src/backend
uvicorn app.main:app --reload --port 8000

# 启动前端服务
cd src/frontend
npm run dev
```

### 7.2 生产环境
```yaml
# kubernetes/agent-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tradeflow-agent
spec:
  replicas: 2
  selector:
    matchLabels:
      app: tradeflow-agent
  template:
    metadata:
      labels:
        app: tradeflow-agent
    spec:
      containers:
      - name: agent
        image: tradeflow-agent:latest
        ports:
        - containerPort: 8001
        env:
        - name: MODEL
          value: "claude-3-opus"
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
```

---

## 8. 监控和日志

### 8.1 性能指标
- **响应时间**: P95 < 4秒
- **并发处理**: 支持50+并发会话
- **Token使用**: 平均每次查询 < 2000 tokens
- **错误率**: < 1%

### 8.2 日志收集
```python
# 集成日志
import logging
from app.core.logging import get_logger

logger = get_logger(__name__)

# Agent调用日志
logger.info(f"Agent query: user={user_id}, query={query[:100]}")
logger.info(f"Agent response: tokens={tokens_used}, time={response_time}ms")
```

### 8.3 监控告警
- Agent服务健康检查
- 响应时间异常告警
- Token使用量超限告警
- 错误率异常告警

---

## 9. 测试方案

### 9.1 单元测试
```python
# tests/test_agent_gateway.py
import pytest
from app.services.agent_gateway import agent_gateway

@pytest.mark.asyncio
async def test_agent_query():
    """测试Agent查询"""
    response = []
    async for chunk in agent_gateway.query_agent(
        "查询苹果手机的供应商",
        user_id=1,
        session_id="test"
    ):
        response.append(chunk)
    
    assert len(response) > 0
    assert any(chunk.get("type") == "final" for chunk in response)
```

### 9.2 集成测试
- 端到端对话测试
- SSE连接稳定性测试
- 并发请求测试
- 错误恢复测试

### 9.3 性能测试
- 负载测试：100并发用户
- 压力测试：找出系统极限
- 稳定性测试：24小时持续运行

---

## 10. 实施计划

### Phase 1: 基础集成（1周）
- [ ] Agent服务化封装
- [ ] 后端Gateway实现
- [ ] 基础SSE通信

### Phase 2: 功能完善（1周）
- [ ] 对话历史管理
- [ ] 文件生成集成
- [ ] 错误处理优化

### Phase 3: 性能优化（3天）
- [ ] 缓存机制
- [ ] 并发优化
- [ ] 响应时间优化

### Phase 4: 部署上线（3天）
- [ ] Docker镜像构建
- [ ] K8s配置
- [ ] 监控配置

---

## 11. 风险和缓解

| 风险 | 影响 | 缓解措施 |
|-----|------|---------|
| Agent响应慢 | 用户体验差 | 实现缓存、优化提示词 |
| SSE连接中断 | 对话中断 | 自动重连机制 |
| Token消耗高 | 成本增加 | 限流、优化对话长度 |
| 并发瓶颈 | 系统崩溃 | 负载均衡、队列管理 |

---

## 12. 附录

### 12.1 相关文档
- [TradeFlowAgent README](../../src/agent/TradeFlowAgent/README.md)
- [ADK集成指南](./ADK_INTEGRATION_GUIDE.md)
- [API设计文档](../api/openapi_specification.yaml)

### 12.2 配置示例
```env
# .env.agent
MODEL=claude-3-opus
JINA_API_KEY=your_jina_key
TENDATA_API_KEY=your_tendata_key
TEMPERATURE=0.7
MAX_TOKENS=2000
```

### 12.3 常见问题
1. **Q: Agent服务启动失败**
   A: 检查环境变量配置，确保API密钥正确

2. **Q: SSE连接频繁断开**
   A: 检查nginx配置，确保支持长连接

3. **Q: 响应时间过长**
   A: 优化提示词，减少不必要的工具调用

---

*本文档持续更新中，最后更新时间：2025-01-09*