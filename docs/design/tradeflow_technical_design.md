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

#### 4. Google ADK Agent Layer 【✅ 已实现】
> **实现状态**: 已通过ADK独立开发完成，位于 `src/agent/TradeFlowAgent/`

- **Main Orchestrator Agent**: 系统级ReAct主协调器 ✅
- **Search Agent**: 网络搜索专家 ✅
- **Trade Agent**: 贸易数据专家（海关数据查询） ✅
- **Company Agent**: 企业信息专家 ✅
- **Enterprise Discovery Agent**: 企业发现专家（供应商匹配） ✅
- **Web Analyzer Agent**: 商品页面解析专家 ✅

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

-- 文件元数据表
CREATE TABLE files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    conversation_id VARCHAR(255), -- 关联的对话ID
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL, -- 'image', 'document', 'code', 'data'
    file_extension VARCHAR(10) NOT NULL,
    content_type VARCHAR(100) NOT NULL,
    file_size BIGINT NOT NULL,
    minio_bucket VARCHAR(100) NOT NULL,
    minio_object_key VARCHAR(500) NOT NULL,
    description TEXT,
    tags JSONB,
    is_generated BOOLEAN DEFAULT false, -- 是否为Agent生成的文件
    preview_content TEXT, -- 预览内容（文本文件的前几行等）
    metadata JSONB, -- 其他元数据（尺寸、编码等）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 文件关联表（文件与对话消息的关系）
CREATE TABLE file_message_relations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id UUID REFERENCES files(id) ON DELETE CASCADE,
    message_id VARCHAR(255) NOT NULL, -- MongoDB中的消息ID
    relation_type VARCHAR(50) NOT NULL, -- 'input', 'output', 'attachment'
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
      message_id: String, // 消息唯一ID
      role: String, // 'user', 'assistant'
      content: String,
      timestamp: Date,
      files: [
        {
          file_id: String, // PostgreSQL中的文件ID
          filename: String,
          file_type: String,
          relation_type: String // 'input', 'output', 'attachment'
        }
      ],
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
  files_summary: {
    total_files: Number,
    file_types: Array, // 对话中涉及的文件类型统计
    generated_files: Number // Agent生成的文件数量
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

# 文件预览缓存
file_preview:{file_id} -> {
  content: preview_text,
  cached_at: timestamp
}
```

### MinIO存储结构

```
# Bucket组织结构
tradeflow-files/
├── users/{user_id}/
│   ├── uploads/           # 用户上传的文件
│   │   ├── documents/     # 文档类文件
│   │   ├── images/        # 图片文件
│   │   └── data/          # 数据文件
│   └── generated/         # Agent生成的文件
│       ├── reports/       # 生成的报告
│       ├── code/          # 生成的代码文件
│       ├── templates/     # 生成的模板
│       └── analysis/      # 分析结果文件

# 对象键格式
{user_id}/{category}/{yyyy/mm/dd}/{uuid}.{extension}

# 示例
users/123e4567-e89b-12d3-a456-426614174000/
  uploads/documents/2024/01/15/contract_abc123.pdf
  generated/reports/2024/01/15/market_analysis_def456.docx
  generated/code/2024/01/15/api_client_ghi789.py

# 临时文件存储
temp-files/
├── processing/{uuid}/     # 文件处理中的临时存储
└── preview/{file_id}/     # 预览图缓存
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

#### 文件管理
```
# 文件上传和管理
POST   /api/v1/files/upload              # 上传文件
GET    /api/v1/files/{id}                # 获取文件元数据
GET    /api/v1/files/{id}/download       # 下载文件
GET    /api/v1/files/{id}/preview        # 获取文件预览
DELETE /api/v1/files/{id}                # 删除文件
PUT    /api/v1/files/{id}                # 更新文件元数据

# 对话文件关联
GET    /api/v1/conversations/{id}/files  # 获取对话关联的所有文件
POST   /api/v1/conversations/{id}/files  # 为对话添加文件
DELETE /api/v1/conversations/{id}/files/{file_id} # 移除对话文件关联

# 文件搜索和过滤
GET    /api/v1/files                     # 获取用户文件列表（支持分页和过滤）
GET    /api/v1/files/search              # 按文件名、类型、标签搜索文件

# 批量操作
POST   /api/v1/files/batch/delete        # 批量删除文件
POST   /api/v1/files/batch/move          # 批量移动文件
POST   /api/v1/files/batch/tag           # 批量添加标签
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

#### 文件上传请求
```json
POST /api/v1/files/upload
Content-Type: multipart/form-data

{
  "file": [binary_data],
  "conversation_id": "conv_123456",
  "description": "产品规格书",
  "tags": ["product", "specification"],
  "is_generated": false
}
```

#### 文件上传响应
```json
{
  "status": "success",
  "data": {
    "file": {
      "id": "file_789abc",
      "filename": "product_spec_1642567890.pdf",
      "original_filename": "产品规格书.pdf",
      "file_type": "document",
      "file_size": 2048576,
      "content_type": "application/pdf",
      "download_url": "/api/v1/files/file_789abc/download",
      "preview_url": "/api/v1/files/file_789abc/preview",
      "created_at": "2024-01-19T08:30:00Z"
    }
  }
}
```

#### 获取对话文件列表请求
```json
GET /api/v1/conversations/conv_123456/files?type=document&limit=10&offset=0
```

#### 获取对话文件列表响应
```json
{
  "status": "success",
  "data": {
    "files": [
      {
        "id": "file_789abc",
        "filename": "market_analysis_report.docx",
        "file_type": "document",
        "file_size": 1024000,
        "is_generated": true,
        "relation_type": "output",
        "preview_content": "# 市场分析报告\n\n## 概述\n本报告分析了LED照明市场...",
        "created_at": "2024-01-19T08:30:00Z"
      },
      {
        "id": "file_def456",
        "filename": "buyer_contact_template.txt",
        "file_type": "code",
        "file_size": 2048,
        "is_generated": true,
        "relation_type": "output",
        "preview_content": "Dear [Company Name],\n\nWe are pleased to introduce...",
        "created_at": "2024-01-19T08:25:00Z"
      }
    ],
    "total": 15,
    "pagination": {
      "limit": 10,
      "offset": 0,
      "has_more": true
    }
  }
}
```

#### 文件预览请求
```json
GET /api/v1/files/file_789abc/preview?lines=50&format=text
```

#### 文件预览响应
```json
{
  "status": "success",
  "data": {
    "preview": {
      "content": "# LED产品规格书\n\n## 基本参数\n- 功率: 12W\n- 色温: 4000K\n- 流明: 1200lm...",
      "format": "markdown",
      "total_lines": 156,
      "preview_lines": 50,
      "file_info": {
        "filename": "product_spec.md",
        "file_size": 8192,
        "last_modified": "2024-01-19T08:30:00Z"
      }
    }
  }
}
```

---

## 文件预览系统设计

### 系统概述

文件预览系统是对话内容展示的重要组成部分，用于在右侧面板中预览和管理对话过程中产生的各种文件。系统支持多种文件格式的预览，提供直观的文件管理界面。

### 支持的文件类型

#### 代码文件
- **.js, .ts, .jsx, .tsx**: JavaScript/TypeScript文件，支持语法高亮
- **.py**: Python文件，支持语法高亮和代码折叠
- **.json**: JSON文件，支持格式化显示和语法验证
- **.yaml, .yml**: YAML配置文件
- **.sql**: SQL脚本文件

#### 文档文件
- **.md**: Markdown文件，支持渲染预览和源码查看
- **.txt**: 纯文本文件
- **.pdf**: PDF文档，支持分页预览
- **.docx**: Word文档，转换为HTML预览
- **.html**: HTML文件，支持渲染和源码模式

#### 数据文件
- **.csv**: CSV数据文件，支持表格形式展示
- **.xlsx**: Excel文件，支持工作表切换
- **.json**: JSON数据文件，支持树形结构展示

#### 图像文件
- **.png, .jpg, .jpeg**: 位图图像，支持缩放和全屏查看
- **.svg**: 矢量图像，支持代码查看和渲染预览
- **.webp**: 现代图像格式

### 架构设计

#### 文件处理流程

```mermaid
graph TD
    A[Agent生成文件] --> B[文件服务接收]
    B --> C[文件类型识别]
    C --> D[存储到MinIO]
    D --> E[元数据存储到PostgreSQL]
    E --> F[关联到对话消息]
    F --> G[生成预览内容]
    G --> H[缓存预览到Redis]
    H --> I[通知前端更新]
    
    J[用户点击文件] --> K[检查预览缓存]
    K --> L{缓存存在?}
    L -->|是| M[返回缓存内容]
    L -->|否| N[从MinIO读取文件]
    N --> O[生成预览内容]
    O --> P[更新缓存]
    P --> M
```

#### 前端组件架构

```typescript
// 文件预览面板组件结构
interface FilePreviewPanel {
  // 文件列表组件
  FileList: {
    filters: FileFilter[];
    sortOptions: SortOption[];
    files: FileInfo[];
  };
  
  // 预览组件
  FilePreview: {
    currentFile: FileInfo | null;
    previewMode: 'code' | 'rendered' | 'image' | 'table';
    renderComponent: CodePreview | ImagePreview | TablePreview | DocumentPreview;
  };
  
  // 操作工具栏
  FileToolbar: {
    actions: ['download', 'copy', 'share', 'delete'];
    viewOptions: ['fullscreen', 'split', 'panel'];
  };
}
```

### 预览实现方案

#### 代码文件预览
```typescript
// 使用react-syntax-highlighter进行语法高亮
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

const CodePreview: React.FC<{ content: string; language: string }> = ({ content, language }) => {
  return (
    <SyntaxHighlighter 
      language={language}
      style={vscDarkPlus}
      showLineNumbers={true}
      wrapLines={true}
    >
      {content}
    </SyntaxHighlighter>
  );
};
```

#### Markdown文件预览
```typescript
// 使用react-markdown进行渲染
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';

const MarkdownPreview: React.FC<{ content: string }> = ({ content }) => {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        code: ({ node, inline, className, children, ...props }) => {
          const match = /language-(\w+)/.exec(className || '');
          return !inline && match ? (
            <SyntaxHighlighter language={match[1]} {...props}>
              {String(children).replace(/\n$/, '')}
            </SyntaxHighlighter>
          ) : (
            <code className={className} {...props}>
              {children}
            </code>
          );
        }
      }}
    >
      {content}
    </ReactMarkdown>
  );
};
```

#### CSV数据预览
```typescript
// 使用react-table进行表格展示
import { useTable, usePagination } from 'react-table';

const CSVPreview: React.FC<{ data: any[]; columns: any[] }> = ({ data, columns }) => {
  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    page,
    prepareRow,
    canPreviousPage,
    canNextPage,
    nextPage,
    previousPage,
    pageCount,
    state: { pageIndex }
  } = useTable({ columns, data }, usePagination);

  return (
    <div>
      <table {...getTableProps()}>
        <thead>
          {headerGroups.map(headerGroup => (
            <tr {...headerGroup.getHeaderGroupProps()}>
              {headerGroup.headers.map(column => (
                <th {...column.getHeaderProps()}>
                  {column.render('Header')}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody {...getTableBodyProps()}>
          {page.map(row => {
            prepareRow(row);
            return (
              <tr {...row.getRowProps()}>
                {row.cells.map(cell => (
                  <td {...cell.getCellProps()}>
                    {cell.render('Cell')}
                  </td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>
      {/* 分页控件 */}
      <div>
        <button onClick={() => previousPage()} disabled={!canPreviousPage}>
          上一页
        </button>
        <span>
          第 {pageIndex + 1} 页，共 {pageCount} 页
        </span>
        <button onClick={() => nextPage()} disabled={!canNextPage}>
          下一页
        </button>
      </div>
    </div>
  );
};
```

### 后端文件服务实现

#### 文件服务类设计

```python
# src/backend/services/file_service.py
from typing import List, Optional, BinaryIO
import minio
from minio import Minio
import uuid
import os
from datetime import datetime
import magic

class FileService:
    """文件管理服务"""
    
    def __init__(self, minio_client: Minio, db_session):
        self.minio_client = minio_client
        self.db_session = db_session
        self.bucket_name = "tradeflow-files"
    
    async def upload_file(
        self,
        file: BinaryIO,
        user_id: str,
        conversation_id: str = None,
        original_filename: str = None,
        description: str = None,
        tags: List[str] = None
    ) -> dict:
        """上传文件并返回文件信息"""
        
        # 生成文件ID和存储路径
        file_id = str(uuid.uuid4())
        file_content = file.read()
        file_size = len(file_content)
        
        # 检测文件类型
        content_type = magic.from_buffer(file_content, mime=True)
        file_extension = self._get_file_extension(original_filename or "")
        file_type = self._classify_file_type(content_type, file_extension)
        
        # 生成MinIO对象键
        today = datetime.now()
        category = "generated" if conversation_id else "uploads"
        object_key = f"users/{user_id}/{category}/{file_type}s/{today.strftime('%Y/%m/%d')}/{file_id}{file_extension}"
        
        # 上传到MinIO
        self.minio_client.put_object(
            bucket_name=self.bucket_name,
            object_name=object_key,
            data=BytesIO(file_content),
            length=file_size,
            content_type=content_type
        )
        
        # 生成预览内容
        preview_content = await self._generate_preview(
            file_content, file_type, file_extension
        )
        
        # 保存元数据到数据库
        file_record = FileRecord(
            id=file_id,
            user_id=user_id,
            conversation_id=conversation_id,
            filename=f"{original_filename}_{int(datetime.now().timestamp())}{file_extension}",
            original_filename=original_filename,
            file_type=file_type,
            file_extension=file_extension,
            content_type=content_type,
            file_size=file_size,
            minio_bucket=self.bucket_name,
            minio_object_key=object_key,
            description=description,
            tags=tags or [],
            preview_content=preview_content[:1000] if preview_content else None  # 限制预览长度
        )
        
        self.db_session.add(file_record)
        await self.db_session.commit()
        
        return {
            "id": file_id,
            "filename": file_record.filename,
            "file_type": file_type,
            "file_size": file_size,
            "content_type": content_type,
            "download_url": f"/api/v1/files/{file_id}/download",
            "preview_url": f"/api/v1/files/{file_id}/preview",
            "created_at": file_record.created_at
        }
    
    async def get_file_preview(
        self, 
        file_id: str, 
        lines: int = None,
        format: str = "auto"
    ) -> dict:
        """获取文件预览内容"""
        
        # 从缓存检查
        cache_key = f"file_preview:{file_id}:{lines}:{format}"
        cached_content = await redis_client.get(cache_key)
        if cached_content:
            return json.loads(cached_content)
        
        # 从数据库获取文件信息
        file_record = await self.db_session.get(FileRecord, file_id)
        if not file_record:
            raise FileNotFoundError(f"File {file_id} not found")
        
        # 从MinIO获取文件内容
        response = self.minio_client.get_object(
            bucket_name=file_record.minio_bucket,
            object_name=file_record.minio_object_key
        )
        content = response.data
        
        # 生成预览
        preview_content = await self._generate_preview(
            content, 
            file_record.file_type, 
            file_record.file_extension,
            lines
        )
        
        result = {
            "content": preview_content,
            "format": self._detect_preview_format(file_record.file_extension),
            "file_info": {
                "filename": file_record.filename,
                "file_size": file_record.file_size,
                "file_type": file_record.file_type,
                "last_modified": file_record.updated_at
            }
        }
        
        # 缓存预览内容（1小时）
        await redis_client.setex(cache_key, 3600, json.dumps(result))
        
        return result
    
    def _classify_file_type(self, content_type: str, extension: str) -> str:
        """根据MIME类型和扩展名分类文件"""
        if extension in ['.py', '.js', '.ts', '.jsx', '.tsx', '.json', '.sql', '.yaml', '.yml']:
            return 'code'
        elif extension in ['.md', '.txt', '.pdf', '.docx', '.html']:
            return 'document'
        elif extension in ['.csv', '.xlsx']:
            return 'data'
        elif content_type.startswith('image/'):
            return 'image'
        else:
            return 'document'
    
    async def _generate_preview(
        self, 
        content: bytes, 
        file_type: str, 
        extension: str,
        lines: int = 50
    ) -> str:
        """生成文件预览内容"""
        try:
            if file_type == 'image':
                return f"[图像文件: {extension}]"
            
            # 尝试解码为文本
            text_content = content.decode('utf-8')
            
            if lines:
                text_lines = text_content.split('\n')[:lines]
                return '\n'.join(text_lines)
            
            # 对于大文件，只返回前1000个字符
            if len(text_content) > 1000:
                return text_content[:1000] + "..."
            
            return text_content
            
        except UnicodeDecodeError:
            return f"[二进制文件: {extension}]"
```

### 性能优化策略

#### 1. 预览内容缓存
- 使用Redis缓存常用文件的预览内容
- 支持按文件修改时间自动失效
- 大文件采用分段预览和延迟加载

#### 2. 图像优化
- 自动生成缩略图
- 支持WebP格式压缩
- 实现渐进式加载

#### 3. 大文件处理
- 支持分块上传和下载
- 大文本文件采用虚拟滚动
- PDF文件按页预览

#### 4. 带宽优化
- 实现文件内容压缩
- 支持Range请求
- CDN加速静态文件访问

---

## Google ADK Agent开发方案 【✅ 已实现】

> **实现状态**: TradeFlowAgent已完整实现，采用层次化ReAct架构
> **代码位置**: `src/agent/TradeFlowAgent/`
> **开发状态**: 功能完整，已通过测试，待集成

### 已实现的Agent架构

#### 层次化ReAct架构设计
```
TradeFlow Agent System
├── 🧠 系统级ReAct - 主协调Agent
│   ├── 使用PlanReActPlanner进行系统级推理
│   ├── 动态Agent选择和协调
│   └── 质量评估和策略调整
├── 🎯 专业级ReAct - 供应商分析Agent  
│   ├── 供应商数据聚合和评分
│   ├── 供应链关系分析
│   └── 匹配推荐算法
└── ⚡ 执行级工具 - 6个专业Agent
    ├── search_agent (Jina Search)
    ├── trade_agent (Tendata API)
    ├── company_agent (企业信息查询)
    ├── enterprise_discovery_agent (B2B平台搜索)
    ├── web_analyzer_agent (Jina Reader)
    └── state_manager_agent (会话状态管理)
```

#### 实际实现代码结构
```python
# src/agent/TradeFlowAgent/trade_flow/main_agent.py
from google.adk.agents import Agent
from google.adk.planners import PlanReActPlanner

# 创建主协调Agent（系统级ReAct）
root_agent = Agent(
    name="trade_flow_orchestrator",
    model=get_model_config(),
    planner=PlanReActPlanner(),  # 系统级推理
    description="贸易数据查询和分析的主协调器",
    instruction="""使用ReAct模式进行系统级推理...""",
    agents=[search_agent, trade_agent, company_agent]
)
```

### 已实现的核心工具集

#### 1. 搜索分析工具
- **web_search.py**: Jina Search API集成，高质量网页搜索
- **jina_reader.py**: 网页内容提取，支持商品页面解析
- **enterprise_discovery.py**: B2B平台企业发现

#### 2. 贸易数据工具
- **tendata_api.py**: 海关数据查询接口
- **trade_data_query.py**: 贸易统计分析
- **company_trade_profile.py**: 企业贸易画像生成

#### 3. 企业信息工具
- **company_info.py**: 企业资质查询
- **company_query.py**: 企业背景调查
- **supplier_profile.py**: 供应商档案管理

#### 4. 文件处理工具
- **artifacts_manager.py**: 文件生成管理
- **csv_converter.py**: CSV报告生成
- **download_artifact.py**: 文件下载服务

### 已验证的核心功能

#### 1. 商品供应商发现 ✅
**输入示例**: `"分析这个商品的供应商：https://www.walmart.com/ip/Apple-iPhone-15"`
**输出能力**:
- 完整供应链层级：零售商→品牌方→代工厂→原材料供应商
- 具体企业信息：富士康、比亚迪电子等主要代工厂
- 联系方式：包含电话、邮箱、联系人姓名
- 贸易数据验证：基于真实海关出口记录

#### 2. 贸易数据查询 ✅
**输入示例**: `"查询2024年手机对美国的出口数据"`
**输出能力**:
- 出口总额和趋势分析
- 主要出口国家和份额
- 热门品牌和产品分布
- 关税和贸易政策影响

#### 3. 企业背景调查 ✅
**输入示例**: `"分析比亚迪电子的供应商资质"`
**输出能力**:
- 企业资质认证（ISO、行业认证）
- 贸易能力评估（年出口额、覆盖国家）
- 主要客户和产品线
- 风险评估和合作建议

### Agent与后端集成方案（待实施）

```python
# 计划的集成接口
class AgentGatewayService:
    """Agent网关服务，负责调度TradeFlowAgent"""
    
    async def process_query(
        self, 
        query: str,
        user_id: int,
        session_id: str
    ) -> AsyncGenerator:
        """处理用户查询并返回流式响应"""
        # 1. 调用TradeFlowAgent
        # 2. 通过SSE返回结果
        # 3. 保存对话历史到MongoDB
        pass
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

## MinIO对象存储集成方案

### MinIO选择理由

相比于设计师建议的Google Cloud Storage，我们选择MinIO作为对象存储方案的原因：

1. **自主可控**: MinIO是开源解决方案，避免云服务vendor lock-in
2. **成本优势**: 自托管MinIO成本更低，特别是在MVP阶段
3. **部署灵活**: 支持本地开发、私有云和公有云多种部署方式
4. **S3兼容**: 完全兼容Amazon S3 API，便于后续迁移
5. **高性能**: 专为云原生环境优化，性能表现优异

### MinIO架构设计

#### 服务配置

```yaml
# minio-config.yaml
version: '3.8'
services:
  minio:
    image: minio/minio:latest
    container_name: tradeflow-minio
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio-data:/data
    environment:
      MINIO_ACCESS_KEY: ${MINIO_ACCESS_KEY}
      MINIO_SECRET_KEY: ${MINIO_SECRET_KEY}
      MINIO_BROWSER_REDIRECT_URL: http://localhost:9001
    command: server /data --console-address ":9001"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 20s
      retries: 3

volumes:
  minio-data:
    driver: local
```

#### 客户端集成

```python
# src/backend/config/minio_config.py
from minio import Minio
from pydantic import BaseSettings
import logging

class MinIOConfig(BaseSettings):
    """MinIO配置类"""
    
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_SECURE: bool = False  # 开发环境使用HTTP
    MINIO_REGION: str = "us-east-1"
    
    # Bucket配置
    MINIO_BUCKET_FILES: str = "tradeflow-files"
    MINIO_BUCKET_TEMP: str = "tradeflow-temp"
    MINIO_BUCKET_BACKUPS: str = "tradeflow-backups"
    
    class Config:
        env_file = ".env"

class MinIOClient:
    """MinIO客户端单例"""
    
    _instance = None
    _client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MinIOClient, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            self.config = MinIOConfig()
            self._client = Minio(
                endpoint=self.config.MINIO_ENDPOINT,
                access_key=self.config.MINIO_ACCESS_KEY,
                secret_key=self.config.MINIO_SECRET_KEY,
                secure=self.config.MINIO_SECURE,
                region=self.config.MINIO_REGION
            )
            self._ensure_buckets_exist()
    
    def _ensure_buckets_exist(self):
        """确保必要的bucket存在"""
        buckets = [
            self.config.MINIO_BUCKET_FILES,
            self.config.MINIO_BUCKET_TEMP,
            self.config.MINIO_BUCKET_BACKUPS
        ]
        
        for bucket in buckets:
            if not self._client.bucket_exists(bucket):
                self._client.make_bucket(bucket)
                
                # 设置bucket策略
                if bucket == self.config.MINIO_BUCKET_FILES:
                    self._set_public_read_policy(bucket)
    
    def _set_public_read_policy(self, bucket_name: str):
        """设置bucket的公共读取策略"""
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{bucket_name}/*"]
                }
            ]
        }
        
        import json
        self._client.set_bucket_policy(
            bucket_name, 
            json.dumps(policy)
        )
    
    @property
    def client(self) -> Minio:
        return self._client

# 全局MinIO客户端实例
minio_client = MinIOClient().client
```

### Agent文件生成集成

#### Agent工具扩展

```python
# src/agent/tools/file_generation_tool.py
from google.adk.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Dict, List, Any
import uuid
import io
from ..services.file_service import FileService

class FileGenerationParams(BaseModel):
    content: str = Field(description="文件内容")
    filename: str = Field(description="文件名")
    file_type: str = Field(description="文件类型: code/document/data")
    description: str = Field(description="文件描述")

class FileGenerationTool(BaseTool):
    """Agent文件生成工具"""
    
    name = "generate_file"
    description = "生成文件并保存到存储系统"
    parameters_model = FileGenerationParams
    
    def __init__(self, file_service: FileService):
        super().__init__()
        self.file_service = file_service
    
    async def run_async(
        self, 
        args: Dict, 
        tool_context: Any
    ) -> Dict:
        """执行文件生成"""
        params = FileGenerationParams(**args)
        
        # 创建文件内容的字节流
        file_content = io.BytesIO(params.content.encode('utf-8'))
        
        # 从工具上下文获取用户和对话信息
        user_id = tool_context.get("user_id")
        conversation_id = tool_context.get("conversation_id")
        
        # 上传文件
        file_info = await self.file_service.upload_file(
            file=file_content,
            user_id=user_id,
            conversation_id=conversation_id,
            original_filename=params.filename,
            description=params.description,
            tags=[params.file_type, "agent_generated"]
        )
        
        return {
            "success": True,
            "file_id": file_info["id"],
            "filename": file_info["filename"],
            "download_url": file_info["download_url"],
            "preview_url": file_info["preview_url"],
            "message": f"文件 {params.filename} 已生成并保存"
        }
```

#### Agent集成示例

```python
# src/agent/buyer_agent.py 更新
class BuyerDevelopmentAgent(BaseTradeAgent):
    """买家开发Agent - 集成文件生成功能"""
    
    def _init_tools(self):
        return [
            TradeDataSearchTool(),
            BuyerRecommendationTool(),
            EmailGeneratorTool(),
            TranslationTool(),
            FileGenerationTool(file_service)  # 新增文件生成工具
        ]
    
    def _get_instruction(self):
        return """
        你是TradeFlow的专业买家开发助手，帮助出口商找到合适的海外买家。
        
        核心能力：
        1. 根据产品信息智能匹配潜在买家
        2. 分析目标市场需求和趋势
        3. 生成专业的开发信模板和业务文档
        4. 提供文化适配的沟通建议
        
        文件生成能力：
        - 当需要生成开发信模板时，使用generate_file工具保存为.txt或.md文件
        - 生成市场分析报告时，保存为.md文件方便阅读
        - 创建联系人列表时，保存为.csv文件方便后续使用
        - 代码示例保存为相应的代码文件格式
        
        文件命名规则：
        - 使用描述性文件名，包含日期
        - 例如：buyer_development_email_template_2024-01-19.txt
        - 市场分析报告：market_analysis_LED_US_2024-01-19.md
        """
```

### 存储策略设计

#### 生命周期管理

```python
# src/backend/services/storage_lifecycle.py
from enum import Enum
from datetime import datetime, timedelta
import asyncio

class FileLifecycleStage(Enum):
    ACTIVE = "active"           # 活跃使用中
    ARCHIVED = "archived"       # 已归档
    TO_DELETE = "to_delete"     # 待删除
    DELETED = "deleted"         # 已删除

class StorageLifecycleManager:
    """存储生命周期管理"""
    
    def __init__(self, minio_client, db_session):
        self.minio_client = minio_client
        self.db_session = db_session
    
    async def manage_lifecycle(self):
        """执行存储生命周期管理"""
        # 1. 标记长期未访问的文件为归档状态
        await self._mark_inactive_files()
        
        # 2. 将归档文件移动到低成本存储
        await self._archive_old_files()
        
        # 3. 删除过期文件
        await self._cleanup_expired_files()
        
        # 4. 清理临时文件
        await self._cleanup_temp_files()
    
    async def _mark_inactive_files(self):
        """标记90天未访问的文件为归档"""
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        
        # 查询长期未访问的活跃文件
        inactive_files = await self.db_session.execute(
            """
            UPDATE files 
            SET lifecycle_stage = 'archived', updated_at = NOW()
            WHERE lifecycle_stage = 'active' 
              AND last_accessed < :cutoff_date
            """,
            {"cutoff_date": cutoff_date}
        )
        
        await self.db_session.commit()
    
    async def _archive_old_files(self):
        """将归档文件移动到归档bucket"""
        archived_files = await self.db_session.execute(
            """
            SELECT id, minio_bucket, minio_object_key
            FROM files 
            WHERE lifecycle_stage = 'archived' 
              AND minio_bucket != 'tradeflow-archives'
            """
        )
        
        for file_record in archived_files:
            try:
                # 复制到归档bucket
                self.minio_client.copy_object(
                    bucket_name="tradeflow-archives",
                    object_name=file_record.minio_object_key,
                    source=f"{file_record.minio_bucket}/{file_record.minio_object_key}"
                )
                
                # 删除原文件
                self.minio_client.remove_object(
                    bucket_name=file_record.minio_bucket,
                    object_name=file_record.minio_object_key
                )
                
                # 更新数据库记录
                await self.db_session.execute(
                    """
                    UPDATE files 
                    SET minio_bucket = 'tradeflow-archives'
                    WHERE id = :file_id
                    """,
                    {"file_id": file_record.id}
                )
                
            except Exception as e:
                logging.error(f"Failed to archive file {file_record.id}: {str(e)}")
        
        await self.db_session.commit()
    
    async def _cleanup_expired_files(self):
        """删除标记为删除且超过保留期的文件"""
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        expired_files = await self.db_session.execute(
            """
            SELECT id, minio_bucket, minio_object_key
            FROM files 
            WHERE lifecycle_stage = 'to_delete' 
              AND updated_at < :cutoff_date
            """,
            {"cutoff_date": cutoff_date}
        )
        
        for file_record in expired_files:
            try:
                # 从MinIO删除
                self.minio_client.remove_object(
                    bucket_name=file_record.minio_bucket,
                    object_name=file_record.minio_object_key
                )
                
                # 更新数据库状态
                await self.db_session.execute(
                    """
                    UPDATE files 
                    SET lifecycle_stage = 'deleted', minio_object_key = NULL
                    WHERE id = :file_id
                    """,
                    {"file_id": file_record.id}
                )
                
            except Exception as e:
                logging.error(f"Failed to delete expired file {file_record.id}: {str(e)}")
        
        await self.db_session.commit()
```

### 安全策略

#### 访问控制

```python
# src/backend/middleware/file_access_control.py
from fastapi import HTTPException, Depends
from ..auth.jwt_auth import get_current_user

class FileAccessControl:
    """文件访问控制中间件"""
    
    def __init__(self, db_session):
        self.db_session = db_session
    
    async def check_file_access(
        self, 
        file_id: str, 
        operation: str,  # 'read', 'write', 'delete'
        current_user = Depends(get_current_user)
    ):
        """检查文件访问权限"""
        
        # 获取文件记录
        file_record = await self.db_session.get(FileRecord, file_id)
        if not file_record:
            raise HTTPException(404, "File not found")
        
        # 检查所有权
        if file_record.user_id != current_user.id:
            raise HTTPException(403, "Access denied")
        
        # 检查文件状态
        if file_record.lifecycle_stage == 'deleted':
            raise HTTPException(410, "File has been deleted")
        
        # 检查操作权限
        if operation == 'delete' and file_record.is_generated:
            # 生成的文件可能有特殊删除规则
            pass
        
        return file_record
```

#### 数据加密

```python
# src/backend/utils/encryption.py
from cryptography.fernet import Fernet
import base64
import os

class FileEncryption:
    """敏感文件加密工具"""
    
    def __init__(self):
        # 从环境变量获取加密密钥
        key = os.environ.get('FILE_ENCRYPTION_KEY')
        if not key:
            key = Fernet.generate_key()
            # 在生产环境中，这应该安全存储
            print(f"Generated encryption key: {key.decode()}")
        else:
            key = key.encode()
        
        self.cipher = Fernet(key)
    
    def encrypt_content(self, content: bytes) -> bytes:
        """加密文件内容"""
        return self.cipher.encrypt(content)
    
    def decrypt_content(self, encrypted_content: bytes) -> bytes:
        """解密文件内容"""
        return self.cipher.decrypt(encrypted_content)
    
    def should_encrypt_file(self, filename: str, content_type: str) -> bool:
        """判断文件是否需要加密"""
        # 包含敏感信息的文件类型需要加密
        sensitive_patterns = [
            'contract', 'agreement', 'invoice', 
            'financial', 'personal', 'confidential'
        ]
        
        filename_lower = filename.lower()
        return any(pattern in filename_lower for pattern in sensitive_patterns)
```

### 备份策略

```python
# src/backend/services/backup_service.py
import asyncio
from datetime import datetime, timedelta

class MinIOBackupService:
    """MinIO数据备份服务"""
    
    def __init__(self, minio_client, backup_config):
        self.minio_client = minio_client
        self.backup_config = backup_config
        self.backup_bucket = "tradeflow-backups"
    
    async def create_daily_backup(self):
        """创建每日备份"""
        today = datetime.now().strftime('%Y-%m-%d')
        backup_prefix = f"daily/{today}/"
        
        # 备份用户文件
        await self._backup_bucket_contents(
            source_bucket="tradeflow-files",
            backup_prefix=backup_prefix + "files/"
        )
        
        # 备份数据库（如果需要）
        await self._backup_database_dumps(backup_prefix + "database/")
    
    async def _backup_bucket_contents(self, source_bucket: str, backup_prefix: str):
        """备份bucket内容"""
        objects = self.minio_client.list_objects(
            bucket_name=source_bucket,
            recursive=True
        )
        
        backup_tasks = []
        for obj in objects:
            # 跳过已经备份的文件
            backup_key = backup_prefix + obj.object_name
            if not self._object_exists(self.backup_bucket, backup_key):
                task = self._copy_object_to_backup(
                    source_bucket, obj.object_name, backup_key
                )
                backup_tasks.append(task)
        
        # 并发执行备份任务
        await asyncio.gather(*backup_tasks)
    
    async def _copy_object_to_backup(
        self, 
        source_bucket: str, 
        source_key: str, 
        backup_key: str
    ):
        """复制对象到备份bucket"""
        try:
            self.minio_client.copy_object(
                bucket_name=self.backup_bucket,
                object_name=backup_key,
                source=f"{source_bucket}/{source_key}"
            )
        except Exception as e:
            logging.error(f"Backup failed for {source_key}: {str(e)}")
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
      - MINIO_ENDPOINT=minio:9000
      - MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY:-tradeflow_access_key}
      - MINIO_SECRET_KEY=${MINIO_SECRET_KEY:-tradeflow_secret_key}
      - MINIO_SECURE=false
    depends_on:
      - postgres
      - mongodb
      - redis
      - minio
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
    ports:
      - "5432:5432"
    
  mongodb:
    image: mongo:6
    volumes:
      - mongo_data:/data/db
    ports:
      - "27017:27017"
    
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
  
  minio:
    image: minio/minio:latest
    container_name: tradeflow-minio
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio_data:/data
    environment:
      MINIO_ACCESS_KEY: ${MINIO_ACCESS_KEY:-tradeflow_access_key}
      MINIO_SECRET_KEY: ${MINIO_SECRET_KEY:-tradeflow_secret_key}
      MINIO_BROWSER_REDIRECT_URL: http://localhost:9001
    command: server /data --console-address ":9001"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 20s
      retries: 3
  
  # MinIO客户端初始化服务（可选）
  minio-init:
    image: minio/mc:latest
    depends_on:
      - minio
    volumes:
      - ./scripts/minio-init.sh:/init.sh:ro
    entrypoint: ["/bin/sh", "/init.sh"]
    environment:
      MINIO_ACCESS_KEY: ${MINIO_ACCESS_KEY:-tradeflow_access_key}
      MINIO_SECRET_KEY: ${MINIO_SECRET_KEY:-tradeflow_secret_key}

volumes:
  postgres_data:
  mongo_data:
  redis_data:
  minio_data:
```

#### MinIO初始化脚本

```bash
# scripts/minio-init.sh
#!/bin/bash

# 等待MinIO服务启动
sleep 10

# 配置mc客户端
mc alias set minio http://minio:9000 $MINIO_ACCESS_KEY $MINIO_SECRET_KEY

# 创建必要的bucket
mc mb minio/tradeflow-files --ignore-existing
mc mb minio/tradeflow-temp --ignore-existing  
mc mb minio/tradeflow-backups --ignore-existing
mc mb minio/tradeflow-archives --ignore-existing

# 设置文件bucket的公共读取策略
mc policy set public minio/tradeflow-files

# 设置生命周期规则
mc lifecycle add minio/tradeflow-temp --expiry 7d
mc lifecycle add minio/tradeflow-files --transition-days 30 --tier STANDARD_IA

echo "MinIO initialization completed"
```

### 生产部署配置

#### Cloud Run + Cloud Storage混合方案

对于生产环境，我们推荐使用Cloud Run部署应用服务，同时保持MinIO作为对象存储，以在成本和性能之间取得平衡：

```bash
#!/bin/bash
# deploy.sh

# 设置项目变量
PROJECT_ID="tradeflow-production"
REGION="us-central1"
MINIO_INSTANCE="tradeflow-minio-vm"

# 1. 部署MinIO到GCE实例
gcloud compute instances create $MINIO_INSTANCE \
  --zone=${REGION}-a \
  --machine-type=e2-standard-2 \
  --boot-disk-size=50GB \
  --boot-disk-type=pd-ssd \
  --image-family=ubuntu-2004-lts \
  --image-project=ubuntu-os-cloud \
  --tags=minio-server \
  --metadata-from-file startup-script=scripts/minio-gce-startup.sh

# 2. 配置防火墙规则
gcloud compute firewall-rules create allow-minio \
  --allow tcp:9000,tcp:9001 \
  --source-ranges 0.0.0.0/0 \
  --target-tags minio-server

# 3. 构建后端镜像
gcloud builds submit --tag gcr.io/${PROJECT_ID}/tradeflow-backend

# 4. 部署到Cloud Run
gcloud run deploy tradeflow-backend \
  --image gcr.io/${PROJECT_ID}/tradeflow-backend \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars="
    GOOGLE_CLOUD_PROJECT=${PROJECT_ID},
    DATABASE_URL=${DATABASE_URL},
    MONGODB_URL=${MONGODB_URL},
    REDIS_URL=${REDIS_URL},
    MINIO_ENDPOINT=${MINIO_EXTERNAL_IP}:9000,
    MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY},
    MINIO_SECRET_KEY=${MINIO_SECRET_KEY},
    MINIO_SECURE=true
  " \
  --min-instances=1 \
  --max-instances=10 \
  --memory=2Gi \
  --cpu=2
```

#### GCE上的MinIO部署脚本

```bash
# scripts/minio-gce-startup.sh
#!/bin/bash

# 更新系统
apt-get update
apt-get install -y curl

# 安装MinIO
wget https://dl.min.io/server/minio/release/linux-amd64/minio
chmod +x minio
sudo mv minio /usr/local/bin/

# 创建MinIO用户和数据目录
sudo useradd -r minio-user -s /sbin/nologin
sudo mkdir -p /opt/minio/data
sudo chown minio-user:minio-user /opt/minio/data

# 创建MinIO配置
cat > /etc/default/minio << EOF
MINIO_ACCESS_KEY="${MINIO_ACCESS_KEY}"
MINIO_SECRET_KEY="${MINIO_SECRET_KEY}"
MINIO_VOLUMES="/opt/minio/data"
MINIO_OPTS="--console-address :9001"
EOF

# 创建systemd服务
cat > /etc/systemd/system/minio.service << EOF
[Unit]
Description=MinIO
Documentation=https://docs.min.io
Wants=network-online.target
After=network-online.target
AssertFileIsExecutable=/usr/local/bin/minio

[Service]
WorkingDirectory=/opt/minio
User=minio-user
Group=minio-user
EnvironmentFile=/etc/default/minio
ExecStartPre=/bin/bash -c "if [ -z \"\${MINIO_ACCESS_KEY}\" ]; then echo \"MINIO_ACCESS_KEY not set in /etc/default/minio\"; exit 1; fi"
ExecStart=/usr/local/bin/minio server \$MINIO_OPTS \$MINIO_VOLUMES
Restart=always
LimitNOFILE=65536
TasksMax=infinity
TimeoutStopSec=infinity
SendSIGKILL=no

[Install]
WantedBy=multi-user.target
EOF

# 启动MinIO服务
systemctl daemon-reload
systemctl enable minio
systemctl start minio

# 安装和配置MinIO客户端
wget https://dl.min.io/client/mc/release/linux-amd64/mc
chmod +x mc
sudo mv mc /usr/local/bin/

# 等待服务启动后初始化bucket
sleep 30
/usr/local/bin/mc alias set local http://localhost:9000 $MINIO_ACCESS_KEY $MINIO_SECRET_KEY
/usr/local/bin/mc mb local/tradeflow-files --ignore-existing
/usr/local/bin/mc mb local/tradeflow-temp --ignore-existing
/usr/local/bin/mc mb local/tradeflow-backups --ignore-existing
/usr/local/bin/mc policy set public local/tradeflow-files

echo "MinIO setup completed"
```

#### 环境变量配置

```bash
# .env.production
# 数据库配置
DATABASE_URL=postgresql://user:password@postgres-instance:5432/tradeflow
MONGODB_URL=mongodb+srv://user:password@mongodb-cluster/tradeflow
REDIS_URL=redis://redis-instance:6379

# MinIO配置
MINIO_ENDPOINT=your-minio-server.com:9000
MINIO_ACCESS_KEY=your-production-access-key
MINIO_SECRET_KEY=your-production-secret-key
MINIO_SECURE=true

# JWT配置
JWT_SECRET_KEY=your-jwt-secret-key

# OAuth配置
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# 文件上传限制
MAX_FILE_SIZE=50MB
ALLOWED_FILE_TYPES=.pdf,.docx,.txt,.md,.py,.js,.json,.csv,.xlsx,.png,.jpg,.svg

# 加密配置
FILE_ENCRYPTION_KEY=your-file-encryption-key
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