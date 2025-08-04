# Google ADK 集成指南 - TradeFlow B2B 贸易智能助手

## 目录
1. [概述](#概述)
2. [架构设计](#架构设计)
3. [环境准备](#环境准备)
4. [Agent 开发指南](#agent-开发指南)
5. [后端集成](#后端集成)
6. [前端集成](#前端集成)
7. [部署方案](#部署方案)
8. [多语言支持](#多语言支持)
9. [安全和监控](#安全和监控)
10. [最佳实践](#最佳实践)

## 概述

Google Agent Development Kit (ADK) 是一个开源的、代码优先的 Python 工具包，用于构建、评估和部署复杂的 AI Agent。本指南将详细介绍如何将 Google ADK 集成到 TradeFlow 应用中，为 B2B 贸易用户提供智能化的买家开发、供应商匹配和市场分析服务。

### 为什么选择 Google ADK

- **灵活性高**：支持自定义工具和复杂的业务逻辑
- **与 Google 生态系统深度集成**：优化支持 Gemini 模型和 Vertex AI
- **生产就绪**：内置部署、监控和扩展能力
- **开源免费**：降低技术成本，社区支持活跃

## 架构设计

### 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                     TradeFlow Frontend (React)                   │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────┐ │
│  │ Chat UI    │  │ Buyer UI   │  │Supplier UI │  │Analytics │ │
│  └────────────┘  └────────────┘  └────────────┘  └──────────┘ │
└─────────────────────────────┬───────────────────────────────────┘
                              │ HTTPS/WebSocket
┌─────────────────────────────▼───────────────────────────────────┐
│                    FastAPI Backend Service                       │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────┐ │
│  │Auth Module │  │Agent Gateway│  │Business    │  │Data      │ │
│  │           │  │Service     │  │Logic       │  │Service   │ │
│  └────────────┘  └────────────┘  └────────────┘  └──────────┘ │
└─────────────────────────────┬───────────────────────────────────┘
                              │ gRPC/REST
┌─────────────────────────────▼───────────────────────────────────┐
│                    Google ADK Agent Layer                        │
│  ┌────────────────┐  ┌────────────────┐  ┌─────────────────┐  │
│  │Buyer Development│  │Supplier Match  │  │Market Analysis  │  │
│  │Agent           │  │Agent           │  │Agent            │  │
│  └────────────────┘  └────────────────┘  └─────────────────┘  │
│         │                    │                    │             │
│  ┌──────┴──────────────────┴────────────────────┴───────────┐ │
│  │                    Shared Tools & Services                 │ │
│  │ • TradeDataSearchTool    • ComplianceCheckTool           │ │
│  │ • TranslationTool        • DocumentGenerationTool        │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────┬───────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│                    External Services & Data                      │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────┐ │
│  │PostgreSQL  │  │MongoDB     │  │Redis Cache │  │Trade APIs│ │
│  └────────────┘  └────────────┘  └────────────┘  └──────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 核心组件说明

1. **Agent Gateway Service**：负责请求路由、意图识别和 Agent 调度
2. **专业 Agent**：
   - Buyer Development Agent：处理买家开发相关任务
   - Supplier Matching Agent：供应商匹配和评估
   - Market Analysis Agent：市场趋势和数据分析
3. **共享工具层**：可复用的业务工具和服务
4. **数据层**：持久化存储和缓存服务

## 环境准备

### 1. 系统要求

```bash
# Python 版本要求
Python 3.9+

# 必需的系统依赖
- Docker 20.10+
- gcloud CLI
- Poetry 或 pip
```

### 2. 安装 Google ADK

```bash
# 使用 pip 安装
pip install google-genai google-cloud-aiplatform[adk,agent_engines]

# 或使用 Poetry
poetry add google-genai google-cloud-aiplatform[adk,agent_engines]
```

### 3. Google Cloud 配置

```bash
# 设置环境变量
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"
export GOOGLE_GENAI_USE_VERTEXAI=true

# 认证配置
gcloud auth application-default login
gcloud config set project $GOOGLE_CLOUD_PROJECT
```

### 4. 项目结构

```
TradeFlowProduct/
├── src/
│   ├── backend/
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── buyer_agent.py
│   │   │   ├── supplier_agent.py
│   │   │   └── market_agent.py
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   ├── trade_data_tool.py
│   │   │   ├── translation_tool.py
│   │   │   └── compliance_tool.py
│   │   ├── services/
│   │   │   ├── agent_gateway.py
│   │   │   └── session_manager.py
│   │   └── main.py
│   └── frontend/
├── deployment/
│   ├── Dockerfile
│   └── k8s/
└── tests/
```

## Agent 开发指南

### 1. 买家开发 Agent

```python
# src/backend/agents/buyer_agent.py
from google.adk.agents import LlmAgent
from google.adk.tools import BaseTool
from typing import Dict, List, Any
import json

class BuyerDevelopmentAgent:
    """专门用于 B2B 贸易买家开发的智能 Agent"""
    
    def __init__(self):
        # 初始化工具
        self.tools = [
            TradeDataSearchTool(),
            BuyerRecommendationTool(),
            MarketInsightTool(),
            EmailGeneratorTool()
        ]
        
        # 创建 Agent
        self.agent = LlmAgent(
            model='gemini-2.0-flash',
            name='buyer_development_agent',
            instruction=self._get_instruction(),
            tools=self.tools,
            generate_content_config={
                "temperature": 0.7,
                "max_output_tokens": 2048,
            }
        )
    
    def _get_instruction(self) -> str:
        return """
        你是 TradeFlow 的专业买家开发助手，专门帮助中国制造商和出口商开发海外买家。
        
        你的核心能力包括：
        1. 根据产品信息智能匹配潜在买家
        2. 分析目标市场需求和趋势
        3. 生成专业的开发信和商务邮件
        4. 提供市场进入策略建议
        5. 评估买家信用和采购潜力
        
        工作原则：
        - 始终基于真实的贸易数据进行分析
        - 考虑文化差异和商务礼仪
        - 提供可执行的具体建议
        - 保持专业和友好的语气
        
        当用户描述他们的产品和目标市场时，你需要：
        1. 理解产品特性和竞争优势
        2. 分析目标市场的需求特征
        3. 推荐最匹配的潜在买家
        4. 提供联系策略和谈判要点
        """
    
    async def process_request(
        self, 
        user_message: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """处理用户请求"""
        # 构建完整的上下文
        enhanced_context = {
            "user_profile": context.get("user_profile", {}),
            "product_info": context.get("product_info", {}),
            "market_preference": context.get("market_preference", {})
        }
        
        # 调用 Agent
        response = await self.agent.run_async(
            message=user_message,
            context=enhanced_context
        )
        
        return {
            "response": response.content,
            "recommendations": self._extract_recommendations(response),
            "next_steps": self._generate_next_steps(response)
        }
```

### 2. 自定义工具开发

```python
# src/backend/tools/trade_data_tool.py
from google.adk.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
import asyncio

class TradeDataSearchParams(BaseModel):
    """贸易数据搜索参数"""
    product_category: str = Field(description="产品类别，如 'LED lighting', 'textiles'")
    target_market: str = Field(description="目标市场，如 'USA', 'Germany', 'Japan'")
    trade_type: str = Field(description="贸易类型：'import' 或 'export'")
    date_range: Optional[str] = Field(default="last_12_months", description="时间范围")

class TradeDataSearchTool(BaseTool):
    """全球贸易数据搜索工具"""
    
    name = "trade_data_search"
    description = "搜索全球贸易数据，包括进出口统计、价格趋势、市场份额等"
    parameters_model = TradeDataSearchParams
    
    async def run_async(
        self, 
        *, 
        args: Dict[str, Any], 
        tool_context: Any
    ) -> Dict[str, Any]:
        """执行贸易数据搜索"""
        # 参数验证
        params = TradeDataSearchParams(**args)
        
        # 模拟数据库查询（实际应连接真实数据源）
        trade_data = await self._query_trade_database(
            product=params.product_category,
            market=params.target_market,
            trade_type=params.trade_type
        )
        
        # 数据分析和整理
        analysis_result = self._analyze_trade_data(trade_data)
        
        return {
            "status": "success",
            "data": {
                "market_size": analysis_result["market_size"],
                "growth_rate": analysis_result["growth_rate"],
                "top_importers": analysis_result["top_importers"],
                "price_trends": analysis_result["price_trends"],
                "seasonal_patterns": analysis_result["seasonal_patterns"],
                "recommendations": self._generate_recommendations(analysis_result)
            }
        }
    
    async def _query_trade_database(
        self, 
        product: str, 
        market: str, 
        trade_type: str
    ) -> List[Dict]:
        """查询贸易数据库"""
        # 实际实现应连接到真实的贸易数据API
        # 这里返回模拟数据
        await asyncio.sleep(0.5)  # 模拟网络延迟
        
        return [
            {
                "year": 2024,
                "month": 1,
                "volume": 150000,
                "value": 4500000,
                "unit_price": 30,
                "top_suppliers": ["China", "Vietnam", "India"]
            }
            # ... 更多数据
        ]
```

### 3. 供应商匹配 Agent

```python
# src/backend/agents/supplier_agent.py
class SupplierMatchingAgent:
    """供应商智能匹配 Agent"""
    
    def __init__(self):
        self.agent = LlmAgent(
            model='gemini-2.0-flash',
            name='supplier_matching_agent',
            instruction="""
            你是专业的供应商匹配专家，帮助采购商找到最合适的供应商。
            
            核心任务：
            1. 理解采购需求的技术规格和商务要求
            2. 从供应商数据库中匹配最合适的候选
            3. 评估供应商的能力、信誉和风险
            4. 提供详细的对比分析和推荐理由
            
            评估维度：
            - 产品质量和技术能力
            - 价格竞争力
            - 生产能力和交期保障
            - 认证和合规性
            - 历史合作记录和信誉
            - 地理位置和物流便利性
            """,
            tools=[
                SupplierSearchTool(),
                SupplierEvaluationTool(),
                RiskAssessmentTool(),
                PriceComparisonTool()
            ]
        )
```

## 后端集成

### 1. Agent Gateway 服务

```python
# src/backend/services/agent_gateway.py
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
import asyncio
from enum import Enum

class AgentType(str, Enum):
    BUYER = "buyer_development"
    SUPPLIER = "supplier_matching"
    MARKET = "market_analysis"
    GENERAL = "general_assistant"

class ChatRequest(BaseModel):
    message: str
    agent_type: Optional[AgentType] = None
    context: Optional[Dict[str, Any]] = {}
    session_id: Optional[str] = None

class AgentGatewayService:
    """Agent 网关服务，负责请求路由和管理"""
    
    def __init__(self):
        # 初始化所有 Agent
        self.agents = {
            AgentType.BUYER: BuyerDevelopmentAgent(),
            AgentType.SUPPLIER: SupplierMatchingAgent(),
            AgentType.MARKET: MarketAnalysisAgent()
        }
        
        # 意图分类器
        self.intent_classifier = IntentClassifier()
        
        # 会话管理器
        self.session_manager = SessionManager()
    
    async def route_request(
        self, 
        request: ChatRequest,
        user_id: str
    ) -> Dict[str, Any]:
        """路由用户请求到合适的 Agent"""
        
        # 获取或创建会话
        session = await self.session_manager.get_or_create_session(
            session_id=request.session_id,
            user_id=user_id
        )
        
        # 如果没有指定 Agent 类型，进行意图识别
        if not request.agent_type:
            intent_result = await self.intent_classifier.classify(
                message=request.message,
                context=session.context
            )
            request.agent_type = intent_result["agent_type"]
        
        # 获取对应的 Agent
        agent = self.agents.get(request.agent_type)
        if not agent:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown agent type: {request.agent_type}"
            )
        
        # 处理请求
        try:
            response = await agent.process_request(
                user_message=request.message,
                context={
                    **session.context,
                    **request.context,
                    "user_id": user_id,
                    "session_id": session.id
                }
            )
            
            # 更新会话上下文
            await self.session_manager.update_context(
                session_id=session.id,
                new_context=response.get("updated_context", {})
            )
            
            return {
                "status": "success",
                "agent_type": request.agent_type,
                "response": response["response"],
                "metadata": {
                    "session_id": session.id,
                    "recommendations": response.get("recommendations", []),
                    "next_steps": response.get("next_steps", [])
                }
            }
            
        except Exception as e:
            # 错误处理和日志记录
            logger.error(f"Agent processing error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Agent processing failed"
            )
```

### 2. FastAPI 应用集成

```python
# src/backend/main.py
from fastapi import FastAPI, WebSocket, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

# 生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化
    app.state.agent_gateway = AgentGatewayService()
    yield
    # 关闭时清理
    await app.state.agent_gateway.shutdown()

# 创建应用
app = FastAPI(
    title="TradeFlow API",
    description="B2B Trade Intelligence Assistant API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React 前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 路由
@app.post("/api/v1/chat")
async def chat_endpoint(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """统一的对话接口"""
    gateway = app.state.agent_gateway
    return await gateway.route_request(request, current_user.id)

@app.post("/api/v1/buyers/recommend")
async def recommend_buyers(
    product_info: ProductInfo,
    target_markets: List[str],
    current_user: User = Depends(get_current_user)
):
    """买家推荐专用接口"""
    gateway = app.state.agent_gateway
    
    request = ChatRequest(
        message=f"为我的{product_info.name}产品推荐{', '.join(target_markets)}市场的买家",
        agent_type=AgentType.BUYER,
        context={
            "product_info": product_info.dict(),
            "target_markets": target_markets
        }
    )
    
    return await gateway.route_request(request, current_user.id)

# WebSocket 支持（用于流式响应）
@app.websocket("/ws/agent-chat")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str
):
    """WebSocket 连接用于实时对话"""
    await websocket.accept()
    
    try:
        # 验证 token
        user = await verify_websocket_token(token)
        
        # 创建专用的流式 Agent 处理器
        stream_handler = StreamingAgentHandler(
            agent_gateway=app.state.agent_gateway,
            websocket=websocket,
            user_id=user.id
        )
        
        await stream_handler.handle_connection()
        
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })
    finally:
        await websocket.close()
```

### 3. 流式响应处理

```python
# src/backend/services/streaming_handler.py
class StreamingAgentHandler:
    """处理 Agent 的流式响应"""
    
    def __init__(self, agent_gateway, websocket, user_id):
        self.agent_gateway = agent_gateway
        self.websocket = websocket
        self.user_id = user_id
    
    async def handle_connection(self):
        """处理 WebSocket 连接"""
        while True:
            try:
                # 接收消息
                data = await self.websocket.receive_json()
                
                if data["type"] == "chat":
                    await self._handle_chat_message(data)
                elif data["type"] == "ping":
                    await self.websocket.send_json({"type": "pong"})
                
            except Exception as e:
                await self.websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })
                break
    
    async def _handle_chat_message(self, data):
        """处理聊天消息并流式返回"""
        request = ChatRequest(**data["payload"])
        
        # 获取对应的 Agent
        agent = self.agent_gateway.agents.get(request.agent_type)
        
        # 创建流式响应
        async for chunk in agent.stream_response(
            message=request.message,
            context=request.context
        ):
            await self.websocket.send_json({
                "type": "stream",
                "chunk": chunk
            })
        
        # 发送完成信号
        await self.websocket.send_json({
            "type": "complete"
        })
```

## 前端集成

### 1. React Agent 组件

```typescript
// src/frontend/components/AgentChat.tsx
import React, { useState, useEffect, useRef } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import { AgentType, ChatMessage } from '../types';

interface AgentChatProps {
  agentType?: AgentType;
  onRecommendations?: (recommendations: any[]) => void;
}

export const AgentChat: React.FC<AgentChatProps> = ({ 
  agentType = 'general_assistant',
  onRecommendations 
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const { sendMessage, lastMessage, readyState } = useWebSocket(
    '/ws/agent-chat',
    {
      onOpen: () => console.log('WebSocket connected'),
      onMessage: (event) => handleWebSocketMessage(event),
      onError: (error) => console.error('WebSocket error:', error)
    }
  );
  
  const handleWebSocketMessage = (event: MessageEvent) => {
    const data = JSON.parse(event.data);
    
    switch (data.type) {
      case 'stream':
        // 处理流式响应
        appendToLastMessage(data.chunk);
        break;
        
      case 'complete':
        setIsLoading(false);
        if (data.recommendations && onRecommendations) {
          onRecommendations(data.recommendations);
        }
        break;
        
      case 'error':
        console.error('Agent error:', data.message);
        setIsLoading(false);
        break;
    }
  };
  
  const sendChatMessage = async () => {
    if (!inputValue.trim()) return;
    
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue,
      timestamp: new Date()
    };
    
    setMessages([...messages, userMessage]);
    setInputValue('');
    setIsLoading(true);
    
    // 发送到 WebSocket
    sendMessage({
      type: 'chat',
      payload: {
        message: inputValue,
        agent_type: agentType,
        session_id: sessionStorage.getItem('chat_session_id')
      }
    });
  };
  
  const appendToLastMessage = (chunk: string) => {
    setMessages(prev => {
      const newMessages = [...prev];
      const lastMessage = newMessages[newMessages.length - 1];
      
      if (lastMessage && lastMessage.role === 'assistant') {
        lastMessage.content += chunk;
      } else {
        newMessages.push({
          id: Date.now().toString(),
          role: 'assistant',
          content: chunk,
          timestamp: new Date()
        });
      }
      
      return newMessages;
    });
  };
  
  return (
    <div className="agent-chat-container">
      <div className="chat-header">
        <h3>{getAgentTitle(agentType)}</h3>
        <span className={`status ${readyState === 1 ? 'online' : 'offline'}`}>
          {readyState === 1 ? '在线' : '离线'}
        </span>
      </div>
      
      <div className="messages-container">
        {messages.map(message => (
          <MessageBubble key={message.id} message={message} />
        ))}
        {isLoading && <LoadingIndicator />}
      </div>
      
      <div className="input-container">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendChatMessage()}
          placeholder="输入您的问题..."
          disabled={isLoading || readyState !== 1}
        />
        <button 
          onClick={sendChatMessage}
          disabled={isLoading || readyState !== 1}
        >
          发送
        </button>
      </div>
    </div>
  );
};
```

### 2. 买家推荐组件

```typescript
// src/frontend/components/BuyerRecommendations.tsx
import React, { useState } from 'react';
import { api } from '../services/api';
import { BuyerCard } from './BuyerCard';

export const BuyerRecommendations: React.FC = () => {
  const [productInfo, setProductInfo] = useState({
    name: '',
    category: '',
    description: '',
    price_range: '',
    moq: ''
  });
  
  const [targetMarkets, setTargetMarkets] = useState<string[]>([]);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  
  const handleGetRecommendations = async () => {
    setIsLoading(true);
    
    try {
      const response = await api.post('/api/v1/buyers/recommend', {
        product_info: productInfo,
        target_markets: targetMarkets
      });
      
      setRecommendations(response.data.recommendations);
    } catch (error) {
      console.error('Failed to get recommendations:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="buyer-recommendations">
      <div className="input-section">
        <h3>产品信息</h3>
        <form>
          <input
            type="text"
            placeholder="产品名称"
            value={productInfo.name}
            onChange={(e) => setProductInfo({
              ...productInfo,
              name: e.target.value
            })}
          />
          {/* 其他表单字段 */}
        </form>
        
        <div className="market-selection">
          <h4>目标市场</h4>
          <MarketSelector
            selected={targetMarkets}
            onChange={setTargetMarkets}
          />
        </div>
        
        <button 
          onClick={handleGetRecommendations}
          disabled={isLoading}
        >
          获取买家推荐
        </button>
      </div>
      
      <div className="recommendations-section">
        {isLoading ? (
          <LoadingSpinner />
        ) : (
          <div className="buyer-grid">
            {recommendations.map((buyer, index) => (
              <BuyerCard 
                key={index} 
                buyer={buyer}
                onContact={(buyer) => handleContactBuyer(buyer)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
```

## 部署方案

### 1. Vertex AI Agent Engine 部署（推荐）

```python
# deployment/deploy_to_vertex_ai.py
from vertexai.preview import reasoning_engines
from google.cloud import aiplatform
import os

def deploy_to_agent_engine():
    """部署到 Vertex AI Agent Engine"""
    
    # 初始化 Vertex AI
    aiplatform.init(
        project=os.environ["GOOGLE_CLOUD_PROJECT"],
        location=os.environ["GOOGLE_CLOUD_LOCATION"]
    )
    
    # 导入 Agent
    from src.backend.agents import BuyerDevelopmentAgent
    
    # 创建 Agent 实例
    buyer_agent = BuyerDevelopmentAgent()
    
    # 包装为 ADK App
    app = reasoning_engines.AdkApp(
        agent=buyer_agent.agent,
        enable_tracing=True,
    )
    
    # 部署到 Agent Engine
    remote_app = reasoning_engines.create(
        reasoning_engine=app,
        requirements=[
            "google-cloud-aiplatform[adk,agent_engines]",
            "fastapi",
            "pydantic",
            "asyncio"
        ],
        display_name="tradeflow-buyer-agent",
        description="TradeFlow Buyer Development Agent"
    )
    
    print(f"Deployed agent: {remote_app.resource_name}")
    return remote_app

if __name__ == "__main__":
    deploy_to_agent_engine()
```

### 2. Cloud Run 部署

```dockerfile
# deployment/Dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY pyproject.toml poetry.lock ./

# 安装 Python 依赖
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

# 复制应用代码
COPY src/ ./src/

# 设置环境变量
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# 启动命令
CMD ["uvicorn", "src.backend.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

```bash
# 部署脚本
#!/bin/bash

# 构建镜像
gcloud builds submit --tag gcr.io/$GOOGLE_CLOUD_PROJECT/tradeflow-backend

# 部署到 Cloud Run
gcloud run deploy tradeflow-backend \
  --image gcr.io/$GOOGLE_CLOUD_PROJECT/tradeflow-backend \
  --platform managed \
  --region $GOOGLE_CLOUD_LOCATION \
  --allow-unauthenticated \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT,GOOGLE_GENAI_USE_VERTEXAI=true"
```

### 3. Kubernetes 部署

```yaml
# deployment/k8s/agent-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tradeflow-agents
spec:
  replicas: 3
  selector:
    matchLabels:
      app: tradeflow-agents
  template:
    metadata:
      labels:
        app: tradeflow-agents
    spec:
      containers:
      - name: agent-service
        image: gcr.io/PROJECT_ID/tradeflow-backend:latest
        ports:
        - containerPort: 8080
        env:
        - name: GOOGLE_CLOUD_PROJECT
          value: "your-project-id"
        - name: GOOGLE_GENAI_USE_VERTEXAI
          value: "true"
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 30
---
apiVersion: v1
kind: Service
metadata:
  name: tradeflow-agents-service
spec:
  selector:
    app: tradeflow-agents
  ports:
    - port: 80
      targetPort: 8080
  type: LoadBalancer
```

## 多语言支持

### 1. 多语言 Agent 配置

```python
# src/backend/agents/multilingual_agent.py
class MultilingualAgentFactory:
    """多语言 Agent 工厂"""
    
    @staticmethod
    def create_buyer_agent(language: str = "zh-CN"):
        """创建指定语言的买家开发 Agent"""
        
        instructions = {
            "zh-CN": """
            你是 TradeFlow 的专业买家开发助手，专门帮助中国制造商开发海外买家。
            请用中文与用户交流，但在生成英文商务信函时使用专业的商务英语。
            """,
            "en-US": """
            You are TradeFlow's professional buyer development assistant, 
            helping manufacturers find and develop overseas buyers.
            """,
            "es-ES": """
            Eres el asistente profesional de desarrollo de compradores de TradeFlow,
            ayudando a los fabricantes a encontrar compradores internacionales.
            """
        }
        
        return LlmAgent(
            model='gemini-2.0-flash',
            name=f'buyer_agent_{language}',
            instruction=instructions.get(language, instructions["en-US"]),
            tools=[
                TradeDataSearchTool(),
                TranslationTool(target_languages=["en", "zh", "es", "ar"]),
                CulturalAdaptationTool()
            ]
        )
```

### 2. 文化适配策略

```python
# src/backend/tools/cultural_adaptation_tool.py
class CulturalAdaptationTool(BaseTool):
    """文化适配工具，调整商务沟通风格"""
    
    name = "cultural_adaptation"
    description = "根据目标市场的文化背景调整商务沟通内容和风格"
    
    CULTURAL_RULES = {
        "US": {
            "communication_style": "direct",
            "formality": "moderate",
            "relationship_building": "task-focused",
            "negotiation": "win-win oriented"
        },
        "JP": {
            "communication_style": "indirect",
            "formality": "high",
            "relationship_building": "relationship-first",
            "negotiation": "consensus-seeking"
        },
        "DE": {
            "communication_style": "direct",
            "formality": "high",
            "relationship_building": "professional",
            "negotiation": "detail-oriented"
        }
    }
    
    async def adapt_message(
        self, 
        message: str, 
        target_culture: str,
        message_type: str = "email"
    ) -> str:
        """调整消息以适应目标文化"""
        rules = self.CULTURAL_RULES.get(target_culture, {})
        
        # 应用文化规则调整消息
        adapted_message = message
        
        if rules.get("formality") == "high":
            adapted_message = self._increase_formality(adapted_message)
        
        if rules.get("communication_style") == "indirect":
            adapted_message = self._make_indirect(adapted_message)
        
        return adapted_message
```

## 安全和监控

### 1. 认证授权集成

```python
# src/backend/security/auth_middleware.py
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """验证 JWT Token"""
    token = credentials.credentials
    
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

# 在 Agent 调用中使用
@app.post("/api/v1/chat", dependencies=[Depends(verify_token)])
async def chat_endpoint(request: ChatRequest):
    # Agent 处理逻辑
    pass
```

### 2. 性能监控

```python
# src/backend/monitoring/agent_monitor.py
from prometheus_client import Counter, Histogram, Gauge
import time

# 定义监控指标
agent_requests_total = Counter(
    'agent_requests_total', 
    'Total number of agent requests',
    ['agent_type', 'status']
)

agent_response_time = Histogram(
    'agent_response_time_seconds',
    'Agent response time in seconds',
    ['agent_type']
)

active_sessions = Gauge(
    'active_agent_sessions',
    'Number of active agent sessions'
)

class AgentMonitor:
    """Agent 性能监控"""
    
    @staticmethod
    def track_request(agent_type: str):
        """追踪请求"""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                
                try:
                    result = await func(*args, **kwargs)
                    agent_requests_total.labels(
                        agent_type=agent_type,
                        status='success'
                    ).inc()
                    return result
                    
                except Exception as e:
                    agent_requests_total.labels(
                        agent_type=agent_type,
                        status='error'
                    ).inc()
                    raise e
                    
                finally:
                    duration = time.time() - start_time
                    agent_response_time.labels(
                        agent_type=agent_type
                    ).observe(duration)
            
            return wrapper
        return decorator
```

### 3. 审计日志

```python
# src/backend/audit/audit_logger.py
import json
from datetime import datetime
from typing import Dict, Any

class AuditLogger:
    """Agent 交互审计日志"""
    
    def __init__(self, storage_backend):
        self.storage = storage_backend
    
    async def log_agent_interaction(
        self,
        user_id: str,
        agent_type: str,
        request: Dict[str, Any],
        response: Dict[str, Any],
        metadata: Dict[str, Any] = {}
    ):
        """记录 Agent 交互日志"""
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "agent_type": agent_type,
            "request": {
                "message": request.get("message"),
                "context": request.get("context", {})
            },
            "response": {
                "content": response.get("content"),
                "recommendations": len(response.get("recommendations", []))
            },
            "metadata": {
                "ip_address": metadata.get("ip_address"),
                "session_id": metadata.get("session_id"),
                "processing_time": metadata.get("processing_time"),
                "tokens_used": metadata.get("tokens_used")
            }
        }
        
        await self.storage.save(audit_entry)
```

## 最佳实践

### 1. Agent 开发建议

1. **模块化设计**
   - 将复杂任务分解为多个专门的 Agent
   - 使用共享工具库避免代码重复
   - 保持 Agent 指令清晰、具体

2. **错误处理**
   ```python
   try:
       response = await agent.run_async(message)
   except RateLimitError:
       # 处理速率限制
       await asyncio.sleep(60)
       response = await agent.run_async(message)
   except Exception as e:
       # 降级到备用逻辑
       response = await fallback_handler(message)
   ```

3. **上下文管理**
   - 限制上下文大小，避免 token 超限
   - 定期清理无关的历史对话
   - 使用结构化数据而非长文本

### 2. 性能优化

1. **缓存策略**
   ```python
   from functools import lru_cache
   import redis
   
   redis_client = redis.Redis()
   
   @lru_cache(maxsize=1000)
   async def get_cached_recommendation(
       product_hash: str,
       market: str
   ):
       # 检查 Redis 缓存
       cache_key = f"rec:{product_hash}:{market}"
       cached = redis_client.get(cache_key)
       
       if cached:
           return json.loads(cached)
       
       # 生成新推荐
       recommendations = await generate_recommendations(...)
       
       # 缓存结果（24小时）
       redis_client.setex(
           cache_key, 
           86400, 
           json.dumps(recommendations)
       )
       
       return recommendations
   ```

2. **并发处理**
   ```python
   async def batch_process_requests(requests: List[ChatRequest]):
       """批量处理请求以提高效率"""
       tasks = []
       for request in requests:
           task = asyncio.create_task(
               agent_gateway.route_request(request)
           )
           tasks.append(task)
       
       results = await asyncio.gather(*tasks)
       return results
   ```

### 3. 测试策略

```python
# tests/test_buyer_agent.py
import pytest
from unittest.mock import Mock, patch

@pytest.mark.asyncio
async def test_buyer_recommendation():
    """测试买家推荐功能"""
    agent = BuyerDevelopmentAgent()
    
    # 模拟贸易数据
    with patch('tools.TradeDataSearchTool.run_async') as mock_search:
        mock_search.return_value = {
            "top_importers": ["Company A", "Company B"],
            "market_size": "$100M"
        }
        
        response = await agent.process_request(
            user_message="推荐美国市场的LED灯具买家",
            context={"product": "LED Panel Light"}
        )
        
        assert "recommendations" in response
        assert len(response["recommendations"]) > 0
```

### 4. 常见问题解决

**Q: Agent 响应速度慢怎么办？**
A: 
1. 使用流式响应减少感知延迟
2. 实施智能缓存策略
3. 优化 prompt 长度和复杂度
4. 考虑使用更快的模型（如 Gemini Flash）

**Q: 如何处理 Agent 幻觉问题？**
A:
1. 使用 Grounding 技术连接真实数据源
2. 实施事实验证工具
3. 在 prompt 中强调基于事实回答
4. 提供清晰的数据引用

**Q: 如何确保数据安全？**
A:
1. 实施端到端加密
2. 使用 VPC 内部通信
3. 定期审计和日志记录
4. 遵循 GDPR 等合规要求

## 总结

通过集成 Google ADK，TradeFlow 将获得：

1. **智能化升级**：专业的 AI Agent 提供贸易咨询和决策支持
2. **用户体验提升**：自然语言交互，降低使用门槛
3. **业务效率提升**：自动化买家开发和供应商匹配
4. **全球化能力**：多语言支持和文化适配
5. **可扩展架构**：模块化设计，易于添加新功能

持续优化和迭代将确保系统始终保持竞争优势，为用户创造更大价值。

---

*最后更新：2024年8月*  
*版本：1.0.0*