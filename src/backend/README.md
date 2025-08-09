# TradeFlow Backend API

TradeFlow B2B贸易智能助手后端API服务，基于FastAPI构建的现代化、高性能的Web API。

> **状态**: ✅ 生产就绪 | **服务地址**: http://localhost:8000 | **文档**: http://localhost:8000/api/v1/docs

## 🚀 核心能力

- **🤖 AI Agent集成** - 完整的TradeFlowAgent包装层，使用Google ADK Runner API
- **⚡ SSE流式响应** - 实时Agent响应流转换器，支持并发用户
- **🔄 Redis会话管理** - 分布式用户会话和上下文管理  
- **🏎️ 性能优化** - Runner连接池、响应缓存、Token监控
- **🛡️ 错误处理** - 重试机制、分类错误处理、优雅降级
- **🔐 认证系统** - JWT token认证和用户权限管理
- **💬 聊天系统** - 支持多用户并发对话管理

## 技术栈

- **框架**: FastAPI
- **数据库**: PostgreSQL, MongoDB
- **缓存**: Redis
- **对象存储**: MinIO
- **异步**: asyncio, asyncpg, motor
- **认证**: JWT
- **日志**: structlog
- **测试**: pytest, httpx
- **部署**: Docker, Docker Compose

## 📋 已实现功能清单

### 🔥 核心功能 (已完成)
- ✅ **Agent集成服务** - TradeFlowAgent完整包装，Google ADK Runner API集成
- ✅ **SSE流式响应** - 实时Agent响应转换，支持流式输出和并发处理
- ✅ **Redis会话管理** - 分布式用户会话存储，上下文持久化管理
- ✅ **性能优化系统** - Runner连接池、智能缓存、Token使用监控
- ✅ **错误处理机制** - 自动重试、分类错误处理、优雅降级策略
- ✅ **认证授权系统** - JWT认证、OAuth集成、权限管理
- ✅ **聊天会话系统** - 多用户并发对话、消息历史管理

### 🏗️ 基础设施 (已完成)
- ✅ **异步API架构** - FastAPI异步设计，高性能并发处理
- ✅ **结构化日志** - 完整的请求追踪和业务事件记录
- ✅ **健康检查监控** - Kubernetes风格的Liveness/Readiness检查
- ✅ **数据库设计** - PostgreSQL关系型数据 + MongoDB文档数据
- ✅ **缓存优化** - Redis多层缓存，查询性能优化
- ✅ **容器化部署** - Docker + Docker Compose生产就绪配置
- ✅ **测试覆盖** - 单元测试、集成测试、Agent集成测试

## 快速开始

### 环境要求

- Python 3.11+
- Poetry (依赖管理)
- Docker & Docker Compose (推荐)

### 本地开发

1. **克隆项目**
   ```bash
   cd src/backend
   ```

2. **安装依赖**
   ```bash
   poetry install
   ```

3. **环境配置**
   ```bash
   cp .env.example .env
   # 编辑.env文件，配置数据库连接等
   ```

4. **启动依赖服务**
   ```bash
   # 根据 midware_config.md 中的配置，确保以下服务运行：
   # - PostgreSQL (localhost:5432, user: postgres, password: root)
   # - MongoDB (localhost:27017)
   # - Redis (localhost:6379, password: root)
   # - MinIO (localhost:9000, user: root, password: rootpassword)
   ```

5. **数据库迁移**
   ```bash
   poetry run alembic upgrade head
   ```

6. **启动应用**
   ```bash
   poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Docker部署

1. **构建并启动所有服务**
   ```bash
   docker-compose up -d --build
   ```

2. **查看服务状态**
   ```bash
   docker-compose ps
   ```

3. **查看日志**
   ```bash
   docker-compose logs -f backend
   ```

## 🚀 API使用指南

### 核心API端点

| 端点类别 | 方法 | 端点 | 描述 |
|---------|------|------|------|
| **🤖 Agent** | POST | `/api/v1/agent/query` | AI Agent查询接口 |
| **📡 流式** | GET | `/api/v1/agent/stream` | SSE流式响应接口 |
| **🔐 认证** | POST | `/api/v1/auth/login` | 用户登录认证 |
| **💬 会话** | GET/POST | `/api/v1/chat/sessions` | 会话管理接口 |
| **❤️ 健康** | GET | `/api/v1/health` | 服务健康检查 |

### Agent查询示例

```bash
# 基础Agent查询
curl -X POST "http://localhost:8000/api/v1/agent/query" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "message": "分析苹果公司的主要供应商",
    "session_id": "supplier_analysis_session",
    "stream": false
  }'

# 流式响应查询
curl -X POST "http://localhost:8000/api/v1/agent/query" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "message": "查询2024年手机对美国的出口数据",
    "session_id": "trade_analysis_session",
    "stream": true
  }'
```

### Agent功能展示

**🛒 商品供应商发现**
```bash
curl -X POST "http://localhost:8000/api/v1/agent/query" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "分析这个商品的供应商：https://www.walmart.com/ip/Apple-iPhone-15",
    "session_id": "product_analysis"
  }'
```

**📊 贸易数据查询**
```bash
curl -X POST "http://localhost:8000/api/v1/agent/query" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "查询比亚迪电子2024年的出口数据和主要市场",
    "session_id": "trade_data"
  }'
```

**🏭 企业背景调查**
```bash
curl -X POST "http://localhost:8000/api/v1/agent/query" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "分析富士康科技集团的供应商资质和贸易能力",
    "session_id": "company_research"
  }'
```

### SSE流式响应

```javascript
// 前端JavaScript示例
const eventSource = new EventSource(
  'http://localhost:8000/api/v1/agent/stream?session_id=your_session_id&token=your_jwt_token'
);

eventSource.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log('Agent响应:', data.content);
};

eventSource.onerror = function(event) {
  console.error('SSE连接错误:', event);
};
```

### API文档访问

启动服务后，可通过以下地址访问完整API文档：

- **📖 Swagger UI**: http://localhost:8000/api/v1/docs
- **📚 ReDoc**: http://localhost:8000/api/v1/redoc  
- **📄 OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

### 健康检查端点

| 检查类型 | 端点 | 用途 |
|----------|------|------|
| **基础检查** | `GET /api/v1/health` | 快速健康状态 |
| **详细检查** | `GET /api/v1/health/detailed` | 所有组件状态 |
| **存活检查** | `GET /api/v1/health/liveness` | Kubernetes存活探针 |
| **就绪检查** | `GET /api/v1/health/readiness` | Kubernetes就绪探针 |

```bash
# 检查所有服务组件状态
curl http://localhost:8000/api/v1/health/detailed | jq

# 示例输出
{
  "status": "healthy",
  "checks": {
    "database": "healthy",
    "redis": "healthy", 
    "agent_runner": "healthy",
    "mongodb": "healthy"
  },
  "agent_status": {
    "runner_pool_size": 5,
    "active_connections": 2,
    "cache_hit_rate": 0.85
  }
}
```

## 测试

### 🧪 测试执行

```bash
# 运行所有测试
poetry run pytest -v

# Agent集成测试（核心功能）
poetry run pytest tests/test_agent_integration.py -v

# 健康检查测试
poetry run pytest tests/test_health.py -v

# 带覆盖率的测试报告
poetry run pytest --cov=app --cov-report=html --cov-report=term-missing

# 运行特定标记的测试
poetry run pytest -m unit          # 单元测试
poetry run pytest -m integration   # 集成测试
poetry run pytest -m agent         # Agent相关测试
```

### 测试分类说明

| 标记 | 类型 | 说明 |
|------|------|------|
| `unit` | 单元测试 | 独立组件功能测试 |
| `integration` | 集成测试 | 多组件协作测试 |
| `agent` | Agent测试 | AI Agent功能和集成测试 |
| `slow` | 慢测试 | 需要较长执行时间的测试 |

### 🔍 Agent功能验证

```bash
# 验证Agent服务状态
curl http://localhost:8000/api/v1/health/detailed

# 测试Agent基础查询
curl -X POST "http://localhost:8000/api/v1/agent/query" \
  -H "Content-Type: application/json" \
  -d '{"message": "你好，请介绍TradeFlow的功能", "session_id": "test"}'

# 运行完整Agent集成测试
poetry run python -m pytest tests/test_agent_integration.py::test_agent_query -v
```

## 📁 项目结构详解

```
src/backend/
├── app/                           # 🏠 应用核心代码
│   ├── api/                      # 🌐 API路由层
│   │   ├── monitoring.py         # 📊 监控端点
│   │   └── v1/                  # API版本1
│   │       ├── agent.py         # 🤖 Agent相关API
│   │       ├── auth.py          # 🔐 认证授权API
│   │       ├── chat.py          # 💬 聊天会话API
│   │       └── health.py        # ❤️ 健康检查API
│   ├── core/                     # 🎯 核心基础模块
│   │   ├── database.py          # 🛢️ 数据库连接配置
│   │   ├── logging.py           # 📝 结构化日志配置
│   │   └── exceptions.py        # ⚠️ 统一异常定义
│   ├── middleware/               # 🔧 中间件层
│   │   ├── cors.py             # 🌍 跨域处理
│   │   ├── error_handler.py    # 🚨 错误处理中间件
│   │   ├── logging.py          # 📋 日志中间件
│   │   ├── metrics.py          # 📈 性能指标收集
│   │   └── performance.py      # ⚡ 性能监控中间件
│   ├── models/                   # 🏗️ 数据模型层
│   │   ├── user.py             # 👤 用户模型
│   │   ├── conversation.py     # 💭 对话模型
│   │   └── ...
│   ├── services/                 # 🔧 业务逻辑服务层
│   │   ├── agent_service.py     # 🤖 Agent核心服务
│   │   ├── agent_performance_optimizer.py  # ⚡ Agent性能优化
│   │   ├── agent_error_handler.py         # 🚨 Agent错误处理
│   │   ├── sse_converter.py     # 📡 SSE流式转换器
│   │   ├── session_manager.py   # 🗂️ 会话管理服务
│   │   ├── cache.py            # 💾 缓存服务
│   │   └── ...
│   ├── schemas/                  # 📋 数据验证模式
│   ├── utils/                    # 🛠️ 工具函数
│   │   ├── jwt_utils.py        # 🔐 JWT工具
│   │   ├── redis_client.py     # 🔴 Redis客户端
│   │   └── minio_client.py     # 📦 MinIO客户端
│   ├── config.py                # ⚙️ 配置管理
│   ├── dependencies.py          # 🔗 依赖注入
│   └── main.py                 # 🚀 应用入口点
├── tests/                        # 🧪 测试文件
│   ├── test_agent_integration.py  # 🤖 Agent集成测试
│   ├── test_health.py           # ❤️ 健康检查测试
│   └── conftest.py             # 🔧 测试配置
├── alembic/                      # 🗃️ 数据库迁移
├── docker-compose.yml           # 🐳 Docker编排
├── Dockerfile                   # 🐳 Docker镜像定义
├── pyproject.toml              # 📦 Python项目配置
├── requirements.txt            # 📋 依赖列表
└── README.md                   # 📖 项目文档
```

### 🔥 核心组件说明

| 组件 | 文件 | 核心功能 |
|------|------|----------|
| **🤖 Agent服务** | `services/agent_service.py` | TradeFlow Agent集成和管理 |
| **📡 SSE转换器** | `services/sse_converter.py` | 实时流式响应转换 |
| **🗂️ 会话管理** | `services/session_manager.py` | Redis分布式会话存储 |
| **⚡ 性能优化** | `services/agent_performance_optimizer.py` | Runner连接池和缓存优化 |
| **🚨 错误处理** | `services/agent_error_handler.py` | 智能重试和错误分类 |
| **🔐 认证系统** | `api/v1/auth.py` | JWT + OAuth认证授权 |

## ⚙️ 配置说明

### 核心配置项

在 `.env` 文件中配置以下关键参数：

```bash
# 🔧 应用基础配置
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=your-secret-key-here
LOG_LEVEL=INFO

# 🛢️ 数据库配置
POSTGRES_URL=postgresql+asyncpg://postgres:root@localhost:5432/mydb
MONGODB_URL=mongodb://localhost:27017
REDIS_URL=redis://:root@localhost:6379/0

# 📦 对象存储配置
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=root
MINIO_SECRET_KEY=rootpassword
MINIO_BUCKET_NAME=tradeflow-storage

# 🔐 JWT认证配置
JWT_SECRET_KEY=your-jwt-secret-key
ACCESS_TOKEN_EXPIRE_HOURS=4
REFRESH_TOKEN_EXPIRE_DAYS=30

# 🤖 Agent配置（重要！）
GOOGLE_ADK_API_KEY=your-google-adk-api-key
GOOGLE_ADK_MODEL=gemini-2.0-flash
AGENT_TIMEOUT_SECONDS=30
AGENT_MAX_RETRIES=3
AGENT_ENABLE_CACHE=true
AGENT_RUNNER_POOL_SIZE=5
AGENT_CACHE_TTL=3600

# 🌐 OAuth配置（可选）
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# 💳 支付配置（未来功能）
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
```

### Agent性能调优配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `AGENT_RUNNER_POOL_SIZE` | 5 | Agent Runner连接池大小 |
| `AGENT_TIMEOUT_SECONDS` | 30 | Agent查询超时时间 |
| `AGENT_CACHE_TTL` | 3600 | 缓存生存时间（秒） |
| `AGENT_ENABLE_CACHE` | true | 是否启用智能缓存 |
| `AGENT_MAX_RETRIES` | 3 | 失败重试次数 |

### 🔧 开发环境快速配置

```bash
# 复制配置模板
cp .env.example .env

# 最小化配置（本地开发）
echo "ENVIRONMENT=development" >> .env
echo "DEBUG=true" >> .env
echo "GOOGLE_ADK_API_KEY=your-api-key" >> .env

# 验证配置
poetry run python -c "from app.config import settings; print(f'环境: {settings.ENVIRONMENT}'); print(f'Agent配置: {settings.GOOGLE_ADK_API_KEY is not None}')"
```

## 🛠️ 开发指南

### 🎨 代码规范与质量

```bash
# 代码格式化和规范检查
poetry run black .              # Python代码格式化
poetry run isort .              # 导入语句排序
poetry run mypy app            # 静态类型检查
poetry run flake8 app          # 代码风格检查

# 一键执行所有检查
poetry run pre-commit run --all-files
```

### 🔧 开发工作流

**1. 环境准备**
```bash
# 安装开发依赖
poetry install --with dev,test

# 启动开发数据库
docker-compose -f docker-compose.dev.yml up -d postgres redis mongodb

# 数据库迁移
poetry run alembic upgrade head
```

**2. 开发服务器**
```bash
# 启动开发服务器（热重载）
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 验证服务状态
curl http://localhost:8000/api/v1/health
```

**3. Agent开发调试**
```bash
# 检查Agent配置
poetry run python -c "from app.config import settings; print('Agent配置:', settings.GOOGLE_ADK_API_KEY is not None)"

# 测试Agent连接
poetry run pytest tests/test_agent_integration.py::test_agent_connection -v

# 调试Agent查询
poetry run python -c "
from app.services.agent_service import AgentService
import asyncio

async def test():
    service = AgentService()
    result = await service.query('你好，TradeFlow', 'debug_session')
    print('Agent响应:', result)

asyncio.run(test())
"
```

### 📝 添加新功能的标准流程

**1. 创建API端点**
```bash
# 1. 创建API路由文件
touch app/api/v1/your_feature.py

# 2. 定义数据模式
touch app/schemas/your_feature.py

# 3. 实现业务逻辑
touch app/services/your_feature.py

# 4. 添加数据模型（如需要）
touch app/models/your_feature.py

# 5. 编写测试
touch tests/test_your_feature.py
```

**2. Agent功能扩展**
```bash
# 如需要扩展Agent功能，在../agent/TradeFlowAgent/中开发
cd ../agent/TradeFlowAgent/

# 添加新的工具或Agent
touch trade_flow/tools/your_new_tool.py
touch trade_flow/agents/your_new_agent.py

# 测试新功能
pytest test/test_your_feature.py -v
```

**3. 集成到后端**
```python
# app/services/agent_service.py中集成新功能
class AgentService:
    async def handle_new_feature(self, query: str, session_id: str):
        # 调用TradeFlow Agent的新功能
        pass
```

### 🗃️ 数据库管理

```bash
# 数据库迁移管理
poetry run alembic revision --autogenerate -m "添加新表或字段"
poetry run alembic upgrade head                    # 应用最新迁移
poetry run alembic downgrade -1                    # 回滚一个版本
poetry run alembic history                         # 查看迁移历史

# 数据库连接测试
poetry run python -c "from app.core.database import test_connection; import asyncio; asyncio.run(test_connection())"

# MongoDB集合管理
poetry run python -c "
from app.core.database import mongodb
import asyncio

async def check_mongo():
    collections = await mongodb.list_collection_names()
    print('MongoDB集合:', collections)

asyncio.run(check_mongo())
"

# Redis缓存管理
redis-cli -h localhost -p 6379 -a root INFO keyspace  # 查看键统计
redis-cli -h localhost -p 6379 -a root KEYS "*"       # 查看所有键
```

## 📊 监控与运维

### 📝 结构化日志系统

系统采用结构化日志记录，包含以下维度：

```python
# 日志示例输出
{
  "timestamp": "2025-01-09T10:30:45.123Z",
  "level": "INFO",
  "request_id": "req_abc123",
  "user_id": "user_456",
  "endpoint": "/api/v1/agent/query",
  "method": "POST",
  "status_code": 200,
  "response_time_ms": 1250,
  "agent_query_time_ms": 980,
  "cache_hit": true,
  "message": "Agent query completed successfully"
}
```

**日志类别**：
- **🔍 请求追踪**: 每个API请求的完整生命周期
- **⚡ 性能指标**: 响应时间、CPU使用、内存使用
- **🤖 Agent事件**: Agent查询、缓存命中、错误重试
- **🚨 错误记录**: 详细的错误堆栈和上下文信息
- **📈 业务事件**: 用户行为、会话管理、功能使用统计

### 📈 性能监控指标

| 指标类别 | 关键指标 | 监控阈值 |
|----------|----------|----------|
| **API性能** | 平均响应时间 | < 500ms |
| **Agent性能** | Agent查询时间 | < 2000ms |
| **缓存效率** | 缓存命中率 | > 80% |
| **错误率** | 4xx/5xx错误率 | < 1% |
| **并发性** | 活跃连接数 | < 1000 |

```bash
# 实时性能监控
curl http://localhost:8000/api/v1/health/detailed | jq '.performance'

# 输出示例
{
  "avg_response_time_ms": 245,
  "agent_avg_query_time_ms": 1200,
  "cache_hit_rate": 0.87,
  "active_connections": 12,
  "error_rate_5min": 0.002
}
```

### ❤️ 健康检查体系

支持多层级健康检查，适配Kubernetes生产环境：

```bash
# 基础存活检查（快速）
curl http://localhost:8000/api/v1/health/liveness
# 返回: {"status": "alive", "timestamp": "..."}

# 就绪性检查（包含依赖）
curl http://localhost:8000/api/v1/health/readiness  
# 检查: 数据库连接、Redis连接、Agent Runner状态

# 详细组件检查
curl http://localhost:8000/api/v1/health/detailed | jq
```

**健康检查输出示例**：
```json
{
  "status": "healthy",
  "timestamp": "2025-01-09T10:30:45.123Z",
  "checks": {
    "database": {
      "status": "healthy",
      "response_time_ms": 15,
      "connection_pool": {"active": 5, "idle": 10}
    },
    "redis": {
      "status": "healthy", 
      "response_time_ms": 2,
      "memory_usage_mb": 45.2
    },
    "agent_runner": {
      "status": "healthy",
      "pool_size": 5,
      "active_runners": 2,
      "avg_query_time_ms": 1200
    },
    "mongodb": {
      "status": "healthy",
      "response_time_ms": 8,
      "collections_count": 4
    }
  },
  "system_info": {
    "uptime_seconds": 86400,
    "memory_usage_mb": 256.7,
    "cpu_usage_percent": 12.5
  }
}
```

### 🚨 故障排除工具

```bash
# Agent服务诊断
curl http://localhost:8000/api/v1/health/detailed | jq '.checks.agent_runner'

# 查看最近错误
docker-compose logs --tail=50 backend | grep ERROR

# Redis连接诊断
redis-cli -h localhost -p 6379 -a root ping

# 数据库连接诊断
poetry run python -c "from app.core.database import test_connection; import asyncio; asyncio.run(test_connection())"

# 清理缓存（如遇缓存问题）
redis-cli -h localhost -p 6379 -a root FLUSHDB
```

## 🛡️ 安全与部署注意事项

### ⚠️ 生产环境安全清单

**🔐 认证与授权**
- [ ] 修改所有默认密码和密钥
- [ ] 启用强密码策略（最小8位，包含特殊字符）
- [ ] 配置JWT密钥轮换机制
- [ ] 启用OAuth 2.0/OIDC集成
- [ ] 配置API速率限制和DDoS防护

**🌐 网络安全**
- [ ] 启用HTTPS/TLS 1.3加密
- [ ] 配置严格的CORS策略
- [ ] 设置适当的CSP（Content Security Policy）
- [ ] 配置防火墙规则，仅开放必要端口
- [ ] 启用WAF（Web Application Firewall）

**🗄️ 数据安全**
- [ ] 数据库连接使用SSL/TLS加密
- [ ] 敏感数据字段加密存储
- [ ] 配置数据备份和恢复策略
- [ ] 启用数据库审计日志
- [ ] 设置Redis AUTH和TLS加密

**📊 监控与审计**
- [ ] 配置集中化日志聚合（ELK/Loki）
- [ ] 启用安全事件监控和告警
- [ ] 配置性能监控（Prometheus/Grafana）
- [ ] 设置健康检查和自动恢复
- [ ] 启用API访问审计日志

### 🐳 生产环境部署

```bash
# 1. 生产环境配置
cp .env.example .env.prod
vim .env.prod  # 配置生产环境参数

# 2. 构建生产镜像
docker-compose -f docker-compose.prod.yml build

# 3. 启动生产服务
docker-compose -f docker-compose.prod.yml up -d

# 4. 验证服务状态
curl https://your-domain.com/api/v1/health

# 5. 配置反向代理（Nginx示例）
# upstream tradeflow_backend {
#     server 127.0.0.1:8000;
# }
# server {
#     listen 443 ssl;
#     server_name your-domain.com;
#     
#     location /api/ {
#         proxy_pass http://tradeflow_backend;
#         proxy_set_header Host $host;
#         proxy_set_header X-Real-IP $remote_addr;
#     }
# }
```

### 🔍 安全配置验证

```bash
# SSL/TLS配置检查
curl -I https://your-domain.com/api/v1/health

# CORS策略验证
curl -H "Origin: https://malicious-site.com" \
     https://your-domain.com/api/v1/health

# 速率限制测试
for i in {1..100}; do curl https://your-domain.com/api/v1/health; done

# JWT token安全检查
curl -H "Authorization: Bearer invalid-token" \
     https://your-domain.com/api/v1/agent/query
```

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交代码变更
4. 添加相应测试
5. 确保所有测试通过
6. 提交 Pull Request

## 许可证

MIT License

## 支持

如有问题或建议，请提交 Issue 或联系开发团队。