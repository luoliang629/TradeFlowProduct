# TradeFlow API 接口文档中心

## 📋 项目概述

TradeFlow是一款面向全球的，基于对话式AI Agent的全球B2B贸易智能助手。本文档中心提供完整的API接口文档、开发指南和集成说明，帮助开发者快速理解和使用TradeFlow API。

### 核心功能
- **智能对话**: 基于Google ADK的AI Agent，支持买家开发和供应商匹配
- **OAuth认证**: 支持Google和GitHub OAuth 2.0登录
- **文件管理**: 文件上传、预览、管理和分享
- **实时通信**: 基于SSE的流式对话体验
- **支付集成**: 集成Stripe支付系统的订阅管理

### 技术架构
- **前端**: React 18 + TypeScript
- **后端**: FastAPI + Python
- **数据库**: PostgreSQL + MongoDB + Redis
- **AI框架**: Google ADK (Agent Development Kit)
- **部署**: Cloud Run (Google Cloud Platform)

## 📚 API文档导航

### 🔧 设计规范
| 文档 | 描述 | 更新时间 |
|------|------|----------|
| [API设计规范](../../docs/api/api_design_guidelines.md) | RESTful设计原则、命名规范、错误处理等 | 2025-01-07 |
| [API安全设计](../../docs/api/api_security_design.md) | 认证授权、数据加密、安全防护策略 | 2025-01-07 |

### 📖 接口规范
| 文档 | 描述 | 更新时间 |
|------|------|----------|
| [OpenAPI规范](../../docs/api/openapi_specification.yaml) | 完整的API接口定义和数据模型 | 2025-01-07 |
| [Mock服务配置](../../docs/api/mock_service_config.md) | Mock服务设置和测试数据 | 2025-01-07 |
| [契约测试指南](../../docs/api/contract_testing_guide.md) | API契约测试实施指南 | 2025-01-07 |

### 🛠️ 开发文档
| 文档 | 描述 | 状态 |
|------|------|------|
| 前端开发指南 | React应用开发和集成指南 | 计划中 |
| 后端开发指南 | FastAPI服务开发和部署 | 计划中 |
| AI Agent开发 | Google ADK集成和Agent开发 | 计划中 |

## 🚀 快速开始指南

### 1. 环境准备

#### 前端开发环境
```bash
# 克隆项目
git clone https://github.com/your-org/TradeFlowProduct.git
cd TradeFlowProduct/src/frontend

# 安装依赖
npm install

# 启动开发服务器
npm start
```

#### 后端开发环境
```bash
# 进入后端目录
cd TradeFlowProduct/src/backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 配置环境变量

创建 `.env` 文件并配置必要的环境变量：

```bash
# 数据库配置
DATABASE_URL=postgresql://user:password@localhost:5432/tradeflow
MONGODB_URL=mongodb://localhost:27017/tradeflow
REDIS_URL=redis://localhost:6379/0

# OAuth配置
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret

# JWT配置
JWT_SECRET_KEY=your_jwt_secret_key
JWT_ALGORITHM=HS256

# Google ADK配置
GOOGLE_ADK_API_KEY=your_adk_api_key
GOOGLE_ADK_PROJECT_ID=your_project_id

# Stripe配置
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# 其他配置
APP_ENV=development
DEBUG=true
LOG_LEVEL=debug
```

### 3. API认证

#### 获取访问令牌

```javascript
// 前端OAuth登录
const loginWithGoogle = async () => {
  window.location.href = '/api/v1/auth/oauth/google?redirect_uri=' + 
    encodeURIComponent(window.location.origin + '/auth/callback');
};

// 处理OAuth回调
const handleAuthCallback = async (code, state) => {
  const response = await fetch('/api/v1/auth/oauth/google/callback', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });
  
  const { access_token, refresh_token } = await response.json();
  
  // 存储令牌
  localStorage.setItem('access_token', access_token);
  localStorage.setItem('refresh_token', refresh_token);
};
```

#### 使用访问令牌

```javascript
// API请求示例
const fetchUserProfile = async () => {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch('/api/v1/auth/me', {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });
  
  return await response.json();
};
```

### 4. 基础API调用示例

#### 发起AI对话

```javascript
const startChat = async (message, agentType = 'buyer') => {
  const response = await fetch('/api/v1/chat', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message: message,
      agent_type: agentType,
      session_id: sessionId
    }),
  });
  
  return await response.json();
};
```

#### SSE流式对话

```javascript
const connectToSSE = (token, sessionId) => {
  const eventSource = new EventSource(
    `/api/v1/chat/stream?token=${token}&session_id=${sessionId}`
  );
  
  eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('收到消息:', data);
  };
  
  eventSource.onerror = (error) => {
    console.error('SSE连接错误:', error);
  };
  
  return eventSource;
};
```

#### 文件上传

```javascript
const uploadFile = async (file, sessionId) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('session_id', sessionId);
  
  const response = await fetch('/api/v1/files', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
    },
    body: formData,
  });
  
  return await response.json();
};
```

## 🔧 开发工具推荐

### API文档和测试工具

#### Swagger UI
访问在线API文档：
- **开发环境**: http://localhost:8000/docs
- **测试环境**: https://staging-api.tradeflow.com/docs
- **生产环境**: https://api.tradeflow.com/docs

#### Postman集合
我们提供了完整的Postman集合用于API测试：

```bash
# 导入Postman集合
curl -o tradeflow-api.postman_collection.json \
  https://api.tradeflow.com/postman/collection.json
```

#### cURL示例

```bash
# 健康检查
curl -X GET "https://api.tradeflow.com/api/v1/health"

# 获取用户信息
curl -X GET "https://api.tradeflow.com/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 发起对话
curl -X POST "https://api.tradeflow.com/api/v1/chat" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "我想找一些电子产品的买家",
    "agent_type": "buyer"
  }'
```

### 开发调试工具

#### 前端调试
- **React DevTools**: 浏览器扩展，用于调试React组件
- **Redux DevTools**: 状态管理调试
- **Network Panel**: 浏览器开发者工具，监控API请求

#### 后端调试
- **FastAPI自动文档**: 访问 `/docs` 和 `/redoc` 端点
- **日志查看**: `tail -f logs/app.log`
- **数据库客户端**: pgAdmin, MongoDB Compass, Redis Insight

#### Mock服务
使用Mock服务进行前端独立开发：

```bash
# 启动Mock服务
npm install -g json-server
json-server --watch mock-data.json --port 3001
```

## 📊 API监控和分析

### 性能监控

#### 关键指标
- **响应时间**: P95 < 200ms, P99 < 500ms
- **错误率**: < 0.1%
- **可用性**: > 99.9%
- **QPS**: 支持1000+ QPS

#### 监控工具
- **Prometheus**: 指标收集
- **Grafana**: 指标可视化
- **ELK Stack**: 日志分析
- **Sentry**: 错误追踪

### 使用分析

#### 统计数据
```bash
# API调用统计
curl -X GET "https://api.tradeflow.com/api/v1/admin/stats" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

#### 用户行为分析
- **对话频率**: 用户AI对话使用情况
- **功能使用**: 各功能模块使用统计
- **文件上传**: 文件类型和大小分析

## ❓ 常见问题解答

### 认证相关

**Q: Token过期了怎么办？**
A: 使用refresh_token自动刷新access_token：

```javascript
const refreshToken = async () => {
  const refreshToken = localStorage.getItem('refresh_token');
  
  const response = await fetch('/api/v1/auth/refresh', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      refresh_token: refreshToken,
    }),
  });
  
  const { access_token } = await response.json();
  localStorage.setItem('access_token', access_token);
};
```

**Q: 如何处理OAuth登录失败？**
A: 检查以下几点：
1. Client ID和Secret配置正确
2. 回调URL在OAuth应用中正确配置
3. 网络连接正常
4. 检查浏览器控制台错误信息

### API调用相关

**Q: 为什么收到429错误？**
A: API调用频率超过限制，请：
1. 检查当前用户的限流配额
2. 实现指数退避重试机制
3. 考虑升级到更高级别的订阅计划

**Q: SSE连接经常断开怎么办？**
A: 实现重连机制：

```javascript
const connectWithRetry = (token, sessionId, maxRetries = 3) => {
  let retryCount = 0;
  
  const connect = () => {
    const eventSource = new EventSource(
      `/api/v1/chat/stream?token=${token}&session_id=${sessionId}`
    );
    
    eventSource.onerror = () => {
      if (retryCount < maxRetries) {
        retryCount++;
        setTimeout(connect, 1000 * retryCount); // 指数退避
      }
    };
    
    return eventSource;
  };
  
  return connect();
};
```

### 文件上传相关

**Q: 大文件上传失败怎么办？**
A: 建议实现分块上传：

```javascript
const uploadLargeFile = async (file, chunkSize = 1024 * 1024) => {
  const chunks = Math.ceil(file.size / chunkSize);
  
  for (let i = 0; i < chunks; i++) {
    const start = i * chunkSize;
    const end = Math.min(start + chunkSize, file.size);
    const chunk = file.slice(start, end);
    
    await uploadChunk(chunk, i, chunks);
  }
};
```

### 错误处理

**Q: 如何统一处理API错误？**
A: 建议封装错误处理函数：

```javascript
const apiRequest = async (url, options = {}) => {
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Authorization': `Bearer ${getAccessToken()}`,
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new APIError(errorData.error.code, errorData.error.message);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API请求失败:', error);
    throw error;
  }
};
```

## 📞 技术支持

### 联系方式
- **技术文档**: https://docs.tradeflow.com
- **API状态页**: https://status.tradeflow.com
- **GitHub Issues**: https://github.com/your-org/TradeFlowProduct/issues
- **邮箱支持**: api-support@tradeflow.com

### 社区资源
- **开发者论坛**: https://forum.tradeflow.com
- **Discord社区**: https://discord.gg/tradeflow
- **技术博客**: https://blog.tradeflow.com

### 更新通知
- **API变更通知**: 订阅邮件列表
- **版本发布**: GitHub Releases
- **维护公告**: 状态页面

## 📝 更新记录

| 版本 | 日期 | 更新内容 | 作者 |
|------|------|----------|------|
| v1.0.0 | 2025-01-07 | 初始版本，完整API文档体系 | API团队 |

## 📄 许可证

本项目遵循 [MIT License](../LICENSE)

---

*本文档会随着API的发展持续更新，请关注我们的更新通知获取最新信息。*