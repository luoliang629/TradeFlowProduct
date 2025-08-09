# TradeFlow - 全球B2B贸易智能助手

> **基于对话式AI Agent的B2B贸易智能助手**  
> 通过自然语言交互帮助用户完成买家开发、供应商采购等贸易业务

[![服务状态](https://img.shields.io/badge/服务状态-运行中-green)](http://localhost:8000/api/v1/health)
[![API文档](https://img.shields.io/badge/API-文档-blue)](http://localhost:8000/api/v1/docs)
[![前端应用](https://img.shields.io/badge/前端-React-lightblue)](http://localhost:3000)

## ✨ 核心特色

- 🤖 **智能对话交互** - Google ADK驱动的专业贸易AI助手
- 🔍 **供应链分析** - 从商品页面追溯完整供应商网络  
- 📊 **真实贸易数据** - 集成海关数据和企业信息查询
- ⚡ **实时响应** - SSE流式响应，支持并发用户会话
- 🌐 **现代化界面** - React前端，响应式设计
- 🔐 **企业级安全** - JWT认证，Redis会话管理，完整的权限控制

## 🚀 快速开始

### 系统要求
- Python 3.11+
- Node.js 18+
- PostgreSQL, MongoDB, Redis
- Google ADK API Key

### 1. 启动后端服务（核心）
```bash
cd src/backend
pip install -r requirements.txt

# 启动依赖服务（PostgreSQL, MongoDB, Redis）
# 详见 midware_config.md

# 启动API服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 验证系统状态
```bash
# 健康检查
curl http://localhost:8000/api/v1/health

# API文档
open http://localhost:8000/api/v1/docs
```

### 3. 启动前端（可选）
```bash
cd src/frontend
npm install
npm run dev
# 访问 http://localhost:3000
```

## 🎯 核心功能展示

### 智能供应商发现
```bash
# API示例
curl -X POST http://localhost:8000/api/v1/agent/query \
  -H "Content-Type: application/json" \
  -d '{
    "message": "分析这个商品的供应商：https://www.walmart.com/ip/Apple-iPhone-15",
    "session_id": "test_session"
  }'
```

### 贸易数据查询
```bash
curl -X POST http://localhost:8000/api/v1/agent/query \
  -H "Content-Type: application/json" \
  -d '{
    "message": "查询2024年手机对美国的出口数据",
    "session_id": "trade_analysis"
  }'
```

### 企业背景调查
```bash
curl -X POST http://localhost:8000/api/v1/agent/query \
  -H "Content-Type: application/json" \
  -d '{
    "message": "分析比亚迪电子的供应商资质和贸易能力",
    "session_id": "supplier_check"
  }'
```

## 🏗️ 系统架构

```
TradeFlow 全栈架构
├── 前端层 (React + TypeScript)
│   ├── 用户界面：聊天交互、数据展示、文件管理
│   ├── 实时通信：SSE连接、状态管理
│   └── 认证授权：JWT token、OAuth集成
├── 后端层 (FastAPI + Python)  
│   ├── API网关：RESTful接口、参数验证
│   ├── 业务逻辑：Agent集成、会话管理、缓存优化
│   ├── 认证服务：JWT认证、用户权限管理
│   └── 数据持久化：PostgreSQL、MongoDB存储
├── AI Agent层 (Google ADK)
│   ├── TradeFlow Agent：贸易领域专业AI助手
│   ├── 推理引擎：ReAct框架、多Agent协作
│   ├── 工具集成：搜索、数据分析、网页解析
│   └── 知识库：贸易流程、供应链数据
└── 基础设施层
    ├── 缓存层：Redis（会话、性能优化）
    ├── 存储层：MinIO（文件存储）
    └── 监控层：健康检查、性能监控
```

## 📁 项目结构

```
TradeFlow/
├── src/
│   ├── backend/           # FastAPI后端服务 ✅ 已完成
│   │   ├── app/          # 应用核心代码
│   │   ├── tests/        # 自动化测试
│   │   └── alembic/      # 数据库迁移
│   ├── frontend/         # React前端应用 ✅ 已完成  
│   │   ├── src/         # 组件和页面
│   │   └── public/      # 静态资源
│   └── agent/           # TradeFlow AI Agent ✅ 已完成
│       └── TradeFlowAgent/  # Google ADK实现
├── docs/                # 项目文档
│   ├── api/            # API接口规范
│   ├── development/    # 开发指南
│   └── requirements/   # 需求文档
└── README.md          # 项目概览（本文件）
```

## 🔧 技术栈

### 后端技术栈
- **API框架**: FastAPI 0.104+ (异步高性能)
- **数据库**: PostgreSQL 15+ (关系型数据), MongoDB 7+ (文档数据)
- **缓存**: Redis 7+ (会话管理、性能优化)
- **对象存储**: MinIO (文件存储)
- **认证**: JWT + OAuth 2.0
- **部署**: Docker + Docker Compose

### AI Agent技术栈  
- **AI框架**: Google ADK (Agent Development Kit)
- **推理模型**: Gemini 2.0 Flash, Claude Sonnet 4
- **推理框架**: ReAct (Reasoning and Acting)
- **工具集成**: Jina Search API, Tendata贸易数据
- **执行环境**: Python 3.11+

### 前端技术栈
- **框架**: React 18+ + TypeScript
- **状态管理**: Redux Toolkit
- **UI组件**: 现代化响应式设计
- **实时通信**: Server-Sent Events (SSE)
- **构建工具**: Vite + ESBuild

## 🌟 关键特性详解

### 1. 智能Agent集成
- **TradeFlow Agent**: 基于Google ADK的专业贸易AI助手
- **流式响应**: SSE实时输出，提升用户体验
- **连接池优化**: Runner连接复用，降低延迟
- **智能缓存**: Redis缓存常见查询，加速响应

### 2. 企业级认证系统
- **JWT认证**: 无状态token认证机制
- **OAuth集成**: 支持Google、GitHub登录
- **权限管理**: 基于角色的访问控制
- **会话管理**: Redis分布式会话存储

### 3. 高性能后端架构
- **异步设计**: FastAPI异步处理，支持高并发
- **智能缓存**: 多层缓存策略，优化数据访问
- **健康监控**: 完整的健康检查和监控体系
- **错误处理**: 分类错误处理，自动重试机制

### 4. 现代化前端体验
- **响应式设计**: 支持桌面、平板、移动端
- **实时交互**: SSE实现实时对话体验  
- **状态管理**: Redux统一状态管理
- **类型安全**: TypeScript全栈类型保护

## 🛡️ 部署与运维

### 开发环境部署
```bash
# 克隆项目
git clone <repository-url>
cd TradeFlowProduct

# 启动全栈开发环境
docker-compose -f docker-compose.dev.yml up -d

# 验证服务状态
curl http://localhost:8000/api/v1/health
```

### 生产环境部署
```bash
# 构建生产镜像
docker-compose -f docker-compose.prod.yml build

# 启动生产服务
docker-compose -f docker-compose.prod.yml up -d

# 监控服务状态
docker-compose logs -f backend
```

### 服务监控
```bash
# 健康检查端点
GET /api/v1/health              # 基础健康检查
GET /api/v1/health/detailed     # 详细组件状态  
GET /api/v1/health/readiness    # 就绪性检查
GET /api/v1/health/liveness     # 存活性检查
```

## 📖 使用指南

### API使用示例

**1. 获取访问令牌**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "demo", "password": "demo123"}'
```

**2. 查询AI Agent**
```bash
curl -X POST http://localhost:8000/api/v1/agent/query \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "分析苹果公司的主要供应商",
    "session_id": "analysis_session",
    "stream": true
  }'
```

**3. 管理对话会话**
```bash
# 获取会话列表
curl -X GET http://localhost:8000/api/v1/chat/sessions \
  -H "Authorization: Bearer <token>"

# 创建新会话
curl -X POST http://localhost:8000/api/v1/chat/sessions \
  -H "Authorization: Bearer <token>" \
  -d '{"title": "供应商分析会话"}'
```

### Agent能力展示

TradeFlow Agent具备以下核心能力：

1. **商品供应商发现** - 从商品链接追溯完整供应链
2. **贸易数据查询** - 基于真实海关数据的贸易分析
3. **企业背景调查** - 供应商资质和贸易能力评估
4. **市场趋势分析** - 行业发展趋势和竞争分析
5. **B2B平台搜索** - 整合阿里巴巴等B2B平台数据

详细使用指南请参考：[Agent使用文档](src/agent/TradeFlowAgent/README.md)

## 🔧 开发指南

### 后端开发
```bash
cd src/backend
poetry install              # 安装依赖
poetry run pytest          # 运行测试
poetry run alembic upgrade head  # 数据库迁移
poetry run uvicorn app.main:app --reload  # 启动开发服务
```

### 前端开发
```bash
cd src/frontend
npm install                 # 安装依赖
npm run dev                # 启动开发服务
npm run test               # 运行测试
npm run build             # 构建生产版本
```

### Agent开发
```bash
cd src/agent/TradeFlowAgent
pip install -r requirements.txt
adk web                    # 启动Agent Web界面
python test/test_phase8_product_supplier_discovery.py  # 运行核心功能测试
```

## 🐛 故障排除

### 常见问题

**1. Agent连接失败**
```bash
# 检查Agent配置
curl http://localhost:8000/api/v1/health/detailed
# 验证Google ADK Runner状态
```

**2. 数据库连接错误**  
```bash
# 检查数据库服务状态
docker-compose ps
# 验证连接配置
poetry run python -c "from app.core.database import test_connection; test_connection()"
```

**3. 缓存服务异常**
```bash
# 重启Redis服务
docker-compose restart redis
# 清空缓存
redis-cli -h localhost -p 6379 -a root flushdb
```

### 性能调优

**1. Agent响应优化**
- 调整`AGENT_RUNNER_POOL_SIZE`增加并发处理能力
- 启用`AGENT_ENABLE_CACHE`缓存常见查询结果
- 优化`AGENT_TIMEOUT_SECONDS`平衡响应速度和准确性

**2. 数据库性能优化**
- 配置PostgreSQL连接池大小
- 启用MongoDB索引优化查询性能
- 调整Redis内存分配和持久化策略

## 📊 项目状态

### ✅ 已完成功能
- [x] 后端API服务 - FastAPI完整实现
- [x] Agent集成服务 - Google ADK集成和优化
- [x] 认证授权系统 - JWT + OAuth
- [x] 会话管理系统 - Redis分布式会话
- [x] 前端UI界面 - React响应式设计
- [x] 实时通信 - SSE流式响应
- [x] 健康检查监控 - 完整监控体系
- [x] 数据库设计 - PostgreSQL + MongoDB
- [x] 缓存优化 - Redis多层缓存
- [x] 容器化部署 - Docker + Docker Compose

### 🚧 开发中功能
- [ ] 支付系统集成 (Stripe)
- [ ] 高级权限管理
- [ ] 数据导出功能
- [ ] 移动端适配优化
- [ ] 国际化多语言支持

### 🔮 计划功能
- [ ] 微服务架构迁移
- [ ] AI模型私有化部署
- [ ] 高级数据分析工具
- [ ] 企业级SSO集成
- [ ] API速率限制和配额管理

## 📝 API文档

完整的API文档可通过以下方式访问：

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc  
- **OpenAPI规范**: http://localhost:8000/api/v1/openapi.json

主要API端点：

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/v1/health` | GET | 系统健康检查 |
| `/api/v1/auth/login` | POST | 用户登录认证 |
| `/api/v1/agent/query` | POST | AI Agent查询 |
| `/api/v1/chat/sessions` | GET/POST | 会话管理 |
| `/api/v1/agent/stream` | GET | SSE流式响应 |

详细的API规范文档请参考：[docs/api/](docs/api/)

## 🤝 贡献指南

1. Fork项目仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交代码变更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交Pull Request

### 开发规范
- 遵循项目代码风格 (Black, ESLint)
- 添加相应的单元测试
- 更新相关文档
- 确保CI/CD流水线通过

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源许可证。

## 📞 支持与联系

- **问题反馈**: 请提交 [GitHub Issues](issues)
- **功能建议**: 欢迎提交 Feature Request
- **技术讨论**: 参与 [Discussions](discussions)

---

**TradeFlow** - 让B2B贸易更智能，让供应商发现更精准！ 🚀

*最后更新: 2025-01-09*