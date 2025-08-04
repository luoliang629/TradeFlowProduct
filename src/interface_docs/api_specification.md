# TradeFlow API 接口规范文档

## 文档概述

本文档定义了 TradeFlow B2B 贸易智能助手的完整 API 接口规范，包括 RESTful API 和 SSE 实时通信接口。

**版本**: v1.0.0  
**基础URL**: `https://api.tradeflow.com/api/v1`  
**文档生成时间**: 2024-01-01

---

## 1. API 设计原则

### 1.1 RESTful 设计
- 遵循 REST 架构风格
- 使用 HTTP 动词表示操作（GET、POST、PUT、DELETE）
- 资源导向的 URL 设计
- 无状态通信

### 1.2 响应格式
- 统一 JSON 响应格式
- 明确的错误码和错误信息
- 支持国际化错误消息

### 1.3 安全机制
- JWT Token 认证
- OAuth 2.0 第三方登录
- API 请求限流
- HTTPS 强制加密

---

## 2. 通用规范

### 2.1 请求头
```http
Content-Type: application/json
Authorization: Bearer {jwt_token}
Accept-Language: en-US,zh-CN
X-Client-Version: 1.0.0
```

### 2.2 统一响应格式

#### 成功响应
```json
{
  "success": true,
  "data": {},
  "message": "操作成功",
  "timestamp": "2024-01-01T12:00:00Z",
  "request_id": "req_123456"
}
```

#### 错误响应
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "参数验证失败",
    "details": [
      {
        "field": "email",
        "message": "邮箱格式不正确"
      }
    ]
  },
  "timestamp": "2024-01-01T12:00:00Z",
  "request_id": "req_123456"
}
```

### 2.3 分页格式
```json
{
  "success": true,
  "data": {
    "items": [],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 100,
      "total_pages": 5,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

### 2.4 错误码定义
```json
{
  "400": "BAD_REQUEST - 请求参数错误",
  "401": "UNAUTHORIZED - 未授权访问",
  "403": "FORBIDDEN - 权限不足",
  "404": "NOT_FOUND - 资源不存在",
  "409": "CONFLICT - 资源冲突",
  "422": "VALIDATION_ERROR - 参数验证失败",
  "429": "RATE_LIMIT_EXCEEDED - 请求频率超限",
  "500": "INTERNAL_SERVER_ERROR - 服务器内部错误",
  "503": "SERVICE_UNAVAILABLE - 服务不可用"
}
```

---

## 3. 认证相关接口

### 3.1 OAuth 登录

#### 发起 OAuth 登录
```http
GET /auth/oauth/{provider}
```

**路径参数**:
- `provider`: OAuth 提供商 (`google`, `github`)

**查询参数**:
- `redirect_uri`: 登录成功后的回调地址
- `state`: 防 CSRF 状态参数

**响应**: 重定向到 OAuth 提供商授权页面

#### OAuth 回调处理
```http
GET /auth/oauth/{provider}/callback
```

**查询参数**:
- `code`: 授权码
- `state`: 状态参数

**响应**:
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "expires_in": 86400,
    "user": {
      "id": "usr_123456",
      "email": "user@example.com",
      "name": "张三",
      "avatar_url": "https://example.com/avatar.jpg",
      "auth_provider": "google",
      "language_preference": "zh-CN",
      "created_at": "2024-01-01T12:00:00Z"
    }
  }
}
```

### 3.2 Token 管理

#### 刷新 Token
```http
POST /auth/refresh
```

**请求体**:
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "access_token": "new_access_token",
    "expires_in": 86400
  }
}
```

#### 退出登录
```http
POST /auth/logout
```

**响应**:
```json
{
  "success": true,
  "message": "退出登录成功"
}
```

#### 获取当前用户信息
```http
GET /auth/me
```

**响应**:
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "usr_123456",
      "email": "user@example.com",
      "name": "张三",
      "company": {
        "id": "comp_123456",
        "name": "上海贸易公司",
        "verification_status": "verified",
        "trust_score": 85
      },
      "subscription": {
        "plan": "professional",
        "credits_remaining": 150,
        "expires_at": "2024-12-31T23:59:59Z"
      }
    }
  }
}
```

---

## 4. Agent 对话接口

### 4.1 HTTP 对话接口

#### 发起对话
```http
POST /chat
```

**请求体**:
```json
{
  "message": "我需要找美国的LED灯具买家",
  "agent_type": "buyer",
  "session_id": "sess_123456",
  "context": {
    "product_info": {
      "name": "LED Panel Light",
      "category": "lighting",
      "price_range": "$10-50"
    },
    "user_preferences": {
      "language": "zh-CN",
      "target_markets": ["US", "EU"]
    }
  },
  "stream": true
}
```

**响应** (非流式):
```json
{
  "success": true,
  "data": {
    "response": {
      "content": "根据您的需求，我为您找到了5家美国LED灯具买家...",
      "agent_type": "buyer",
      "session_id": "sess_123456",
      "recommendations": [
        {
          "id": "buyer_001",
          "company_name": "Bright Lighting Inc.",
          "country": "US",
          "match_score": 0.92,
          "reasoning": "该公司专注于LED照明产品，年采购量超过200万美元"
        }
      ],
      "metadata": {
        "tokens_used": 150,
        "processing_time": 2.5,
        "confidence_score": 0.85,
        "data_sources": ["trade_data", "company_db"]
      }
    }
  }
}
```

#### 获取对话历史
```http
GET /chat/history
```

**查询参数**:
- `session_id`: 会话ID (可选)
- `agent_type`: Agent类型 (可选)
- `page`: 页码 (默认: 1)
- `limit`: 每页数量 (默认: 20, 最大: 100)
- `start_date`: 开始日期 (可选)
- `end_date`: 结束日期 (可选)

**响应**:
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "msg_123456",
        "session_id": "sess_123456",
        "agent_type": "buyer",
        "user_message": "找LED灯具买家",
        "agent_response": "为您找到了5家买家...",
        "tokens_used": 150,
        "created_at": "2024-01-01T12:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 50,
      "total_pages": 3,
      "has_next": true
    }
  }
}
```

#### 删除会话
```http
DELETE /chat/session/{session_id}
```

**响应**:
```json
{
  "success": true,
  "message": "会话删除成功"
}
```

### 4.2 SSE 流式对话接口

#### 建立 SSE 连接
```http
GET /chat/stream?token={jwt_token}&session_id={session_id}
```

**查询参数**:
- `token`: JWT 访问令牌
- `session_id`: 会话ID (可选，不提供则创建新会话)

**响应头**:
```http
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
Access-Control-Allow-Origin: *
```

#### SSE 事件类型

**1. 连接建立**
```
event: connected
data: {"session_id": "sess_123456", "agent_ready": true}
```

**2. 流式内容**
```
event: stream
data: {"chunk": "根据您的需求", "chunk_id": 1}

event: stream
data: {"chunk": "，我为您找到了", "chunk_id": 2}
```

**3. Agent状态更新**
```
event: agent_status
data: {"status": "thinking", "operation": "搜索买家数据库", "progress": 0.3}
```

**4. 推荐结果**
```
event: recommendation
data: {
  "type": "buyer",
  "company": {
    "name": "Bright Lighting Inc.",
    "country": "US",
    "score": 0.92
  },
  "preview": true
}
```

**5. 完成事件**
```
event: complete
data: {
  "session_id": "sess_123456",
  "total_recommendations": 5,
  "tokens_used": 150,
  "processing_time": 3.2
}
```

**6. 错误事件**
```
event: error
data: {
  "error": "AGENT_PROCESSING_ERROR",
  "message": "Agent处理超时",
  "retry_after": 5
}
```

---

## 5. 买家开发接口

### 5.1 获取买家推荐

```http
POST /buyers/recommend
```

**请求体**:
```json
{
  "product_info": {
    "name": "LED Panel Light",
    "category": "lighting",
    "subcategory": "commercial_lighting",
    "description": "高效节能LED面板灯，适用于办公和商业场所",
    "hs_code": "940540",
    "specifications": {
      "power": "36W",
      "color_temperature": "4000K",
      "dimensions": "600x600mm"
    },
    "price_range": {
      "min": 10,
      "max": 50,
      "currency": "USD",
      "unit": "piece"
    },
    "moq": 500,
    "lead_time": "15-30 days"
  },
  "target_markets": ["US", "DE", "UK", "CA"],
  "preferences": {
    "company_size": ["medium", "large"],
    "trade_terms": ["FOB", "CIF"],
    "payment_terms": ["T/T", "L/C"],
    "order_frequency": "monthly",
    "relationship_type": "distributor"
  },
  "filters": {
    "exclude_countries": ["CN"],
    "min_annual_purchase": 1000000,
    "verification_required": true
  }
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "recommendations": [
      {
        "id": "buyer_001",
        "company_name": "Bright Lighting Inc.",
        "country": "US",
        "state": "California",
        "city": "Los Angeles",
        "match_score": 0.92,
        "buyer_profile": {
          "company_type": "distributor",
          "annual_purchase": "$2M+",
          "main_products": ["LED lights", "Smart lighting", "Industrial lighting"],
          "company_size": "50-200",
          "established_year": 2010,
          "certifications": ["UL", "Energy Star"],
          "market_focus": ["North America", "Europe"]
        },
        "trade_info": {
          "preferred_terms": "FOB",
          "payment_terms": "30% T/T, 70% L/C",
          "typical_order_size": "$50K-200K",
          "order_frequency": "Monthly"
        },
        "contact_info": {
          "website": "https://brightlighting.com",
          "contact_person": "John Smith",
          "position": "Purchasing Manager",
          "email": "purchasing@brightlighting.com",
          "phone": "+1-555-0123"
        },
        "match_reasons": [
          "产品类别完全匹配",
          "采购量符合您的MOQ要求",
          "支持您偏好的FOB贸易条款",
          "在目标市场有强大的分销网络"
        ],
        "risk_assessment": {
          "credit_rating": "A",
          "payment_history": "excellent",
          "business_stability": "high",
          "verification_status": "verified"
        }
      }
    ],
    "total": 15,
    "query_metadata": {
      "query_id": "qry_123456",
      "search_criteria": "LED lighting products in North American market",
      "data_sources": ["trade_data", "company_directory", "customs_data"],
      "last_updated": "2024-01-01T12:00:00Z"
    }
  }
}
```

### 5.2 获取买家详情

```http
GET /buyers/{buyer_id}
```

**路径参数**:
- `buyer_id`: 买家ID

**响应**:
```json
{
  "success": true,
  "data": {
    "buyer": {
      "id": "buyer_001",
      "company_name": "Bright Lighting Inc.",
      "basic_info": {
        "registration_number": "US123456789",
        "tax_id": "12-3456789",
        "address": {
          "street": "123 Business Ave",
          "city": "Los Angeles",
          "state": "CA",
          "postal_code": "90210",
          "country": "US"
        },
        "founded_year": 2010,
        "employee_count": "50-200",
        "annual_revenue": "$10M-50M"
      },
      "business_details": {
        "business_type": ["distributor", "retailer"],
        "main_markets": ["US", "CA", "MX"],
        "product_categories": ["lighting", "electrical", "smart_home"],
        "certifications": ["UL Listed", "Energy Star Partner"],
        "warehouse_locations": ["Los Angeles", "New York"]
      },
      "trade_history": {
        "total_import_value": 15000000,
        "main_suppliers": ["China", "Germany", "South Korea"],
        "recent_orders": [
          {
            "date": "2023-12-01",
            "product": "LED Strip Lights",
            "value": 50000,
            "supplier_country": "CN"
          }
        ]
      },
      "contact_details": {
        "primary_contact": {
          "name": "John Smith",
          "position": "Purchasing Manager",
          "email": "j.smith@brightlighting.com",
          "phone": "+1-555-0123",
          "languages": ["English", "Spanish"]
        },
        "alternative_contacts": []
      },
      "verification": {
        "status": "verified",
        "verified_date": "2023-06-15",
        "verification_documents": ["business_license", "tax_certificate"],
        "trust_score": 85
      }
    }
  }
}
```

### 5.3 生成联系模板

```http
POST /buyers/{buyer_id}/contact
```

**请求体**:
```json
{
  "product_info": {
    "name": "LED Panel Light",
    "key_features": ["Energy efficient", "Long lifespan", "Easy installation"]
  },
  "template_type": "introduction",
  "language": "en",
  "tone": "professional",
  "include_company_intro": true,
  "include_samples": true
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "template": {
      "subject": "Premium LED Panel Lights - Partnership Opportunity",
      "content": "Dear Mr. Smith,\n\nI hope this email finds you well. My name is [Your Name] from [Your Company], a leading manufacturer of high-quality LED lighting solutions.\n\nI came across Bright Lighting Inc. and was impressed by your strong presence in the North American lighting market...",
      "follow_up_suggestions": [
        "发送产品目录和价格表",
        "提议安排视频会议讨论合作",
        "邀请参观工厂或参加展会"
      ],
      "best_contact_time": "9:00-17:00 PST",
      "cultural_notes": [
        "American business culture values directness and efficiency",
        "Include specific product benefits and competitive advantages",
        "Mention compliance with US standards (UL, Energy Star)"
      ]
    }
  }
}
```

---

## 6. 供应商匹配接口

### 6.1 搜索供应商

```http
POST /suppliers/search
```

**请求体**:
```json
{
  "product_requirements": {
    "category": "textiles",
    "subcategory": "cotton_fabric",
    "specifications": {
      "material": "100% cotton",
      "weight": "200-250 GSM",
      "width": "150cm",
      "color": "white"
    },
    "quality_standards": ["OEKO-TEX", "GOTS"],
    "quantity": {
      "moq": 1000,
      "annual_demand": 100000,
      "unit": "meters"
    }
  },
  "supplier_preferences": {
    "countries": ["CN", "IN", "TR", "BD"],
    "company_size": ["medium", "large"],
    "certifications_required": ["ISO9001", "OEKO-TEX"],
    "production_capacity": "high",
    "export_experience": "5+ years"
  },
  "trade_terms": {
    "payment_terms": ["T/T", "L/C"],
    "delivery_terms": ["FOB", "CIF"],
    "lead_time": "30-45 days"
  }
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "suppliers": [
      {
        "id": "sup_001",
        "company_name": "Shanghai Textile Manufacturing Co., Ltd.",
        "country": "CN",
        "city": "Shanghai",
        "match_score": 0.89,
        "capabilities": {
          "main_products": ["Cotton fabric", "Polyester fabric", "Blended fabric"],
          "production_capacity": "500,000 meters/month",
          "moq": 500,
          "lead_time": "25-35 days",
          "export_markets": ["US", "EU", "AU", "CA"]
        },
        "certifications": [
          {
            "name": "OEKO-TEX Standard 100",
            "number": "2023OK0123",
            "valid_until": "2024-12-31"
          },
          {
            "name": "ISO 9001:2015",
            "number": "ISO123456",
            "valid_until": "2025-06-30"
          }
        ],
        "pricing": {
          "price_range": "$2.50-$4.00",
          "currency": "USD",
          "unit": "meter",
          "price_terms": "FOB Shanghai",
          "payment_terms": "30% T/T, 70% L/C at sight"
        },
        "quality_assurance": {
          "quality_control": "Third-party inspection available",
          "sample_policy": "Free samples available",
          "warranty": "Quality guarantee for 12 months"
        }
      }
    ],
    "total": 12,
    "search_metadata": {
      "search_id": "search_123456",
      "filters_applied": 8,
      "data_sources": ["supplier_directory", "trade_data", "certification_db"]
    }
  }
}
```

### 6.2 供应商对比

```http
POST /suppliers/compare
```

**请求体**:
```json
{
  "supplier_ids": ["sup_001", "sup_002", "sup_003"],
  "comparison_criteria": [
    "pricing",
    "quality",
    "delivery_time",
    "certifications",
    "export_experience"
  ]
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "comparison": {
      "suppliers": [
        {
          "id": "sup_001",
          "name": "Shanghai Textile Co.",
          "country": "CN",
          "scores": {
            "pricing": 8.5,
            "quality": 9.0,
            "delivery": 8.0,
            "certifications": 9.5,
            "experience": 9.0
          },
          "overall_score": 8.8
        }
      ],
      "summary": {
        "best_for_price": "sup_002",
        "best_for_quality": "sup_001",
        "best_overall": "sup_001",
        "recommendations": [
          "Shanghai Textile Co. 在质量和认证方面表现最佳",
          "考虑价格因素，建议进一步与供应商协商批量采购折扣"
        ]
      }
    }
  }
}
```

---

## 7. 产品管理接口

### 7.1 创建产品

```http
POST /products
```

**请求体**:
```json
{
  "name": "LED Panel Light Pro",
  "category": "lighting",
  "subcategory": "commercial_lighting",
  "description": "高效节能LED面板灯，适用于办公和商业场所",
  "specifications": {
    "power": "36W",
    "voltage": "AC 100-240V",
    "color_temperature": "4000K",
    "lumens": "3600lm",
    "dimensions": "600x600x15mm",
    "material": "Aluminum + PMMA"
  },
  "pricing": {
    "price": 25.50,
    "currency": "USD",
    "unit": "piece",
    "moq": 500,
    "price_breaks": [
      {"quantity": 500, "price": 25.50},
      {"quantity": 1000, "price": 24.00},
      {"quantity": 5000, "price": 22.50}
    ]
  },
  "certifications": ["CE", "RoHS", "Energy Star"],
  "images": [
    "https://example.com/product1.jpg",
    "https://example.com/product2.jpg"
  ],
  "hs_code": "940540",
  "lead_time": "15-30 days",
  "packaging": {
    "unit_size": "620x620x50mm",
    "weight": "2.5kg",
    "carton_qty": 10
  }
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "product": {
      "id": "prod_123456",
      "name": "LED Panel Light Pro",
      "slug": "led-panel-light-pro",
      "status": "active",
      "created_at": "2024-01-01T12:00:00Z",
      "updated_at": "2024-01-01T12:00:00Z"
    }
  }
}
```

### 7.2 获取产品列表

```http
GET /products
```

**查询参数**:
- `category`: 产品类别 (可选)
- `status`: 产品状态 (可选)
- `page`: 页码 (默认: 1)
- `limit`: 每页数量 (默认: 20)
- `search`: 搜索关键词 (可选)
- `sort`: 排序字段 (默认: created_at)
- `order`: 排序方向 (asc/desc, 默认: desc)

**响应**:
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "prod_123456",
        "name": "LED Panel Light Pro",
        "category": "lighting",
        "price": 25.50,
        "currency": "USD",
        "moq": 500,
        "status": "active",
        "created_at": "2024-01-01T12:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 50,
      "total_pages": 3
    }
  }
}
```

---

## 8. 订阅和支付接口

### 8.1 获取订阅计划

```http
GET /subscription/plans
```

**响应**:
```json
{
  "success": true,
  "data": {
    "plans": [
      {
        "id": "plan_starter",
        "name": "Starter",
        "description": "适合个人用户和小企业",
        "price": {
          "monthly": 29,
          "yearly": 290,
          "currency": "USD"
        },
        "features": {
          "conversations_per_month": 50,
          "buyer_recommendations": 100,
          "supplier_searches": 50,
          "export_formats": ["PDF", "Excel"],
          "support": "Email"
        },
        "limits": {
          "api_calls_per_day": 1000,
          "concurrent_sessions": 2
        }
      },
      {
        "id": "plan_professional",
        "name": "Professional",
        "description": "适合成长型企业",
        "price": {
          "monthly": 99,
          "yearly": 990,
          "currency": "USD"
        },
        "features": {
          "conversations_per_month": 200,
          "buyer_recommendations": 500,
          "supplier_searches": 200,
          "export_formats": ["PDF", "Excel", "CSV"],
          "support": "Priority Email + Live Chat",
          "custom_branding": true
        },
        "limits": {
          "api_calls_per_day": 5000,
          "concurrent_sessions": 5
        }
      }
    ]
  }
}
```

### 8.2 创建订阅

```http
POST /subscription/create
```

**请求体**:
```json
{
  "plan_id": "plan_professional",
  "billing_cycle": "monthly",
  "payment_method": "stripe",
  "stripe_payment_method_id": "pm_123456"
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "subscription": {
      "id": "sub_123456",
      "plan_id": "plan_professional",
      "status": "active",
      "current_period_start": "2024-01-01T00:00:00Z",
      "current_period_end": "2024-02-01T00:00:00Z",
      "credits_remaining": 200,
      "auto_renew": true
    },
    "invoice": {
      "id": "inv_123456",
      "amount": 99,
      "currency": "USD",
      "status": "paid",
      "paid_at": "2024-01-01T12:00:00Z"
    }
  }
}
```

### 8.3 使用统计

```http
GET /usage/summary
```

**查询参数**:
- `period`: 统计周期 (`current_month`, `last_month`, `current_year`)
- `breakdown`: 是否显示详细分解 (true/false)

**响应**:
```json
{
  "success": true,
  "data": {
    "period": "current_month",
    "period_start": "2024-01-01T00:00:00Z",
    "period_end": "2024-01-31T23:59:59Z",
    "usage": {
      "conversations": {
        "used": 45,
        "limit": 200,
        "remaining": 155
      },
      "buyer_recommendations": {
        "used": 120,
        "limit": 500,
        "remaining": 380
      },
      "supplier_searches": {
        "used": 35,
        "limit": 200,
        "remaining": 165
      },
      "api_calls": {
        "used": 2500,
        "limit": 5000,
        "remaining": 2500
      }
    },
    "breakdown": [
      {
        "date": "2024-01-01",
        "conversations": 3,
        "api_calls": 150
      }
    ],
    "cost_breakdown": {
      "base_subscription": 99,
      "overage_charges": 0,
      "total": 99,
      "currency": "USD"
    }
  }
}
```

---

## 9. 系统接口

### 9.1 健康检查

```http
GET /health
```

**响应**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "1.0.0",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "ai_agent": "healthy"
  }
}
```

### 9.2 系统状态

```http
GET /status
```

**响应**:
```json
{
  "success": true,
  "data": {
    "system": {
      "uptime": 86400,
      "load": {
        "cpu": 45,
        "memory": 60,
        "disk": 30
      }
    },
    "ai_agents": {
      "buyer_agent": {
        "status": "active",
        "queue_length": 5,
        "avg_response_time": 2.3
      },
      "supplier_agent": {
        "status": "active",
        "queue_length": 2,
        "avg_response_time": 1.8
      }
    }
  }
}
```

---

## 10. 错误处理和状态码

### 10.1 HTTP状态码使用

- `200 OK`: 请求成功
- `201 Created`: 资源创建成功
- `204 No Content`: 请求成功但无返回内容
- `400 Bad Request`: 客户端请求错误
- `401 Unauthorized`: 未授权
- `403 Forbidden`: 权限不足
- `404 Not Found`: 资源不存在
- `409 Conflict`: 资源冲突
- `422 Unprocessable Entity`: 参数验证失败
- `429 Too Many Requests`: 请求频率超限
- `500 Internal Server Error`: 服务器内部错误
- `503 Service Unavailable`: 服务不可用

### 10.2 错误响应格式

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "参数验证失败",
    "details": [
      {
        "field": "email",
        "code": "INVALID_FORMAT",
        "message": "邮箱格式不正确"
      }
    ]
  },
  "timestamp": "2024-01-01T12:00:00Z",
  "request_id": "req_123456",
  "documentation_url": "https://docs.tradeflow.com/api/errors#VALIDATION_ERROR"
}
```

### 10.3 业务错误码

```json
{
  "AUTH_001": "Invalid credentials",
  "AUTH_002": "Token expired", 
  "AUTH_003": "Account suspended",
  "AGENT_001": "Agent processing timeout",
  "AGENT_002": "Agent service unavailable",
  "QUOTA_001": "Monthly quota exceeded",
  "QUOTA_002": "Rate limit exceeded",
  "DATA_001": "Invalid product category",
  "DATA_002": "Country not supported",
  "PAYMENT_001": "Payment method declined",
  "PAYMENT_002": "Subscription expired"
}
```

---

## 11. API版本管理

### 11.1 版本策略
- 使用URL路径版本控制: `/api/v1/`, `/api/v2/`
- 主版本号表示不兼容的API更改
- 次版本号表示向后兼容的功能添加
- 补丁版本号表示向后兼容的问题修复

### 11.2 弃用策略
- 新版本发布后，旧版本至少维护12个月
- 提前6个月通知API弃用
- 在响应头中标识即将弃用的功能

```http
Deprecation: true
Sunset: 2024-12-31T23:59:59Z
Link: </api/v2/buyers/recommend>; rel="successor-version"
```

---

## 12. 安全规范

### 12.1 认证机制
- JWT Token 有效期: 24小时
- Refresh Token 有效期: 30天  
- 支持Token黑名单机制
- 异地登录检测和通知

### 12.2 API限流
```json
{
  "rate_limits": {
    "authenticated": "1000 requests/hour",
    "unauthenticated": "100 requests/hour",
    "premium": "5000 requests/hour"
  }
}
```

### 12.3 数据安全
- 所有API强制HTTPS
- 敏感数据加密存储
- 个人信息脱敏处理
- 完整的审计日志

---

## 13. 性能优化

### 13.1 缓存策略
- Redis缓存热点数据，TTL 1小时
- CDN缓存静态资源
- 数据库查询优化
- API响应压缩

### 13.2 分页优化
- 默认分页大小: 20
- 最大分页大小: 100
- 使用游标分页处理大数据集
- 提供总数统计的可选性

### 13.3 监控指标
- API响应时间 < 2秒
- 可用性 > 99.9%
- 错误率 < 0.1%
- Agent响应时间 < 5秒

---

**文档更新日期**: 2024-01-01  
**联系方式**: api-support@tradeflow.com  
**技术支持**: https://docs.tradeflow.com