# TradeFlow Backend API

TradeFlow B2B贸易智能助手后端API服务，基于FastAPI构建的现代化、高性能的Web API。

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

## 功能特性

- ✅ 异步API设计，高性能处理
- ✅ 结构化日志记录，便于调试和监控
- ✅ 全面的错误处理和异常管理
- ✅ 性能监控和请求追踪
- ✅ 速率限制和安全防护
- ✅ 健康检查和服务监控
- ✅ 数据库迁移管理
- ✅ 完整的测试覆盖
- ✅ Docker容器化部署

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

## API文档

启动服务后，可以通过以下地址访问API文档：

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

## 健康检查

- **基础检查**: `GET /api/v1/health`
- **详细检查**: `GET /api/v1/health/detailed`
- **存活性检查**: `GET /api/v1/health/liveness`
- **就绪性检查**: `GET /api/v1/health/readiness`

## 测试

### 运行测试

```bash
# 运行所有测试
poetry run pytest

# 运行特定测试文件
poetry run pytest tests/test_health.py

# 运行带覆盖率的测试
poetry run pytest --cov=app --cov-report=html

# 运行特定标记的测试
poetry run pytest -m unit
poetry run pytest -m integration
```

### 测试分类

- `unit`: 单元测试
- `integration`: 集成测试
- `slow`: 慢测试

## 项目结构

```
src/backend/
├── app/                    # 应用代码
│   ├── api/               # API路由
│   │   └── v1/           # API版本1
│   ├── core/              # 核心模块
│   │   ├── database.py   # 数据库配置
│   │   ├── logging.py    # 日志配置
│   │   └── exceptions.py # 异常定义
│   ├── middleware/        # 中间件
│   ├── models/           # 数据模型
│   ├── schemas/          # Pydantic模式
│   ├── services/         # 业务逻辑
│   ├── utils/            # 工具函数
│   ├── config.py         # 配置管理
│   ├── dependencies.py   # 依赖注入
│   └── main.py          # 应用入口
├── tests/                 # 测试文件
├── alembic/              # 数据库迁移
├── docker-compose.yml    # Docker编排
├── Dockerfile           # Docker镜像
├── pyproject.toml       # 项目配置
└── README.md           # 项目文档
```

## 配置说明

主要配置项在 `.env` 文件中：

```bash
# 应用配置
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=your-secret-key

# 数据库配置
POSTGRES_URL=postgresql+asyncpg://postgres:root@localhost:5432/mydb
MONGODB_URL=mongodb://localhost:27017
REDIS_URL=redis://:root@localhost:6379/0

# MinIO配置
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=root
MINIO_SECRET_KEY=rootpassword
```

## 开发指南

### 代码规范

- 使用 `black` 进行代码格式化
- 使用 `isort` 进行导入排序
- 使用 `mypy` 进行类型检查
- 使用 `flake8` 进行代码检查

```bash
# 格式化代码
poetry run black .
poetry run isort .

# 类型检查
poetry run mypy app

# 代码检查
poetry run flake8 app
```

### 添加新的API端点

1. 在 `app/api/v1/` 下创建新的路由文件
2. 在 `app/schemas/` 下定义请求/响应模式
3. 在 `app/services/` 下实现业务逻辑
4. 在 `app/models/` 下定义数据模型（如需要）
5. 添加相应的测试文件

### 数据库迁移

```bash
# 创建新迁移
poetry run alembic revision --autogenerate -m "描述迁移内容"

# 应用迁移
poetry run alembic upgrade head

# 回滚迁移
poetry run alembic downgrade -1
```

## 监控和日志

### 日志

应用使用结构化日志记录，支持：

- 请求ID追踪
- 性能指标记录
- 错误详细信息
- 业务事件记录

### 性能监控

- 请求响应时间
- CPU使用时间
- 慢请求告警
- 速率限制

### 健康检查

支持Kubernetes风格的健康检查：

- **Liveness Probe**: 检查应用是否存活
- **Readiness Probe**: 检查应用是否就绪
- **详细检查**: 检查所有依赖服务状态

## 安全注意事项

⚠️ **开发环境配置**

当前配置适用于开发环境，生产环境部署时请注意：

1. 修改所有默认密码
2. 启用HTTPS/TLS加密
3. 配置防火墙规则
4. 设置适当的CORS策略
5. 启用速率限制
6. 配置日志聚合和监控

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