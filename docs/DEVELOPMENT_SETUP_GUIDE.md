# TradeFlow 开发环境配置指南

> **完整的TradeFlow开发环境搭建指南**  
> 从零开始搭建包括后端API、AI Agent、前端界面的完整开发环境

## 📋 系统要求

### 基础环境要求
- **操作系统**: macOS 10.15+, Ubuntu 18.04+, Windows 10+ (推荐WSL2)
- **Python**: 3.11+ (推荐3.11.5)
- **Node.js**: 18+ (推荐18.17.0)
- **Git**: 2.25+
- **Docker**: 20.10+ 和 Docker Compose 2.0+

### 硬件推荐
- **内存**: 16GB+ (Agent运行需要较多内存)
- **存储**: 50GB+ 可用空间
- **网络**: 稳定的互联网连接 (Agent需要访问外部API)

## 🚀 快速开始（15分钟搭建）

### 1. 克隆项目
```bash
git clone <repository-url>
cd TradeFlowProduct
```

### 2. 一键启动基础服务
```bash
# 启动数据库和缓存服务
cd src/backend
docker-compose -f docker-compose.dev.yml up -d postgres mongodb redis minio

# 验证服务状态
docker-compose ps
```

### 3. 配置后端环境
```bash
cd src/backend

# 安装Python依赖管理工具
pip install poetry

# 安装项目依赖
poetry install

# 配置环境变量
cp .env.example .env
vim .env  # 配置必要的API密钥

# 数据库初始化
poetry run alembic upgrade head

# 启动后端服务
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 验证核心功能
```bash
# 健康检查
curl http://localhost:8000/api/v1/health

# Agent功能测试
curl -X POST "http://localhost:8000/api/v1/agent/query" \
  -H "Content-Type: application/json" \
  -d '{"message": "你好，请介绍TradeFlow的功能", "session_id": "test"}'
```

### 5. 启动前端（可选）
```bash
cd src/frontend
npm install
npm run dev
# 访问 http://localhost:3000
```

## 🔧 详细配置步骤

### 步骤一：基础环境准备

**1. Python环境配置**
```bash
# 安装Python 3.11 (推荐使用pyenv)
curl https://pyenv.run | bash
pyenv install 3.11.5
pyenv global 3.11.5

# 验证Python版本
python --version  # 应显示 Python 3.11.5
```

**2. Node.js环境配置**
```bash
# 安装Node.js (推荐使用nvm)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18.17.0
nvm use 18.17.0

# 验证Node.js版本
node --version  # 应显示 v18.17.0+
npm --version   # 应显示 9.6.7+
```

**3. Docker环境配置**
```bash
# macOS用户安装Docker Desktop
# https://docs.docker.com/desktop/install/mac-install/

# Ubuntu用户安装Docker
sudo apt update
sudo apt install docker.io docker-compose-plugin

# 验证Docker安装
docker --version
docker compose version
```

### 步骤二：数据库服务配置

**1. 启动基础数据服务**
```bash
cd src/backend

# 创建Docker网络
docker network create tradeflow-network

# 启动数据库服务
docker-compose -f docker-compose.dev.yml up -d postgres mongodb redis minio

# 等待服务启动完成
sleep 30

# 验证服务连接
docker-compose exec postgres pg_isready -U postgres
docker-compose exec redis redis-cli ping
docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')"
```

**2. 数据库初始化**
```bash
# PostgreSQL数据库创建
docker-compose exec postgres createdb -U postgres mydb
docker-compose exec postgres createdb -U postgres mydb_test

# MongoDB数据库初始化
docker-compose exec mongodb mongosh --eval "
  use tradeflow;
  db.createCollection('test');
  use tradeflow_test;
  db.createCollection('test');
"

# Redis连接测试
docker-compose exec redis redis-cli -a root set test-key "test-value"
docker-compose exec redis redis-cli -a root get test-key
```

**3. MinIO对象存储配置**
```bash
# 访问MinIO管理界面
open http://localhost:9001
# 用户名: root, 密码: rootpassword

# 创建存储桶
docker-compose exec minio mc alias set local http://localhost:9000 root rootpassword
docker-compose exec minio mc mb local/tradeflow-storage
```

### 步骤三：后端服务配置

**1. Python环境和依赖安装**
```bash
cd src/backend

# 安装Poetry包管理工具
curl -sSL https://install.python-poetry.org | python3 -

# 配置Poetry
poetry config virtualenvs.create true
poetry config virtualenvs.in-project true

# 安装项目依赖
poetry install --with dev,test

# 激活虚拟环境
poetry shell
```

**2. 环境变量配置**
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量
cat > .env << EOF
# 应用基础配置
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=$(openssl rand -base64 32)
LOG_LEVEL=INFO

# 数据库配置
POSTGRES_URL=postgresql+asyncpg://postgres:root@localhost:5432/mydb
MONGODB_URL=mongodb://localhost:27017
REDIS_URL=redis://:root@localhost:6379/0

# MinIO配置
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=root
MINIO_SECRET_KEY=rootpassword

# JWT配置
JWT_SECRET_KEY=$(openssl rand -base64 32)
ACCESS_TOKEN_EXPIRE_HOURS=4

# Agent配置（重要！请配置有效的API密钥）
GOOGLE_ADK_API_KEY=your-google-adk-api-key-here
GOOGLE_ADK_MODEL=gemini-2.0-flash
AGENT_TIMEOUT_SECONDS=30
AGENT_MAX_RETRIES=3
AGENT_ENABLE_CACHE=true
AGENT_RUNNER_POOL_SIZE=5

# 搜索API配置
JINA_API_KEY=your-jina-api-key-here

# 贸易数据API配置（可选）
TENDATA_API_KEY=your-tendata-api-key-here
EOF

# 验证配置
poetry run python -c "
from app.config import settings
print(f'环境: {settings.ENVIRONMENT}')
print(f'数据库: {settings.POSTGRES_URL}')
print(f'Agent配置: {settings.GOOGLE_ADK_API_KEY is not None}')
"
```

**3. 数据库迁移**
```bash
# 运行数据库迁移
poetry run alembic upgrade head

# 验证数据库表创建
poetry run python -c "
import asyncio
from app.core.database import database
async def check_tables():
    query = 'SELECT tablename FROM pg_tables WHERE schemaname = '\''public'\'''
    async with database.pool.acquire() as conn:
        tables = await conn.fetch(query)
        print('数据库表:', [t['tablename'] for t in tables])
asyncio.run(check_tables())
"
```

**4. 启动后端服务**
```bash
# 方式1：开发模式启动（推荐）
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level info

# 方式2：生产模式启动
poetry run gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# 方式3：Docker方式启动
docker-compose up -d backend
```

### 步骤四：Agent配置与测试

**1. TradeFlow Agent环境配置**
```bash
cd src/agent/TradeFlowAgent

# 安装Agent依赖
pip install -r requirements.txt

# 配置Agent环境变量
cat > .env << EOF
# AI模型配置
MODEL=claude-sonnet-4-20250514
API_KEY=your-anthropic-api-key-here

# 或者使用Gemini
# MODEL=gemini-2.0-flash  
# API_KEY=your-google-api-key-here

# 必需的搜索API
JINA_API_KEY=your-jina-api-key-here

# 可选的贸易数据API
TENDATA_API_KEY=your-tendata-api-key-here
EOF
```

**2. Agent独立测试**
```bash
# 启动Agent Web界面
adk web
# 访问 http://localhost:8000 测试Agent功能

# 命令行测试
python test/test_phase8_product_supplier_discovery.py

# 运行核心功能测试
pytest test/ -v -k "test_supplier_discovery or test_trade_query"
```

**3. Agent与后端集成测试**
```bash
cd ../../backend

# 测试Agent集成
poetry run pytest tests/test_agent_integration.py -v

# 手动测试Agent查询
curl -X POST "http://localhost:8000/api/v1/agent/query" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "分析苹果公司的主要供应商",
    "session_id": "integration_test"
  }'
```

### 步骤五：前端开发环境配置

**1. 前端依赖安装**
```bash
cd src/frontend

# 安装npm依赖
npm install

# 或者使用yarn
yarn install
```

**2. 前端环境配置**
```bash
# 创建前端环境变量文件
cat > .env.local << EOF
VITE_API_BASE_URL=http://localhost:8000
VITE_ENVIRONMENT=development
VITE_ENABLE_MOCK=false
EOF
```

**3. 启动前端开发服务器**
```bash
# 启动开发服务器
npm run dev

# 或者使用yarn
yarn dev

# 访问前端应用
open http://localhost:3000
```

## 🧪 开发环境验证

### 全栈功能测试

**1. 后端API测试**
```bash
# 健康检查
curl http://localhost:8000/api/v1/health

# 详细健康检查
curl http://localhost:8000/api/v1/health/detailed | jq

# 用户认证测试
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo",
    "password": "demo123"
  }'
```

**2. Agent功能测试**
```bash
# 基础Agent查询
curl -X POST "http://localhost:8000/api/v1/agent/query" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你好，请介绍TradeFlow的核心功能",
    "session_id": "dev_test"
  }'

# 供应商分析测试
curl -X POST "http://localhost:8000/api/v1/agent/query" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "分析富士康的主要产品线和客户",
    "session_id": "supplier_test"
  }'
```

**3. 前端界面测试**
```bash
# 访问前端应用
open http://localhost:3000

# 测试功能：
# 1. 用户注册/登录
# 2. 创建聊天会话
# 3. 发送Agent查询
# 4. 查看响应结果
# 5. 文件上传下载（如适用）
```

### 性能基准测试

**1. API性能测试**
```bash
# 安装压测工具
npm install -g clinic autocannon

# API响应时间测试
autocannon -c 10 -d 30 http://localhost:8000/api/v1/health

# Agent查询性能测试（注意：会消耗API配额）
autocannon -c 2 -d 10 -m POST \
  -H "Content-Type: application/json" \
  -b '{"message": "简单测试", "session_id": "perf_test"}' \
  http://localhost:8000/api/v1/agent/query
```

**2. 数据库连接测试**
```bash
# PostgreSQL连接池测试
poetry run python -c "
import asyncio
from app.core.database import database
async def test_connections():
    tasks = []
    for i in range(20):
        task = database.fetch_one('SELECT 1 as test')
        tasks.append(task)
    results = await asyncio.gather(*tasks)
    print(f'成功执行 {len(results)} 个并发数据库查询')
asyncio.run(test_connections())
"
```

**3. Redis缓存性能测试**
```bash
# Redis性能基准测试
docker-compose exec redis redis-benchmark -h localhost -p 6379 -a root -c 50 -n 10000
```

## 🛠️ 开发工具配置

### VS Code开发环境

**1. 推荐的VS Code插件**
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.black-formatter", 
    "ms-python.isort",
    "ms-python.mypy-type-checker",
    "bradlc.vscode-tailwindcss",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-typescript-next",
    "formulahendry.auto-rename-tag",
    "christian-kohler.path-intellisense"
  ]
}
```

**2. VS Code工作区配置**
```json
{
  "folders": [
    {"name": "后端", "path": "./src/backend"},
    {"name": "前端", "path": "./src/frontend"}, 
    {"name": "Agent", "path": "./src/agent/TradeFlowAgent"},
    {"name": "文档", "path": "./docs"}
  ],
  "settings": {
    "python.defaultInterpreterPath": "./src/backend/.venv/bin/python",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.mypyEnabled": true,
    "typescript.preferences.importModuleSpecifier": "relative"
  }
}
```

### Git开发工作流

**1. Git hooks配置**
```bash
cd TradeFlowProduct

# 安装pre-commit
pip install pre-commit

# 配置pre-commit hooks
cat > .pre-commit-config.yaml << EOF
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
        files: ^src/backend/

  - repo: https://github.com/pycqa/isort
    rev: 5.10.1
    hooks:
      - id: isort
        files: ^src/backend/

  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v2.6.2
    hooks:
      - id: prettier
        files: ^src/frontend/
EOF

# 安装hooks
pre-commit install
```

**2. 开发分支策略**
```bash
# 创建功能分支
git checkout -b feature/agent-optimization

# 提交代码变更
git add .
git commit -m "优化Agent查询性能和缓存策略"

# 推送到远程分支
git push origin feature/agent-optimization

# 创建Pull Request
gh pr create --title "Agent性能优化" --body "详细描述变更内容"
```

## 🐛 常见问题解决

### 环境配置问题

**问题1：Python依赖安装失败**
```bash
# 解决方案：更新pip和setuptools
pip install --upgrade pip setuptools wheel
poetry install

# 如果仍然失败，尝试清理缓存
poetry cache clear --all .
poetry install
```

**问题2：Docker服务启动失败**
```bash
# 检查Docker状态
docker info

# 清理Docker资源
docker system prune -a

# 重建服务
docker-compose down
docker-compose up -d --build
```

**问题3：数据库连接失败**
```bash
# 检查数据库服务状态
docker-compose ps postgres

# 查看数据库日志
docker-compose logs postgres

# 重启数据库服务
docker-compose restart postgres

# 验证连接参数
psql "postgresql://postgres:root@localhost:5432/mydb" -c "SELECT version();"
```

### Agent配置问题

**问题1：Agent查询超时或失败**
```bash
# 检查Agent配置
poetry run python -c "
from app.config import settings
print('Google ADK API Key配置:', settings.GOOGLE_ADK_API_KEY is not None)
print('Agent超时设置:', settings.AGENT_TIMEOUT_SECONDS)
"

# 测试Agent连接
cd src/agent/TradeFlowAgent
python -c "
from trade_flow.main_agent import TradeFlowAgent
agent = TradeFlowAgent()
print('Agent初始化成功')
"
```

**问题2：搜索功能不可用**
```bash
# 检查Jina API配置
curl -H "Authorization: Bearer $JINA_API_KEY" \
  https://api.jina.ai/v1/search \
  -d '{"q": "test query"}' \
  -H "Content-Type: application/json"

# 如果没有Jina API，可以临时禁用搜索功能
export JINA_API_KEY=""  # 留空使用备用搜索方案
```

### 前端开发问题

**问题1：npm依赖安装失败**
```bash
# 清理npm缓存
npm cache clean --force

# 删除node_modules重新安装
rm -rf node_modules package-lock.json
npm install

# 或者使用yarn
rm -rf node_modules yarn.lock
yarn install
```

**问题2：前端无法连接后端API**
```bash
# 检查后端服务状态
curl http://localhost:8000/api/v1/health

# 检查CORS配置
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     http://localhost:8000/api/v1/agent/query

# 更新前端API配置
echo "VITE_API_BASE_URL=http://localhost:8000" > src/frontend/.env.local
```

## 🚀 生产部署准备

### 生产环境检查清单

**1. 安全配置检查**
```bash
# 生成强密码和密钥
export SECRET_KEY=$(openssl rand -base64 32)
export JWT_SECRET_KEY=$(openssl rand -base64 32)
export DATABASE_PASSWORD=$(openssl rand -base64 16)

# 检查环境变量配置
poetry run python -c "
from app.config import settings
assert settings.SECRET_KEY != 'your-secret-key', '请配置生产环境密钥'
assert not settings.DEBUG, '生产环境应禁用DEBUG'
assert settings.ENVIRONMENT == 'production', '请设置生产环境标识'
print('✅ 生产环境配置检查通过')
"
```

**2. 性能优化配置**
```bash
# 数据库连接池优化
export POSTGRES_POOL_SIZE=20
export POSTGRES_MAX_OVERFLOW=30

# Agent性能优化
export AGENT_RUNNER_POOL_SIZE=10
export AGENT_CACHE_TTL=7200
export AGENT_ENABLE_CACHE=true

# Redis内存优化
docker-compose exec redis redis-cli CONFIG SET maxmemory 1gb
docker-compose exec redis redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

**3. 监控和日志配置**
```bash
# 配置结构化日志
export LOG_LEVEL=INFO
export LOG_FORMAT=json

# 配置监控
export ENABLE_METRICS=true
export SENTRY_DSN=your-sentry-dsn-here

# 健康检查配置
export HEALTH_CHECK_INTERVAL=30
```

### Docker生产部署

```bash
# 构建生产镜像
docker-compose -f docker-compose.prod.yml build

# 启动生产服务
docker-compose -f docker-compose.prod.yml up -d

# 验证生产部署
curl https://your-domain.com/api/v1/health
```

---

## 📚 相关资源

### 官方文档
- **后端API文档**: [src/backend/README.md](../src/backend/README.md)
- **Agent使用指南**: [docs/AGENT_USAGE_GUIDE.md](AGENT_USAGE_GUIDE.md)
- **API规范文档**: [docs/api/](api/)

### 开发工具
- **API文档界面**: http://localhost:8000/api/v1/docs
- **Agent独立界面**: cd src/agent/TradeFlowAgent && adk web
- **数据库管理**: 推荐使用 pgAdmin 或 DBeaver

### 社区支持
- **GitHub Issues**: 报告问题和获取帮助
- **GitHub Discussions**: 技术讨论和经验分享
- **开发者文档**: 详细的API和集成文档

---

**TradeFlow开发环境配置指南** - 助力高效开发，构建强大的B2B贸易智能助手！ 🚀

*最后更新：2025-01-09*