# TradeFlow MVP 技术设计文档

## 目录
1. [执行摘要](#执行摘要)
2. [系统架构设计](#系统架构设计)
3. [数据架构设计](#数据架构设计)
4. [API设计](#api设计)
5. [Google ADK Agent开发方案](#google-adk-agent开发方案)
6. [第三方登录集成](#第三方登录集成)
7. [多语言支持策略](#多语言支持策略)
8. [部署架构](#部署架构)
9. [性能优化策略](#性能优化策略)
10. [测试方案](#测试方案)
11. [风险与缓解措施](#风险与缓解措施)
12. [实施计划](#实施计划)

---

## 执行摘要

### 项目背景
TradeFlow是一款基于AI的B2B贸易智能助手，通过自然语言交互帮助用户完成买家开发、供应商采购等贸易业务。本文档为3-4个月MVP版本的技术设计方案。

### 核心技术决策
- **AI框架**: Google ADK (Agent Development Kit)
- **后端**: FastAPI (Python)
- **前端**: React
- **数据库**: PostgreSQL（结构化数据） + MongoDB（对话数据） + Redis（缓存）
- **认证**: OAuth 2.0 (Google, GitHub)
- **部署**: Docker + Cloud Run

### 设计原则
1. **简洁实用**: 避免过度工程化，专注MVP核心功能
2. **可扩展性**: 模块化设计，便于后续迭代
3. **用户体验**: 优先保证响应速度和易用性
4. **安全合规**: 遵循数据安全和隐私保护标准

---

## 系统架构设计

### 整体架构图

```mermaid
graph TD
    subgraph "Frontend Layer"
        A[React App SPA]
        B[i18n Support] 
        C[OAuth Client]
        D1[File Preview Panel]
    end
    
    subgraph "API Gateway Layer"
        D[FastAPI REST API]
        E[SSE Handler]
        F[Auth Middleware]
    end
    
    subgraph "Business Logic Layer"
        G[Agent Gateway Service]
        H[Business Services]
        I[Payment Service]
        P[File Service]
    end
    
    subgraph "Google ADK Agent Layer"
        J[Buyer Agent]
        K[Supplier Agent]
        L[Market Analysis Agent]
    end
    
    subgraph "Data Layer"
        M[PostgreSQL<br/>Structured + Files]
        N[MongoDB<br/>Dialogues]
        O[Redis<br/>Cache]
        Q[MinIO<br/>Object Storage]
    end
    
    A --> D
    A -.-> E
    B --> D
    C --> D
    D1 --> D
    
    D --> G
    D --> P
    E --> G
    F --> D
    F --> E
    
    G --> J
    G --> K
    G --> L
    H --> M
    I --> M
    P --> M
    P --> Q
    
    J --> N
    K --> N
    L --> N
    J --> P
    K --> P
    L --> P
    G --> O
```

### 核心组件说明

#### 1. Frontend Layer
- **React SPA**: 单页应用，提供流畅的用户体验
- **i18n Support**: 基于React-i18next的多语言支持
- **OAuth Client**: 处理Google/GitHub第三方登录
- **File Preview Panel**: 右侧文件预览面板，支持对话中生成文件的预览和管理

#### 2. API Gateway Layer
- **FastAPI REST**: 提供RESTful API接口
- **SSE Handler**: 支持实时对话流式响应
- **Auth Middleware**: JWT token验证和权限控制

#### 3. Business Logic Layer
- **Agent Gateway Service**: 统一的Agent调度和管理
- **Business Services**: 用户管理、产品管理、交易管理等
- **Payment Service**: Stripe支付集成
- **File Service**: 文件上传、存储、预览和管理服务，支持多种文件格式

#### 4. Google ADK Agent Layer
- **Buyer Agent**: 买家开发智能助手
- **Supplier Agent**: 供应商匹配助手
- **Market Analysis Agent**: 市场分析助手

#### 5. Data Layer
- **PostgreSQL**: 存储用户、企业、产品等结构化数据，以及文件元数据
- **MongoDB**: 存储对话历史、Agent上下文等非结构化数据
- **Redis**: 会话缓存、API限流、热点数据缓存
- **MinIO**: 对象存储服务，存储Agent生成的文件和用户上传的文档

---

## 数据架构设计

### PostgreSQL Schema（结构化数据）

```sql
-- 用户表（支持OAuth）
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE,
    name VARCHAR(255),
    avatar_url TEXT,
    auth_provider VARCHAR(50), -- 'google', 'github', 'email'
    auth_provider_id VARCHAR(255),
    language_preference VARCHAR(10) DEFAULT 'en',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 企业认证表
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    company_name VARCHAR(255) NOT NULL,
    company_type VARCHAR(50), -- 'manufacturer', 'trader', 'buyer'
    country VARCHAR(2),
    business_license TEXT,
    verification_status VARCHAR(50) DEFAULT 'pending',
    trust_score INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 产品表
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id),
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    description TEXT,
    hs_code VARCHAR(20),
    price_range JSONB,
    moq INTEGER,
    images JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 使用记录表
CREATE TABLE usage_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    action_type VARCHAR(50), -- 'chat', 'recommendation', 'export'
    tokens_used INTEGER,
    cost DECIMAL(10, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 订阅和支付表
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    stripe_customer_id VARCHAR(255),
    stripe_subscription_id VARCHAR(255),
    plan_type VARCHAR(50),
    credits_remaining INTEGER,
    status VARCHAR(50),
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### MongoDB Collections（非结构化数据）

```javascript
// 对话集合
conversations: {
  _id: ObjectId,
  user_id: String,
  session_id: String,
  agent_type: String, // 'buyer', 'supplier', 'market'
  messages: [
    {
      role: String, // 'user', 'assistant'
      content: String,
      timestamp: Date,
      metadata: {
        tokens: Number,
        model: String,
        tools_used: Array
      }
    }
  ],
  context: {
    user_profile: Object,
    product_info: Object,
    preferences: Object
  },
  created_at: Date,
  updated_at: Date
}

// Agent会话状态
agent_sessions: {
  _id: ObjectId,
  session_id: String,
  user_id: String,
  agent_type: String,
  state: Object, // Agent的内部状态
  memory: Array, // 短期记忆
  last_activity: Date,
  expires_at: Date
}

// AI推荐结果
recommendations: {
  _id: ObjectId,
  user_id: String,
  type: String, // 'buyer', 'supplier'
  query: Object,
  results: [
    {
      name: String,
      score: Number,
      details: Object,
      contact_info: Object,
      reasoning: String
    }
  ],
  metadata: {
    processing_time: Number,
    data_sources: Array,
    confidence_score: Number
  },
  created_at: Date
}

// 用户反馈
user_feedback: {
  _id: ObjectId,
  user_id: String,
  reference_id: String, // 关联的推荐或对话ID
  type: String, // 'recommendation', 'conversation'
  rating: Number,
  comment: String,
  created_at: Date
}
```

### Redis缓存结构

```
# 用户会话
session:{user_id} -> {
  token: JWT,
  user_data: {...},
  expires_at: timestamp
}

# API限流
rate_limit:{user_id}:{endpoint} -> count

# 热点数据缓存
cache:products:{category} -> [products...]
cache:buyers:{market} -> [buyers...]

# Agent对话上下文（临时）
agent_context:{session_id} -> {
  messages: [...],
  state: {...}
}
```

---

## API设计

### RESTful API端点

#### 认证相关
```
POST   /api/v1/auth/oauth/{provider}     # OAuth登录
POST   /api/v1/auth/refresh              # 刷新Token
POST   /api/v1/auth/logout               # 登出
GET    /api/v1/auth/me                   # 获取当前用户信息
```

#### Agent对话
```
POST   /api/v1/chat                      # 统一对话入口
GET    /api/v1/chat/history              # 获取对话历史
DELETE /api/v1/chat/session/{id}         # 删除会话
```

#### 业务功能
```
# 买家开发
POST   /api/v1/buyers/recommend          # 获取买家推荐
GET    /api/v1/buyers/{id}               # 获取买家详情
POST   /api/v1/buyers/{id}/contact       # 生成联系模板

# 供应商匹配
POST   /api/v1/suppliers/search          # 搜索供应商
GET    /api/v1/suppliers/{id}            # 获取供应商详情
POST   /api/v1/suppliers/compare         # 供应商对比

# 产品管理
POST   /api/v1/products                  # 创建产品
GET    /api/v1/products                  # 获取产品列表
PUT    /api/v1/products/{id}             # 更新产品
DELETE /api/v1/products/{id}             # 删除产品
```

#### 订阅和支付
```
GET    /api/v1/subscription/plans        # 获取订阅计划
POST   /api/v1/subscription/create       # 创建订阅
POST   /api/v1/subscription/cancel       # 取消订阅
GET    /api/v1/usage/summary             # 使用统计
```

### SSE（Server-Sent Events）接口

#### 技术选择说明

**SSE vs WebSocket对比**：

| 特性 | SSE | WebSocket |
|-----|-----|-----------|
| 通信方向 | 单向（服务器→客户端） | 双向 |
| 协议复杂度 | 简单（基于HTTP） | 复杂（独立协议） |
| 浏览器支持 | 原生支持 | 需要额外处理 |
| 自动重连 | 内置 | 需要手动实现 |
| 代理友好 | 是 | 可能有问题 |
| 并发连接限制 | 6个/域名 | 无限制 |

对于TradeFlow这种主要是AI流式响应的场景，SSE更加简单可靠。

#### 接口定义

```javascript
// SSE连接
GET /api/v1/chat/stream?token={jwt_token}

// 发起对话（HTTP POST）
POST /api/v1/chat
{
  "message": "找美国的LED灯具买家",
  "agent_type": "buyer",
  "session_id": "xxx",
  "stream": true
}

// SSE 事件流格式
// 流式内容
event: stream
data: {"chunk": "根据您的需求，我为您找到了..."}

// 推荐结果
event: recommendation
data: {"type": "buyer", "company": "Bright Lighting Inc.", "score": 0.92}

// 完成事件
event: complete
data: {"session_id": "xxx", "tokens_used": 150, "total_recommendations": 5}

// 错误事件
event: error
data: {"error": "Agent processing failed", "code": "AGENT_ERROR"}
```

#### 重要技术注意事项

1. **浏览器连接限制**：同域名下最多6个并发SSE连接，超出需要排队
2. **连接管理**：及时关闭不需要的连接，避免资源浪费
3. **错误处理**：实现客户端自动重连机制
4. **CORS配置**：确保跨域请求正确配置
5. **代理兼容**：某些代理可能缓冲SSE响应，影响实时性

### API请求/响应示例

#### 买家推荐请求
```json
POST /api/v1/buyers/recommend
{
  "product_info": {
    "name": "LED Panel Light",
    "category": "lighting",
    "description": "高效节能LED面板灯",
    "price_range": "$10-50",
    "moq": 500
  },
  "target_markets": ["US", "DE", "UK"],
  "preferences": {
    "company_size": "medium",
    "trade_terms": "FOB"
  }
}
```

#### 买家推荐响应
```json
{
  "status": "success",
  "data": {
    "recommendations": [
      {
        "company_name": "Bright Lighting Inc.",
        "country": "US",
        "match_score": 0.92,
        "buyer_profile": {
          "annual_purchase": "$2M+",
          "main_products": ["LED lights", "Smart lighting"],
          "company_size": "50-200"
        },
        "contact_suggestion": {
          "best_approach": "email",
          "template": "..."
        }
      }
    ],
    "total": 10,
    "query_id": "rec_123456"
  }
}
```

---

## Google ADK Agent开发方案

### Agent架构设计

```python
# src/agent/base_agent.py
from google.adk.agents import LlmAgent
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseTradeAgent(ABC):
    """TradeFlow Agent基类"""
    
    def __init__(self, name: str, model: str = "gemini-2.0-flash"):
        self.name = name
        self.model = model
        self.tools = self._init_tools()
        self.agent = self._create_agent()
    
    @abstractmethod
    def _init_tools(self) -> List:
        """初始化Agent工具"""
        pass
    
    @abstractmethod
    def _get_instruction(self) -> str:
        """获取Agent指令"""
        pass
    
    def _create_agent(self) -> LlmAgent:
        """创建LLM Agent"""
        return LlmAgent(
            model=self.model,
            name=self.name,
            instruction=self._get_instruction(),
            tools=self.tools,
            generate_content_config={
                "temperature": 0.7,
                "max_output_tokens": 2048,
            }
        )
    
    async def process(
        self, 
        message: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """处理用户请求"""
        response = await self.agent.run_async(
            message=message,
            context=context
        )
        
        return self._format_response(response)
    
    @abstractmethod
    def _format_response(self, response: Any) -> Dict[str, Any]:
        """格式化响应"""
        pass
```

### 买家开发Agent实现

```python
# src/agent/buyer_agent.py
from .base_agent import BaseTradeAgent
from ..tools import (
    TradeDataSearchTool,
    BuyerRecommendationTool,
    EmailGeneratorTool,
    TranslationTool
)

class BuyerDevelopmentAgent(BaseTradeAgent):
    """买家开发Agent"""
    
    def __init__(self):
        super().__init__(name="buyer_development_agent")
    
    def _init_tools(self):
        return [
            TradeDataSearchTool(),
            BuyerRecommendationTool(),
            EmailGeneratorTool(),
            TranslationTool()
        ]
    
    def _get_instruction(self):
        return """
        你是TradeFlow的专业买家开发助手，帮助出口商找到合适的海外买家。
        
        核心能力：
        1. 根据产品信息智能匹配潜在买家
        2. 分析目标市场需求和趋势
        3. 生成专业的开发信模板
        4. 提供文化适配的沟通建议
        
        工作流程：
        1. 理解用户的产品和目标市场
        2. 搜索相关贸易数据和买家信息
        3. 基于匹配度推荐最合适的买家
        4. 提供个性化的联系策略
        
        注意事项：
        - 始终基于真实数据
        - 考虑文化差异
        - 提供可执行的建议
        """
    
    def _format_response(self, response):
        return {
            "content": response.content,
            "recommendations": self._extract_recommendations(response),
            "contact_templates": self._generate_templates(response),
            "metadata": {
                "confidence": 0.85,
                "data_sources": ["trade_data", "company_db"]
            }
        }
```

### Agent工具实现

```python
# src/agent/tools/trade_data_tool.py
from google.adk.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Dict, List
import asyncio

class TradeDataSearchParams(BaseModel):
    product_category: str = Field(description="产品类别")
    target_market: str = Field(description="目标市场")
    trade_type: str = Field(description="贸易类型：import/export")

class TradeDataSearchTool(BaseTool):
    """贸易数据搜索工具"""
    
    name = "trade_data_search"
    description = "搜索全球贸易数据"
    parameters_model = TradeDataSearchParams
    
    async def run_async(
        self, 
        args: Dict, 
        tool_context: Any
    ) -> Dict:
        params = TradeDataSearchParams(**args)
        
        # 查询MongoDB中的贸易数据
        trade_data = await self._query_trade_db(
            category=params.product_category,
            market=params.target_market
        )
        
        return {
            "market_size": trade_data.get("market_size"),
            "growth_rate": trade_data.get("growth_rate"),
            "top_importers": trade_data.get("importers", [])[:10],
            "price_trends": trade_data.get("price_trends")
        }
```

### Agent Gateway服务

```python
# src/backend/services/agent_gateway.py
from typing import Dict, Optional
from enum import Enum
import asyncio

class AgentType(str, Enum):
    BUYER = "buyer"
    SUPPLIER = "supplier"
    MARKET = "market"

class AgentGatewayService:
    """Agent网关服务"""
    
    def __init__(self):
        self.agents = {
            AgentType.BUYER: BuyerDevelopmentAgent(),
            AgentType.SUPPLIER: SupplierMatchingAgent(),
            AgentType.MARKET: MarketAnalysisAgent()
        }
        self.intent_classifier = IntentClassifier()
    
    async def route_request(
        self,
        message: str,
        agent_type: Optional[AgentType],
        context: Dict,
        user_id: str
    ) -> Dict:
        """路由请求到合适的Agent"""
        
        # 自动识别Agent类型
        if not agent_type:
            agent_type = await self.intent_classifier.classify(
                message, context
            )
        
        # 获取Agent
        agent = self.agents.get(agent_type)
        if not agent:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        # 处理请求
        try:
            # 从MongoDB加载会话上下文
            session_context = await self._load_session_context(
                user_id, agent_type
            )
            
            # 合并上下文
            full_context = {
                **session_context,
                **context,
                "user_id": user_id
            }
            
            # 调用Agent
            response = await agent.process(message, full_context)
            
            # 保存对话到MongoDB
            await self._save_conversation(
                user_id, agent_type, message, response
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Agent error: {str(e)}")
            raise
```

---

## 第三方登录集成

### OAuth配置

```python
# src/backend/config/oauth.py
from pydantic import BaseSettings

class OAuthConfig(BaseSettings):
    # Google OAuth
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/oauth/google/callback"
    
    # GitHub OAuth
    GITHUB_CLIENT_ID: str
    GITHUB_CLIENT_SECRET: str
    GITHUB_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/oauth/github/callback"
    
    # JWT配置
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    class Config:
        env_file = ".env"
```

### OAuth服务实现

```python
# src/backend/services/oauth_service.py
from authlib.integrations.starlette_client import OAuth
from fastapi import HTTPException
import jwt
from datetime import datetime, timedelta

class OAuthService:
    """OAuth认证服务"""
    
    def __init__(self, config: OAuthConfig):
        self.config = config
        self.oauth = OAuth()
        self._setup_providers()
    
    def _setup_providers(self):
        """配置OAuth提供商"""
        # Google
        self.oauth.register(
            name='google',
            client_id=self.config.GOOGLE_CLIENT_ID,
            client_secret=self.config.GOOGLE_CLIENT_SECRET,
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
            client_kwargs={'scope': 'openid email profile'}
        )
        
        # GitHub
        self.oauth.register(
            name='github',
            client_id=self.config.GITHUB_CLIENT_ID,
            client_secret=self.config.GITHUB_CLIENT_SECRET,
            access_token_url='https://github.com/login/oauth/access_token',
            authorize_url='https://github.com/login/oauth/authorize',
            api_base_url='https://api.github.com/',
            client_kwargs={'scope': 'user:email'}
        )
    
    async def handle_oauth_callback(
        self, 
        provider: str, 
        code: str
    ) -> Dict:
        """处理OAuth回调"""
        client = self.oauth.create_client(provider)
        
        # 获取token
        token = await client.authorize_access_token(code=code)
        
        # 获取用户信息
        if provider == 'google':
            user_info = token.get('userinfo')
        elif provider == 'github':
            resp = await client.get('user')
            user_info = resp.json()
        
        # 创建或更新用户
        user = await self._create_or_update_user(
            provider, user_info
        )
        
        # 生成JWT
        access_token = self._generate_jwt(user)
        
        return {
            "access_token": access_token,
            "user": user
        }
    
    def _generate_jwt(self, user: Dict) -> str:
        """生成JWT token"""
        payload = {
            "user_id": str(user["id"]),
            "email": user["email"],
            "exp": datetime.utcnow() + timedelta(
                hours=self.config.JWT_EXPIRATION_HOURS
            )
        }
        
        return jwt.encode(
            payload, 
            self.config.JWT_SECRET_KEY, 
            algorithm=self.config.JWT_ALGORITHM
        )
```

### OAuth路由实现

```python
# src/backend/routers/auth.py
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse

router = APIRouter(prefix="/api/v1/auth")

@router.get("/oauth/{provider}")
async def oauth_login(provider: str, request: Request):
    """发起OAuth登录"""
    client = oauth_service.oauth.create_client(provider)
    redirect_uri = request.url_for(
        "oauth_callback", provider=provider
    )
    return await client.authorize_redirect(
        request, redirect_uri
    )

@router.get("/oauth/{provider}/callback")
async def oauth_callback(
    provider: str, 
    code: str = None, 
    error: str = None
):
    """OAuth回调处理"""
    if error:
        raise HTTPException(400, detail=error)
    
    try:
        result = await oauth_service.handle_oauth_callback(
            provider, code
        )
        
        # 重定向到前端，带上token
        frontend_url = f"{FRONTEND_URL}/auth/success?token={result['access_token']}"
        return RedirectResponse(url=frontend_url)
        
    except Exception as e:
        logger.error(f"OAuth error: {str(e)}")
        raise HTTPException(400, detail="Authentication failed")
```

---

## 多语言支持策略

### 前端国际化（Phase 1）

```typescript
// src/frontend/i18n/config.ts
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// 翻译资源
import enTranslations from './locales/en.json';
import zhTranslations from './locales/zh.json';

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: enTranslations },
      zh: { translation: zhTranslations }
    },
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false
    },
    detection: {
      order: ['localStorage', 'navigator', 'htmlTag'],
      caches: ['localStorage']
    }
  });

export default i18n;
```

### 翻译文件示例

```json
// src/frontend/i18n/locales/zh.json
{
  "common": {
    "login": "登录",
    "logout": "退出",
    "search": "搜索",
    "send": "发送"
  },
  "auth": {
    "login_with_google": "使用 Google 登录",
    "login_with_github": "使用 GitHub 登录",
    "welcome_back": "欢迎回来"
  },
  "chat": {
    "placeholder": "输入您的问题...",
    "thinking": "正在思考...",
    "error": "出错了，请重试"
  },
  "buyer": {
    "find_buyers": "寻找买家",
    "recommend_buyers": "推荐买家",
    "buyer_profile": "买家档案"
  }
}
```

### 后端多语言支持（Phase 2）

```python
# src/backend/services/translation_service.py
from googletrans import Translator
from functools import lru_cache

class TranslationService:
    """翻译服务"""
    
    def __init__(self):
        self.translator = Translator()
        self.supported_languages = ['en', 'zh-CN', 'es', 'ar']
    
    @lru_cache(maxsize=1000)
    async def translate(
        self, 
        text: str, 
        target_lang: str, 
        source_lang: str = 'auto'
    ) -> str:
        """翻译文本"""
        if source_lang == target_lang:
            return text
        
        try:
            result = await self.translator.translate(
                text, 
                dest=target_lang, 
                src=source_lang
            )
            return result.text
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return text
    
    async def translate_response(
        self, 
        response: Dict, 
        target_lang: str
    ) -> Dict:
        """翻译API响应"""
        # 翻译需要的字段
        if 'content' in response:
            response['content'] = await self.translate(
                response['content'], target_lang
            )
        
        # 翻译推荐结果
        if 'recommendations' in response:
            for rec in response['recommendations']:
                if 'description' in rec:
                    rec['description'] = await self.translate(
                        rec['description'], target_lang
                    )
        
        return response
```

---

## 部署架构

### Docker配置

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY src/ ./src/

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["uvicorn", "src.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose开发环境

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/tradeflow
      - MONGODB_URL=mongodb://mongodb:27017/tradeflow
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - mongodb
      - redis
    volumes:
      - ./src:/app/src
    
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: tradeflow
    volumes:
      - postgres_data:/var/lib/postgresql/data
    
  mongodb:
    image: mongo:6
    volumes:
      - mongo_data:/data/db
    
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  mongo_data:
  redis_data:
```

### 生产部署（Cloud Run）

```bash
#!/bin/bash
# deploy.sh

# 构建镜像
gcloud builds submit --tag gcr.io/${PROJECT_ID}/tradeflow-backend

# 部署到Cloud Run
gcloud run deploy tradeflow-backend \
  --image gcr.io/${PROJECT_ID}/tradeflow-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="
    GOOGLE_CLOUD_PROJECT=${PROJECT_ID},
    DATABASE_URL=${DATABASE_URL},
    MONGODB_URL=${MONGODB_URL},
    REDIS_URL=${REDIS_URL}
  " \
  --min-instances=1 \
  --max-instances=10 \
  --memory=2Gi \
  --cpu=2
```

---

## 性能优化策略

### 1. 数据库优化

```python
# MongoDB索引
db.conversations.createIndex({ "user_id": 1, "created_at": -1 })
db.conversations.createIndex({ "session_id": 1 })
db.recommendations.createIndex({ "user_id": 1, "type": 1 })

# PostgreSQL索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_auth_provider ON users(auth_provider, auth_provider_id);
CREATE INDEX idx_products_company ON products(company_id);
CREATE INDEX idx_usage_user_created ON usage_records(user_id, created_at);
```

### 2. 缓存策略

```python
# src/backend/utils/cache.py
from functools import wraps
import redis
import json
import hashlib

redis_client = redis.Redis.from_url(REDIS_URL)

def cache_result(expire_time=3600):
    """缓存装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"cache:{func.__name__}:{hashlib.md5(
                f"{args}{kwargs}".encode()
            ).hexdigest()}"
            
            # 尝试从缓存获取
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # 调用原函数
            result = await func(*args, **kwargs)
            
            # 存入缓存
            redis_client.setex(
                cache_key, 
                expire_time, 
                json.dumps(result)
            )
            
            return result
        return wrapper
    return decorator

# 使用示例
@cache_result(expire_time=3600)
async def get_buyer_recommendations(product_info, markets):
    # 耗时的推荐计算
    pass
```

### 3. Agent响应优化

#### 后端SSE实现

```python
# SSE流式响应处理
from fastapi.responses import StreamingResponse
import json

async def stream_agent_response(
    agent: BaseTradeAgent,
    message: str,
    context: Dict
):
    """流式返回Agent响应（SSE格式）"""
    async def generate():
        try:
            # 流式内容
            async for chunk in agent.stream_process(message, context):
                data = json.dumps({"chunk": chunk}, ensure_ascii=False)
                yield f"event: stream\ndata: {data}\n\n"
            
            # 推荐结果（如果有）
            recommendations = agent.get_recommendations()
            for rec in recommendations:
                data = json.dumps(rec, ensure_ascii=False)
                yield f"event: recommendation\ndata: {data}\n\n"
            
            # 完成事件
            metadata = agent.get_metadata()
            data = json.dumps(metadata, ensure_ascii=False)
            yield f"event: complete\ndata: {data}\n\n"
            
        except Exception as e:
            # 错误事件
            error_data = json.dumps({
                "error": str(e),
                "code": "AGENT_ERROR"
            }, ensure_ascii=False)
            yield f"event: error\ndata: {error_data}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*"
        }
    )

# FastAPI路由
@router.get("/chat/stream")
async def chat_stream(
    token: str,
    session_id: str = None,
    current_user: User = Depends(get_current_user)
):
    """SSE聊天流端点"""
    return stream_agent_response(agent, message, context)
```

#### 前端EventSource实现

```javascript
// React Hook for SSE
import { useState, useEffect, useCallback } from 'react';

const useChatStream = () => {
    const [messages, setMessages] = useState([]);
    const [isStreaming, setIsStreaming] = useState(false);
    const [eventSource, setEventSource] = useState(null);

    const sendMessage = useCallback(async (message, agentType = 'buyer') => {
        setIsStreaming(true);
        
        try {
            // 1. 发起聊天请求
            const response = await fetch('/api/v1/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    message,
                    agent_type: agentType,
                    stream: true
                })
            });

            const { session_id } = await response.json();

            // 2. 建立SSE连接
            const es = new EventSource(
                `/api/v1/chat/stream?token=${token}&session_id=${session_id}`
            );

            setEventSource(es);

            // 3. 处理流式内容
            es.addEventListener('stream', (event) => {
                const data = JSON.parse(event.data);
                setMessages(prev => [
                    ...prev.slice(0, -1),
                    {
                        ...prev[prev.length - 1],
                        content: (prev[prev.length - 1]?.content || '') + data.chunk
                    }
                ]);
            });

            // 4. 处理推荐结果
            es.addEventListener('recommendation', (event) => {
                const recommendation = JSON.parse(event.data);
                // 更新UI显示推荐
                setRecommendations(prev => [...prev, recommendation]);
            });

            // 5. 处理完成事件
            es.addEventListener('complete', (event) => {
                const metadata = JSON.parse(event.data);
                setIsStreaming(false);
                es.close();
                
                // 更新token使用统计等
                updateUsageStats(metadata);
            });

            // 6. 处理错误
            es.addEventListener('error', (event) => {
                const error = JSON.parse(event.data);
                console.error('Stream error:', error);
                setIsStreaming(false);
                es.close();
            });

            // 7. 连接错误处理
            es.onerror = (error) => {
                console.error('EventSource error:', error);
                setIsStreaming(false);
                es.close();
            };

        } catch (error) {
            console.error('Send message error:', error);
            setIsStreaming(false);
        }
    }, [token]);

    const stopStream = useCallback(() => {
        if (eventSource) {
            eventSource.close();
            setEventSource(null);
            setIsStreaming(false);
        }
    }, [eventSource]);

    useEffect(() => {
        return () => {
            if (eventSource) {
                eventSource.close();
            }
        };
    }, [eventSource]);

    return {
        messages,
        isStreaming,
        sendMessage,
        stopStream
    };
};

// 在组件中使用
const ChatComponent = () => {
    const { messages, isStreaming, sendMessage, stopStream } = useChatStream();

    return (
        <div className="chat-container">
            {messages.map((message, index) => (
                <div key={index} className="message">
                    {message.content}
                </div>
            ))}
            
            {isStreaming && (
                <button onClick={stopStream}>
                    停止生成
                </button>
            )}
        </div>
    );
};
```

### 4. API限流

```python
# src/backend/middleware/rate_limit.py
from fastapi import HTTPException
import time

class RateLimiter:
    """API限流中间件"""
    
    def __init__(self, redis_client, max_requests=100, window=3600):
        self.redis = redis_client
        self.max_requests = max_requests
        self.window = window
    
    async def check_limit(self, user_id: str, endpoint: str):
        """检查限流"""
        key = f"rate_limit:{user_id}:{endpoint}"
        
        try:
            current = self.redis.incr(key)
            if current == 1:
                self.redis.expire(key, self.window)
            
            if current > self.max_requests:
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded"
                )
        except redis.RedisError:
            # Redis错误时放行
            pass
```

---

## 测试方案

### 单元测试

```python
# tests/test_agents.py
import pytest
from unittest.mock import Mock, patch

@pytest.mark.asyncio
async def test_buyer_agent():
    """测试买家Agent"""
    agent = BuyerDevelopmentAgent()
    
    # Mock工具响应
    with patch.object(TradeDataSearchTool, 'run_async') as mock_tool:
        mock_tool.return_value = {
            "top_importers": ["Company A", "Company B"],
            "market_size": "$100M"
        }
        
        response = await agent.process(
            message="找美国LED灯具买家",
            context={"product": "LED Panel"}
        )
        
        assert "recommendations" in response
        assert len(response["recommendations"]) > 0
```

### API集成测试

```python
# tests/test_api.py
from fastapi.testclient import TestClient

def test_oauth_login():
    """测试OAuth登录"""
    response = client.get("/api/v1/auth/oauth/google")
    assert response.status_code == 302
    assert "accounts.google.com" in response.headers["location"]

def test_chat_endpoint():
    """测试对话接口"""
    response = client.post(
        "/api/v1/chat",
        json={
            "message": "找买家",
            "agent_type": "buyer"
        },
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    assert "content" in response.json()
```

### 性能测试

```python
# tests/test_performance.py
import asyncio
import time

async def test_concurrent_requests():
    """测试并发性能"""
    start_time = time.time()
    
    # 创建100个并发请求
    tasks = []
    for i in range(100):
        task = asyncio.create_task(
            client.post("/api/v1/chat", json={...})
        )
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    
    duration = time.time() - start_time
    assert duration < 10  # 100个请求应在10秒内完成
    assert all(r.status_code == 200 for r in results)
```

---

## 风险与缓解措施

### 技术风险

| 风险 | 影响 | 概率 | 缓解措施 |
|-----|------|------|----------|
| Google ADK API限制 | 高 | 中 | 实施缓存策略，准备降级方案 |
| MongoDB性能瓶颈 | 中 | 中 | 优化索引，考虑分片 |
| OAuth服务不稳定 | 高 | 低 | 保留邮箱登录，多provider支持 |
| AI响应时间过长 | 高 | 中 | 流式响应，使用更快的模型 |

### 业务风险

| 风险 | 影响 | 概率 | 缓解措施 |
|-----|------|------|----------|
| 用户采用率低 | 高 | 中 | 优化新手引导，提供试用 |
| 数据质量问题 | 高 | 高 | 建立数据审核机制 |
| 多语言翻译不准 | 中 | 中 | 人工审核关键内容 |

### 安全风险

| 风险 | 影响 | 概率 | 缓解措施 |
|-----|------|------|----------|
| 数据泄露 | 高 | 低 | 加密存储，访问控制 |
| DDoS攻击 | 中 | 中 | 使用CDN，限流保护 |
| Token劫持 | 高 | 低 | HTTPS，短期Token |

---

## 实施计划

### 第1个月：基础架构和认证

**第1-2周**
- [ ] 搭建开发环境
- [ ] 初始化项目结构
- [ ] 配置数据库（PostgreSQL + MongoDB + Redis）
- [ ] 实现基础FastAPI框架

**第3-4周**
- [ ] 实现Google OAuth登录
- [ ] 实现JWT认证系统
- [ ] 基础用户管理API
- [ ] 前端登录界面

### 第2个月：AI Agent开发

**第5-6周**
- [ ] Google ADK环境配置
- [ ] 实现买家开发Agent
- [ ] 基础工具开发（搜索、推荐）
- [ ] Agent Gateway服务

**第7-8周**
- [ ] SSE流式对话响应
- [ ] 对话历史存储（MongoDB）
- [ ] 前端对话界面（EventSource API）
- [ ] 基础多语言支持（UI）

### 第3个月：业务功能完善

**第9-10周**
- [ ] 供应商匹配Agent
- [ ] 产品管理功能
- [ ] 买家推荐API
- [ ] GitHub OAuth集成

**第11-12周**
- [ ] Stripe支付集成
- [ ] 使用统计和限额
- [ ] 性能优化
- [ ] 部署到Cloud Run

### 第4个月：优化和上线

**第13-14周**
- [ ] 全面测试
- [ ] 性能调优
- [ ] 安全审计
- [ ] 文档完善

**第15-16周**
- [ ] Beta测试
- [ ] Bug修复
- [ ] 正式上线
- [ ] 监控配置

---

## 总结

本技术设计方案基于TradeFlow MVP需求，采用简洁实用的架构设计：

**核心优势**：
1. **Google ADK驱动**：利用先进的AI框架快速实现智能对话
2. **混合数据架构**：PostgreSQL处理结构化数据，MongoDB存储灵活的对话数据
3. **渐进式实现**：多语言等复杂功能分阶段实施
4. **用户友好**：OAuth登录降低使用门槛

**关键指标**：
- 开发周期：3-4个月
- AI响应时间：< 4秒（流式响应体感更快）
- 第三方登录率：> 30%
- 系统可用性：> 99%

通过合理的技术选型和务实的实施计划，TradeFlow MVP将在预定时间内成功交付，为后续迭代奠定坚实基础。