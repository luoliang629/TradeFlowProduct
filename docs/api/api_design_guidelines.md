# TradeFlow API 设计规范

## 📋 文档概述

本文档定义了TradeFlow项目的API设计标准和最佳实践，旨在确保API的一致性、可维护性和用户体验。所有API开发者必须严格遵循本规范。

- **版本**: v1.0
- **创建日期**: 2025-01-07
- **适用范围**: TradeFlow所有API接口
- **更新周期**: 季度评审更新

## 🎯 设计原则

### 1. RESTful设计原则

#### 1.1 资源导向设计
- API应以资源为中心进行设计，而非功能
- 资源名称使用名词，避免动词
- 体现资源的层级关系

```yaml
# ✅ 良好示例
GET    /api/v1/users/{id}                    # 获取用户
GET    /api/v1/users/{id}/companies          # 获取用户的公司
POST   /api/v1/chat                          # 创建对话
GET    /api/v1/chat/history                  # 获取对话历史

# ❌ 错误示例
GET    /api/v1/getUser/{id}                  # 动词形式
POST   /api/v1/createChat                    # 动词形式
GET    /api/v1/getUserCompanies/{id}         # 动词形式
```

#### 1.2 复数形式规范
- 集合资源使用复数形式
- 单个资源通过ID访问时仍保持复数路径

```yaml
# ✅ 标准格式
GET    /api/v1/users                         # 用户列表
GET    /api/v1/users/{id}                    # 单个用户
POST   /api/v1/files                         # 上传文件
GET    /api/v1/files/{id}                    # 单个文件

# ❌ 避免混用
GET    /api/v1/user                          # 不一致
GET    /api/v1/file/{id}                     # 不一致
```

### 2. HTTP方法使用规范

#### 2.1 标准HTTP方法语义

| 方法   | 用途 | 幂等性 | 安全性 | 示例 |
|--------|------|--------|--------|------|
| GET    | 读取资源 | ✅ | ✅ | `GET /api/v1/users/{id}` |
| POST   | 创建资源或执行操作 | ❌ | ❌ | `POST /api/v1/users` |
| PUT    | 完整更新资源 | ✅ | ❌ | `PUT /api/v1/users/{id}` |
| PATCH  | 部分更新资源 | ❌ | ❌ | `PATCH /api/v1/users/{id}` |
| DELETE | 删除资源 | ✅ | ❌ | `DELETE /api/v1/users/{id}` |

#### 2.2 特殊操作处理
对于不能简单映射到CRUD操作的业务逻辑，采用以下模式：

```yaml
# 子资源模式
POST   /api/v1/users/{id}/password-reset     # 重置密码
POST   /api/v1/orders/{id}/cancel            # 取消订单
POST   /api/v1/files/{id}/share              # 分享文件

# 动作模式（特殊情况下使用）
POST   /api/v1/buyers/recommend              # 买家推荐
POST   /api/v1/suppliers/search              # 供应商搜索
POST   /api/v1/suppliers/compare             # 供应商对比
```

## 🌐 URL命名规范

### 3.1 层级关系表示

```yaml
# 一级资源
/api/v1/users                               # 用户管理
/api/v1/chat                                # 对话管理
/api/v1/files                               # 文件管理

# 二级资源（从属关系）
/api/v1/users/{id}/profile                  # 用户资料
/api/v1/users/{id}/subscription             # 用户订阅
/api/v1/chat/{session_id}/messages          # 对话消息
/api/v1/files/{id}/preview                  # 文件预览

# 三级资源（谨慎使用，避免过深嵌套）
/api/v1/users/{id}/companies/{company_id}/certificates
```

### 3.2 命名约定

```yaml
# URL段命名规则
- 使用小写字母
- 单词间使用连字符(-)分隔
- 避免下划线和驼峰
- 使用有意义的名称

# ✅ 良好示例
/api/v1/subscription-plans
/api/v1/oauth-providers
/api/v1/password-reset

# ❌ 错误示例
/api/v1/subscriptionPlans      # 驼峰
/api/v1/subscription_plans     # 下划线
/api/v1/sub-plans             # 缩写
```

## 📊 HTTP状态码规范

### 4.1 状态码使用标准

#### 成功状态码 (2xx)
```yaml
200 OK:
  - 用途: GET请求成功，PUT/PATCH更新成功
  - 示例: 获取用户信息，更新用户资料

201 Created:
  - 用途: POST请求成功创建资源
  - 示例: 创建用户，上传文件
  - 必须: 返回新创建资源的标识符

204 No Content:
  - 用途: DELETE成功，无返回内容
  - 示例: 删除文件，注销用户
```

#### 重定向状态码 (3xx)
```yaml
302 Found:
  - 用途: OAuth登录重定向
  - 示例: 重定向到OAuth提供商

304 Not Modified:
  - 用途: 缓存未过期
  - 示例: 条件请求资源未修改
```

#### 客户端错误 (4xx)
```yaml
400 Bad Request:
  - 用途: 请求参数错误，格式错误
  - 示例: 缺少必填字段，格式不正确

401 Unauthorized:
  - 用途: 未认证，Token无效或过期
  - 示例: 未登录，Token过期

403 Forbidden:
  - 用途: 已认证但无权限
  - 示例: 访问他人资源，权限不足

404 Not Found:
  - 用途: 资源不存在
  - 示例: 用户不存在，文件不存在

409 Conflict:
  - 用途: 资源冲突
  - 示例: 邮箱已存在，重复操作

422 Unprocessable Entity:
  - 用途: 请求格式正确但逻辑错误
  - 示例: 业务规则验证失败

429 Too Many Requests:
  - 用途: 请求频率超限
  - 示例: API限流，超过调用配额
```

#### 服务器错误 (5xx)
```yaml
500 Internal Server Error:
  - 用途: 服务器内部错误
  - 注意: 不应暴露详细错误信息

502 Bad Gateway:
  - 用途: 上游服务错误
  - 示例: 第三方API调用失败

503 Service Unavailable:
  - 用途: 服务暂时不可用
  - 示例: 系统维护，过载保护
```

## 📄 请求/响应格式标准

### 5.1 统一响应格式

所有API响应必须遵循统一格式：

```json
{
  "success": boolean,
  "timestamp": "2025-01-07T10:00:00Z",
  "request_id": "req_123456789",
  "data": object | array | null,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": [
      {
        "field": "email",
        "message": "邮箱格式不正确"
      }
    ]
  },
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "total_pages": 5,
    "has_next": true,
    "has_prev": false
  }
}
```

### 5.2 成功响应示例

```json
// 单个资源响应
{
  "success": true,
  "timestamp": "2025-01-07T10:00:00Z",
  "request_id": "req_123456789",
  "data": {
    "user": {
      "id": "user_123",
      "email": "user@example.com",
      "name": "张三"
    }
  }
}

// 列表资源响应
{
  "success": true,
  "timestamp": "2025-01-07T10:00:00Z",
  "request_id": "req_123456789",
  "data": {
    "items": [
      {
        "id": "file_123",
        "name": "document.pdf",
        "size": 1024000
      }
    ]
  },
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 1,
    "total_pages": 1,
    "has_next": false,
    "has_prev": false
  }
}
```

### 5.3 错误响应示例

```json
// 验证错误
{
  "success": false,
  "timestamp": "2025-01-07T10:00:00Z",
  "request_id": "req_123456789",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "请求参数验证失败",
    "details": [
      {
        "field": "email",
        "message": "邮箱格式不正确"
      },
      {
        "field": "password",
        "message": "密码长度不能少于8位"
      }
    ]
  }
}

// 业务逻辑错误
{
  "success": false,
  "timestamp": "2025-01-07T10:00:00Z",
  "request_id": "req_123456789",
  "error": {
    "code": "INSUFFICIENT_CREDITS",
    "message": "积分不足，无法继续使用服务"
  }
}
```

## 📃 分页、排序、过滤规范

### 6.1 分页参数

```yaml
查询参数:
  page: 页码，从1开始，默认1
  limit: 每页数量，默认20，最大100
  
URL示例:
  GET /api/v1/files?page=2&limit=50

响应格式:
  pagination:
    page: 2
    limit: 50
    total: 150
    total_pages: 3
    has_next: true
    has_prev: true
```

### 6.2 排序参数

```yaml
查询参数:
  sort: 排序字段，支持多字段
  order: 排序方向 (asc/desc)，默认asc
  
URL示例:
  GET /api/v1/users?sort=created_at&order=desc
  GET /api/v1/files?sort=name,size&order=asc,desc

多字段排序格式:
  sort=field1,field2&order=asc,desc
```

### 6.3 过滤参数

```yaml
基础过滤:
  GET /api/v1/files?type=document&session_id=sess_123

时间范围过滤:
  GET /api/v1/chat/history?created_after=2025-01-01T00:00:00Z
  GET /api/v1/chat/history?created_before=2025-01-31T23:59:59Z

搜索过滤:
  GET /api/v1/buyers?search=company_name&country=US

状态过滤:
  GET /api/v1/users?status=active&verified=true
```

## 🔄 版本管理策略

### 7.1 URL路径版本控制

```yaml
版本格式: /api/v{major}/
当前版本: /api/v1/
下个版本: /api/v2/

完整示例:
  https://api.tradeflow.com/api/v1/users
  https://api.tradeflow.com/api/v2/users
```

### 7.2 版本升级策略

```yaml
主要版本升级 (Breaking Changes):
  - URL路径版本号递增
  - 支持多版本并存
  - 提供迁移指南

次要版本升级 (Non-breaking Changes):
  - 保持相同版本号
  - 向后兼容
  - 渐进式功能增加

修复版本 (Bug Fixes):
  - 保持相同版本号
  - 透明升级
  - 不影响客户端
```

### 7.3 向后兼容原则

```yaml
兼容性变更 (允许):
  ✅ 添加新的API端点
  ✅ 添加新的响应字段（可选）
  ✅ 添加新的查询参数（可选）
  ✅ 扩展枚举值范围

破坏性变更 (需要新版本):
  ❌ 删除API端点
  ❌ 删除响应字段
  ❌ 修改字段类型
  ❌ 修改字段含义
  ❌ 修改错误码含义
  ❌ 修改默认行为
```

### 7.4 API废弃策略

```yaml
废弃流程:
  1. 通知期: 在响应头中添加废弃警告
     Deprecation: true
     Sunset: 2025-07-07T00:00:00Z
     
  2. 文档更新: 在API文档中标记为废弃
  
  3. 客户端通知: 邮件通知主要用户
  
  4. 迁移支持: 提供迁移指南和工具
  
  5. 下线执行: 6个月通知期后下线

废弃通知示例:
  HTTP/1.1 200 OK
  Deprecation: true
  Sunset: "Fri, 04 Jul 2025 00:00:00 GMT"
  Link: </api/v2/users>; rel="successor-version"
```

## ❌ 错误处理规范

### 8.1 错误码体系设计

```yaml
错误码格式: {CATEGORY}_{SPECIFIC_ERROR}

认证授权类:
  UNAUTHORIZED              # 未认证
  TOKEN_EXPIRED            # Token过期
  TOKEN_INVALID            # Token无效
  FORBIDDEN                # 无权限
  OAUTH_ERROR              # OAuth错误

验证类:
  VALIDATION_ERROR         # 参数验证错误
  REQUIRED_FIELD_MISSING   # 缺少必填字段
  INVALID_FORMAT          # 格式错误
  INVALID_VALUE           # 值无效

业务逻辑类:
  RESOURCE_NOT_FOUND      # 资源不存在
  RESOURCE_CONFLICT       # 资源冲突
  INSUFFICIENT_CREDITS    # 积分不足
  OPERATION_NOT_ALLOWED   # 操作不允许
  BUSINESS_RULE_VIOLATION # 业务规则违反

限流类:
  RATE_LIMIT_EXCEEDED     # 频率限制
  QUOTA_EXCEEDED          # 配额超限
  CONCURRENT_LIMIT        # 并发限制

系统类:
  INTERNAL_ERROR          # 内部错误
  SERVICE_UNAVAILABLE     # 服务不可用
  TIMEOUT_ERROR           # 超时错误
  MAINTENANCE_MODE        # 维护模式
```

### 8.2 多语言支持

```json
{
  "success": false,
  "timestamp": "2025-01-07T10:00:00Z",
  "request_id": "req_123456789",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "message_i18n": {
      "en": "Validation failed",
      "zh": "参数验证失败",
      "ja": "バリデーションに失敗しました"
    },
    "details": [
      {
        "field": "email",
        "message": "Invalid email format",
        "message_i18n": {
          "en": "Invalid email format",
          "zh": "邮箱格式不正确",
          "ja": "メールアドレスの形式が正しくありません"
        }
      }
    ]
  }
}
```

## 🔄 批量操作规范

### 9.1 批量创建

```yaml
POST /api/v1/products/batch
Content-Type: application/json

{
  "items": [
    {
      "name": "产品A",
      "category": "electronics"
    },
    {
      "name": "产品B", 
      "category": "clothing"
    }
  ]
}

响应:
{
  "success": true,
  "data": {
    "created": [
      {
        "id": "prod_123",
        "name": "产品A"
      }
    ],
    "failed": [
      {
        "index": 1,
        "error": {
          "code": "VALIDATION_ERROR",
          "message": "产品名称重复"
        }
      }
    ]
  }
}
```

### 9.2 批量更新

```yaml
PATCH /api/v1/users/batch
Content-Type: application/json

{
  "items": [
    {
      "id": "user_123",
      "status": "active"
    },
    {
      "id": "user_456", 
      "status": "inactive"
    }
  ]
}
```

### 9.3 批量删除

```yaml
DELETE /api/v1/files/batch
Content-Type: application/json

{
  "ids": ["file_123", "file_456", "file_789"]
}

响应:
{
  "success": true,
  "data": {
    "deleted": ["file_123", "file_456"],
    "failed": [
      {
        "id": "file_789",
        "error": {
          "code": "RESOURCE_NOT_FOUND",
          "message": "文件不存在"
        }
      }
    ]
  }
}
```

## ⏱️ 异步操作规范

### 10.1 长时间操作处理

```yaml
POST /api/v1/files/process
Content-Type: application/json

{
  "file_id": "file_123",
  "operation": "transcribe"
}

立即响应:
HTTP/1.1 202 Accepted
Location: /api/v1/jobs/job_456

{
  "success": true,
  "data": {
    "job": {
      "id": "job_456",
      "status": "pending",
      "progress": 0,
      "estimated_completion": "2025-01-07T10:05:00Z"
    }
  }
}
```

### 10.2 任务状态查询

```yaml
GET /api/v1/jobs/job_456

响应:
{
  "success": true,
  "data": {
    "job": {
      "id": "job_456",
      "status": "processing",
      "progress": 45,
      "created_at": "2025-01-07T10:00:00Z",
      "updated_at": "2025-01-07T10:02:00Z",
      "estimated_completion": "2025-01-07T10:05:00Z"
    }
  }
}

完成后:
{
  "success": true,
  "data": {
    "job": {
      "id": "job_456",
      "status": "completed",
      "progress": 100,
      "result": {
        "transcript": "文件转录内容...",
        "confidence": 0.95
      }
    }
  }
}
```

### 10.3 Webhook通知

```yaml
配置Webhook:
POST /api/v1/webhooks
{
  "url": "https://client.example.com/webhooks/tradeflow",
  "events": ["job.completed", "job.failed"]
}

Webhook负载:
{
  "event": "job.completed",
  "timestamp": "2025-01-07T10:05:00Z",
  "data": {
    "job_id": "job_456",
    "status": "completed",
    "result": {
      "transcript": "文件转录内容..."
    }
  }
}
```

## 📚 文档要求

### 11.1 API文档结构

```yaml
每个API端点必须包含:
  - 端点描述和用途
  - 请求参数说明
  - 响应格式说明
  - 错误码说明
  - 示例请求和响应
  - 业务规则说明
  - 权限要求
  - 限流规则
```

### 11.2 OpenAPI规范要求

```yaml
必需字段:
  - operationId: 唯一操作标识符
  - summary: 简要描述
  - description: 详细描述
  - tags: 分类标签
  - parameters: 参数定义
  - requestBody: 请求体定义（如需要）
  - responses: 响应定义
  - security: 安全要求（如需要）

推荐字段:
  - examples: 示例数据
  - deprecated: 废弃标记
  - externalDocs: 外部文档链接
```

### 11.3 代码示例要求

```yaml
每个API端点提供示例:
  - cURL示例
  - JavaScript示例
  - Python示例
  - 响应示例

cURL示例格式:
curl -X GET "https://api.tradeflow.com/api/v1/users/123" \
  -H "Authorization: Bearer {access_token}" \
  -H "Accept: application/json"

JavaScript示例格式:
const response = await fetch('/api/v1/users/123', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Accept': 'application/json'
  }
});
const data = await response.json();
```

## ✅ 实施检查清单

### 开发阶段检查
- [ ] URL设计遵循RESTful原则
- [ ] 使用正确的HTTP方法和状态码
- [ ] 实现统一的响应格式
- [ ] 添加适当的错误处理
- [ ] 实现分页、排序、过滤功能
- [ ] 支持批量操作（如需要）
- [ ] 处理异步操作（如需要）
- [ ] 添加请求验证
- [ ] 实现API限流
- [ ] 添加日志记录

### 文档阶段检查
- [ ] 完善OpenAPI规范定义
- [ ] 添加详细的接口说明
- [ ] 提供请求/响应示例
- [ ] 说明错误码和处理方式
- [ ] 添加权限要求说明
- [ ] 提供多语言代码示例

### 测试阶段检查
- [ ] 单元测试覆盖率>80%
- [ ] 集成测试覆盖主要流程
- [ ] 错误场景测试完整
- [ ] 性能测试满足要求
- [ ] 安全测试无高危漏洞
- [ ] 兼容性测试通过

### 上线阶段检查
- [ ] API版本控制就绪
- [ ] 监控和告警配置完成
- [ ] 限流规则配置正确
- [ ] 日志收集正常
- [ ] 文档同步更新
- [ ] 客户端通知（如有API变更）

---

*本规范将根据项目发展和最佳实践的演进持续更新，确保API设计的现代性和一致性。*