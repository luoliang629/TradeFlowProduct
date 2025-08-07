# TradeFlow 契约测试指南

## 1. 概述

契约测试是确保前后端API接口一致性的关键实践。本指南定义了TradeFlow项目中如何实施契约测试，确保前后端团队能够独立开发而不破坏集成。

**版本**: v1.0.0  
**更新日期**: 2025-01-07  
**相关文档**:
- [OpenAPI规范](./openapi_specification.yaml)
- [Mock服务配置](./mock_service_config.md)

## 2. 契约测试架构

### 2.1 核心概念

```mermaid
graph TB
    A[Consumer/前端] -->|定义期望| B[Contract/契约]
    C[Provider/后端] -->|验证实现| B
    B -->|生成| D[契约文件]
    D -->|验证| E[契约测试]
    E -->|通过| F[部署]
    E -->|失败| G[修复]
```

### 2.2 技术栈

| 组件 | 技术选型 | 用途 |
|-----|---------|------|
| 契约框架 | Pact | 契约定义和验证 |
| 前端测试 | Jest + Pact | Consumer契约测试 |
| 后端测试 | Pytest + Pact | Provider契约验证 |
| 契约仓库 | Pact Broker | 契约版本管理 |
| CI/CD | GitHub Actions | 自动化契约验证 |

## 3. Consumer端契约测试（前端）

### 3.1 环境配置

```bash
# 安装依赖
npm install --save-dev @pact-foundation/pact @pact-foundation/pact-node

# 配置文件结构
src/
├── contracts/
│   ├── setup.js           # Pact配置
│   ├── consumer/           # Consumer测试
│   │   ├── auth.pact.js
│   │   ├── chat.pact.js
│   │   └── buyers.pact.js
│   └── pacts/             # 生成的契约文件
```

### 3.2 Pact配置

```javascript
// src/contracts/setup.js
import { Pact } from '@pact-foundation/pact'
import path from 'path'

export const createPact = (consumer, provider) => {
  return new Pact({
    consumer,
    provider,
    port: 8080,
    log: path.resolve(process.cwd(), 'logs', 'pact.log'),
    dir: path.resolve(process.cwd(), 'src/contracts/pacts'),
    logLevel: 'INFO',
    spec: 3,  // Pact规范版本
    pactfileWriteMode: 'update',
    cors: true
  })
}

// 全局配置
export const pactConfig = {
  brokerUrl: process.env.PACT_BROKER_URL || 'http://localhost:9292',
  brokerToken: process.env.PACT_BROKER_TOKEN,
  publishVerificationResult: true,
  providerVersion: process.env.GIT_COMMIT || '1.0.0',
  consumerVersion: process.env.GIT_COMMIT || '1.0.0'
}
```

### 3.3 Consumer契约测试示例

```javascript
// src/contracts/consumer/auth.pact.js
import { createPact } from '../setup'
import { Matchers } from '@pact-foundation/pact'
import { authService } from '../../services/auth'

const { like, term, eachLike } = Matchers

describe('Authentication API Contract', () => {
  const provider = createPact('TradeFlow-Frontend', 'TradeFlow-Backend')

  beforeAll(() => provider.setup())
  afterEach(() => provider.verify())
  afterAll(() => provider.finalize())

  describe('POST /auth/oauth/google/callback', () => {
    it('should return authentication tokens and user info', async () => {
      // 定义期望的请求和响应
      const expectedRequest = {
        method: 'GET',
        path: '/api/v1/auth/oauth/google/callback',
        query: {
          code: term({
            matcher: '^[A-Za-z0-9-_]+$',
            generate: 'test-auth-code-123'
          }),
          state: like('random-state-string')
        }
      }

      const expectedResponse = {
        status: 200,
        headers: {
          'Content-Type': 'application/json'
        },
        body: {
          success: true,
          data: {
            access_token: term({
              matcher: '^[A-Za-z0-9-_]+\\.[A-Za-z0-9-_]+\\.[A-Za-z0-9-_]+$',
              generate: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.signature'
            }),
            refresh_token: like('refresh-token-123'),
            expires_in: like(86400),
            user: {
              id: term({
                matcher: '^usr_[a-z0-9]+$',
                generate: 'usr_123456'
              }),
              email: term({
                matcher: '^[\\w._%+-]+@[\\w.-]+\\.[A-Za-z]{2,}$',
                generate: 'user@example.com'
              }),
              name: like('John Doe'),
              avatar_url: term({
                matcher: '^https?://.*',
                generate: 'https://example.com/avatar.jpg'
              }),
              auth_provider: term({
                matcher: '^(google|github)$',
                generate: 'google'
              }),
              language_preference: like('zh-CN'),
              created_at: term({
                matcher: '\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}',
                generate: '2024-01-01T12:00:00Z'
              })
            }
          },
          timestamp: like('2024-01-01T12:00:00Z'),
          request_id: like('req_123456')
        }
      }

      // 添加交互
      await provider.addInteraction({
        state: 'user has valid OAuth code',
        uponReceiving: 'a request for OAuth callback',
        withRequest: expectedRequest,
        willRespondWith: expectedResponse
      })

      // 执行实际请求
      const response = await authService.handleOAuthCallback(
        'google',
        'test-auth-code-123',
        'random-state-string'
      )

      // 验证响应
      expect(response.success).toBe(true)
      expect(response.data.access_token).toBeDefined()
      expect(response.data.user.email).toMatch(/^[\w._%+-]+@[\w.-]+\.[A-Za-z]{2,}$/)
    })

    it('should handle invalid auth code', async () => {
      await provider.addInteraction({
        state: 'user has invalid OAuth code',
        uponReceiving: 'a request with invalid code',
        withRequest: {
          method: 'GET',
          path: '/api/v1/auth/oauth/google/callback',
          query: {
            code: 'invalid-code'
          }
        },
        willRespondWith: {
          status: 401,
          body: {
            success: false,
            error: {
              code: 'INVALID_AUTH_CODE',
              message: like('授权码无效或已过期')
            }
          }
        }
      })

      try {
        await authService.handleOAuthCallback('google', 'invalid-code')
      } catch (error) {
        expect(error.code).toBe('INVALID_AUTH_CODE')
      }
    })
  })
})
```

```javascript
// src/contracts/consumer/chat.pact.js
import { createPact } from '../setup'
import { Matchers } from '@pact-foundation/pact'
import { chatService } from '../../services/chat'

const { like, eachLike, term } = Matchers

describe('Chat API Contract', () => {
  const provider = createPact('TradeFlow-Frontend', 'TradeFlow-Backend')

  beforeAll(() => provider.setup())
  afterEach(() => provider.verify())
  afterAll(() => provider.finalize())

  describe('POST /chat', () => {
    it('should create a chat with buyer agent', async () => {
      const chatRequest = {
        message: '我需要找美国的LED灯具买家',
        agent_type: 'buyer',
        session_id: 'sess_123456',
        stream: false
      }

      const expectedResponse = {
        status: 200,
        body: {
          success: true,
          data: {
            response: {
              content: like('根据您的需求，我为您找到了5家美国LED灯具买家'),
              agent_type: 'buyer',
              session_id: like('sess_123456'),
              recommendations: eachLike({
                id: term({
                  matcher: '^buyer_[a-z0-9]+$',
                  generate: 'buyer_001'
                }),
                company_name: like('Bright Lighting Inc.'),
                country: term({
                  matcher: '^[A-Z]{2}$',
                  generate: 'US'
                }),
                match_score: like(0.92)
              }, { min: 1 }),
              files: eachLike({
                id: term({
                  matcher: '^file_[a-z0-9]+$',
                  generate: 'file_001'
                }),
                name: like('buyer_list.csv'),
                type: term({
                  matcher: '^(code|document|data|image)$',
                  generate: 'data'
                })
              }),
              metadata: {
                tokens_used: like(150),
                processing_time: like(2.5),
                confidence_score: like(0.85)
              }
            }
          }
        }
      }

      await provider.addInteraction({
        state: 'agent is available',
        uponReceiving: 'a chat request for buyer agent',
        withRequest: {
          method: 'POST',
          path: '/api/v1/chat',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': term({
              matcher: '^Bearer .+$',
              generate: 'Bearer token123'
            })
          },
          body: chatRequest
        },
        willRespondWith: expectedResponse
      })

      const response = await chatService.sendMessage(chatRequest)
      expect(response.data.response.agent_type).toBe('buyer')
      expect(response.data.response.recommendations).toBeDefined()
      expect(response.data.response.recommendations.length).toBeGreaterThan(0)
    })
  })

  describe('GET /chat/stream (SSE)', () => {
    it('should establish SSE connection', async () => {
      // SSE契约测试需要特殊处理
      const sseContract = {
        state: 'SSE connection available',
        uponReceiving: 'SSE connection request',
        withRequest: {
          method: 'GET',
          path: '/api/v1/chat/stream',
          query: {
            token: like('jwt-token'),
            session_id: like('sess_123456')
          }
        },
        willRespondWith: {
          status: 200,
          headers: {
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive'
          }
        }
      }

      await provider.addInteraction(sseContract)

      // 测试SSE连接
      const eventSource = await chatService.createStreamConnection('jwt-token', 'sess_123456')
      expect(eventSource).toBeDefined()
      expect(eventSource.readyState).toBe(EventSource.CONNECTING)
    })
  })
})
```

### 3.4 文件管理契约测试

```javascript
// src/contracts/consumer/files.pact.js
import { createPact } from '../setup'
import { Matchers } from '@pact-foundation/pact'
import { fileService } from '../../services/files'

const { like, term, eachLike } = Matchers

describe('Files API Contract', () => {
  const provider = createPact('TradeFlow-Frontend', 'TradeFlow-Backend')

  beforeAll(() => provider.setup())
  afterEach(() => provider.verify())
  afterAll(() => provider.finalize())

  describe('GET /files', () => {
    it('should return file list with pagination', async () => {
      await provider.addInteraction({
        state: 'user has files',
        uponReceiving: 'a request for file list',
        withRequest: {
          method: 'GET',
          path: '/api/v1/files',
          query: {
            page: '1',
            limit: '20',
            session_id: 'sess_123456'
          },
          headers: {
            'Authorization': term({
              matcher: '^Bearer .+$',
              generate: 'Bearer token123'
            })
          }
        },
        willRespondWith: {
          status: 200,
          body: {
            success: true,
            data: {
              items: eachLike({
                id: term({
                  matcher: '^file_[a-z0-9]+$',
                  generate: 'file_001'
                }),
                name: like('report.pdf'),
                type: term({
                  matcher: '^(code|document|data|image|other)$',
                  generate: 'document'
                }),
                mime_type: like('application/pdf'),
                size: like(1024576),
                url: term({
                  matcher: '^https?://.*',
                  generate: 'https://storage.example.com/file_001'
                }),
                created_at: like('2024-01-01T12:00:00Z')
              }),
              pagination: {
                page: 1,
                limit: 20,
                total: like(50),
                total_pages: like(3),
                has_next: like(true),
                has_prev: like(false)
              }
            }
          }
        }
      })

      const response = await fileService.listFiles({
        page: 1,
        limit: 20,
        session_id: 'sess_123456'
      })

      expect(response.data.items).toBeDefined()
      expect(response.data.pagination).toBeDefined()
    })
  })

  describe('GET /files/{id}/preview', () => {
    it('should return file preview content', async () => {
      await provider.addInteraction({
        state: 'file exists',
        uponReceiving: 'a request for file preview',
        withRequest: {
          method: 'GET',
          path: '/api/v1/files/file_001/preview',
          headers: {
            'Authorization': like('Bearer token123')
          }
        },
        willRespondWith: {
          status: 200,
          body: {
            success: true,
            data: {
              content: like('# Markdown Preview\n\nThis is the file content...'),
              preview_type: term({
                matcher: '^(text|code|markdown|table|image)$',
                generate: 'markdown'
              }),
              language: like('markdown'),
              line_count: like(100),
              truncated: like(false)
            }
          }
        }
      })

      const preview = await fileService.getFilePreview('file_001')
      expect(preview.data.preview_type).toBeDefined()
      expect(preview.data.content).toBeDefined()
    })
  })
})
```

## 4. Provider端契约验证（后端）

### 4.1 Python环境配置

```bash
# 安装依赖
pip install pact-python pytest pytest-asyncio

# 项目结构
tests/
├── contracts/
│   ├── conftest.py          # Pytest配置
│   ├── provider/            # Provider验证测试
│   │   ├── test_auth_contract.py
│   │   ├── test_chat_contract.py
│   │   └── test_files_contract.py
│   └── pacts/              # 从Broker下载的契约
```

### 4.2 Provider验证配置

```python
# tests/contracts/conftest.py
import pytest
from pact import Verifier
import os
from app import create_app
from app.database import init_test_db

@pytest.fixture(scope='session')
def app():
    """创建测试应用实例"""
    app = create_app('testing')
    init_test_db()
    return app

@pytest.fixture(scope='session')
def verifier():
    """配置Pact Verifier"""
    return Verifier(
        provider='TradeFlow-Backend',
        broker_url=os.getenv('PACT_BROKER_URL', 'http://localhost:9292'),
        broker_token=os.getenv('PACT_BROKER_TOKEN'),
        publish_verification_results=True,
        provider_version=os.getenv('GIT_COMMIT', '1.0.0')
    )

@pytest.fixture
def provider_states():
    """定义Provider状态"""
    return {
        'user has valid OAuth code': setup_valid_oauth_code,
        'user has invalid OAuth code': setup_invalid_oauth_code,
        'agent is available': setup_agent_available,
        'user has files': setup_user_files,
        'file exists': setup_file_exists
    }

def setup_valid_oauth_code():
    """设置有效的OAuth码状态"""
    # 在测试数据库中创建临时OAuth码
    from app.models import OAuthCode
    OAuthCode.create(
        code='test-auth-code-123',
        provider='google',
        user_data={'email': 'user@example.com'},
        expires_at=datetime.now() + timedelta(minutes=10)
    )

def setup_user_files():
    """设置用户文件状态"""
    from app.models import File, User
    user = User.get_or_create(id='usr_123456')
    File.create_batch([
        {
            'id': 'file_001',
            'name': 'report.pdf',
            'type': 'document',
            'user_id': user.id,
            'session_id': 'sess_123456'
        }
    ])
```

### 4.3 Provider验证测试

```python
# tests/contracts/provider/test_auth_contract.py
import pytest
from pact import Verifier
from unittest.mock import patch, MagicMock

class TestAuthContract:
    """认证API契约验证"""
    
    @pytest.mark.contract
    def test_verify_auth_contract(self, verifier, app, provider_states):
        """验证认证相关的契约"""
        
        # 配置状态处理器
        verifier.set_state_handler(provider_states)
        
        # 验证契约
        output, logs = verifier.verify_pacts(
            provider_base_url=f"http://localhost:{app.config['PORT']}",
            pact_urls=['./tests/contracts/pacts/tradeflow-frontend-tradeflow-backend.json'],
            verbose=True,
            provider_states_setup_url=f"http://localhost:{app.config['PORT']}/_pact/provider_states"
        )
        
        assert output == 0, f"Contract verification failed:\n{logs}"

    @pytest.mark.contract
    async def test_oauth_callback_implementation(self, app):
        """测试OAuth回调的实际实现"""
        from app.services.auth import AuthService
        
        # Mock外部OAuth服务
        with patch('app.services.auth.google_oauth') as mock_oauth:
            mock_oauth.exchange_code.return_value = {
                'access_token': 'google-token',
                'user_info': {
                    'email': 'user@example.com',
                    'name': 'Test User',
                    'picture': 'https://example.com/avatar.jpg'
                }
            }
            
            # 执行实际的服务逻辑
            service = AuthService()
            result = await service.handle_oauth_callback(
                provider='google',
                code='test-auth-code-123',
                state='random-state'
            )
            
            # 验证响应格式符合契约
            assert result['success'] is True
            assert 'access_token' in result['data']
            assert result['data']['user']['email'] == 'user@example.com'
            assert result['data']['user']['auth_provider'] == 'google'
```

```python
# tests/contracts/provider/test_chat_contract.py
import pytest
from pact import Verifier
import asyncio
from unittest.mock import patch, AsyncMock

class TestChatContract:
    """对话API契约验证"""
    
    @pytest.mark.contract
    def test_verify_chat_contract(self, verifier, app, provider_states):
        """验证对话相关的契约"""
        
        verifier.set_state_handler(provider_states)
        
        output, logs = verifier.verify_pacts(
            provider_base_url=f"http://localhost:{app.config['PORT']}",
            pact_urls=['./tests/contracts/pacts/tradeflow-frontend-tradeflow-backend.json'],
            verbose=True
        )
        
        assert output == 0

    @pytest.mark.contract
    async def test_chat_with_buyer_agent(self, app):
        """测试买家Agent对话实现"""
        from app.services.chat import ChatService
        from app.agents.buyer_agent import BuyerAgent
        
        # Mock Agent响应
        with patch.object(BuyerAgent, 'process') as mock_process:
            mock_process.return_value = {
                'content': '根据您的需求，我为您找到了5家美国LED灯具买家',
                'recommendations': [
                    {
                        'id': 'buyer_001',
                        'company_name': 'Bright Lighting Inc.',
                        'country': 'US',
                        'match_score': 0.92
                    }
                ],
                'files': [
                    {
                        'id': 'file_001',
                        'name': 'buyer_list.csv',
                        'type': 'data'
                    }
                ]
            }
            
            service = ChatService()
            result = await service.create_chat(
                message='我需要找美国的LED灯具买家',
                agent_type='buyer',
                session_id='sess_123456',
                user_id='usr_123456'
            )
            
            # 验证响应结构
            assert result['success'] is True
            assert result['data']['response']['agent_type'] == 'buyer'
            assert len(result['data']['response']['recommendations']) > 0
            assert 'files' in result['data']['response']

    @pytest.mark.contract
    async def test_sse_stream_implementation(self, app):
        """测试SSE流式响应实现"""
        from app.services.stream import StreamService
        
        service = StreamService()
        
        # 创建SSE生成器
        async def stream_generator():
            yield 'event: connected\n'
            yield f'data: {{"session_id": "sess_123456", "agent_ready": true}}\n\n'
            
            message = '根据您的需求，我为您找到了买家'
            for char in message:
                yield 'event: stream\n'
                yield f'data: {{"chunk": "{char}"}}\n\n'
                await asyncio.sleep(0.01)
            
            yield 'event: complete\n'
            yield f'data: {{"session_id": "sess_123456"}}\n\n'
        
        # 验证SSE格式
        chunks = []
        async for chunk in stream_generator():
            chunks.append(chunk)
        
        assert any('event: connected' in chunk for chunk in chunks)
        assert any('event: stream' in chunk for chunk in chunks)
        assert any('event: complete' in chunk for chunk in chunks)
```

## 5. 契约发布与管理

### 5.1 Pact Broker配置

```yaml
# docker-compose.yml
services:
  pact-broker:
    image: pactfoundation/pact-broker:latest
    ports:
      - "9292:9292"
    environment:
      PACT_BROKER_DATABASE_URL: postgresql://pact:pact@postgres/pact
      PACT_BROKER_BASIC_AUTH_USERNAME: admin
      PACT_BROKER_BASIC_AUTH_PASSWORD: changeme
      PACT_BROKER_WEBHOOK_HOST: http://localhost:9292
    depends_on:
      - postgres

  postgres:
    image: postgres:13
    environment:
      POSTGRES_USER: pact
      POSTGRES_PASSWORD: pact
      POSTGRES_DB: pact
    volumes:
      - pact-postgres:/var/lib/postgresql/data

volumes:
  pact-postgres:
```

### 5.2 契约发布脚本

```javascript
// scripts/publish-pacts.js
const pact = require('@pact-foundation/pact-node')
const path = require('path')

const publishOptions = {
  pactFilesOrDirs: [path.resolve(process.cwd(), 'src/contracts/pacts')],
  pactBroker: process.env.PACT_BROKER_URL || 'http://localhost:9292',
  pactBrokerToken: process.env.PACT_BROKER_TOKEN,
  consumerVersion: process.env.GIT_COMMIT || require('../package.json').version,
  tags: [process.env.GIT_BRANCH || 'main']
}

pact.publishPacts(publishOptions)
  .then(() => {
    console.log('✅ Pacts published successfully')
    process.exit(0)
  })
  .catch(error => {
    console.error('❌ Failed to publish pacts:', error)
    process.exit(1)
  })
```

```python
# scripts/verify_pacts.py
import os
import sys
from pact import Verifier

def verify_pacts():
    """从Broker验证契约"""
    verifier = Verifier(
        provider='TradeFlow-Backend',
        broker_url=os.getenv('PACT_BROKER_URL', 'http://localhost:9292'),
        broker_token=os.getenv('PACT_BROKER_TOKEN'),
        provider_version=os.getenv('GIT_COMMIT', '1.0.0'),
        publish_verification_results=True
    )
    
    # 验证最新的契约
    success = verifier.verify_with_broker(
        enable_pending=True,
        include_wip_pacts_since='2024-01-01'
    )
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(verify_pacts())
```

## 6. CI/CD集成

### 6.1 GitHub Actions工作流

```yaml
# .github/workflows/contract-tests.yml
name: Contract Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  consumer-tests:
    name: Consumer Contract Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run consumer tests
        run: npm run test:contracts
      
      - name: Publish contracts
        if: github.ref == 'refs/heads/main'
        env:
          PACT_BROKER_URL: ${{ secrets.PACT_BROKER_URL }}
          PACT_BROKER_TOKEN: ${{ secrets.PACT_BROKER_TOKEN }}
          GIT_COMMIT: ${{ github.sha }}
          GIT_BRANCH: ${{ github.ref_name }}
        run: npm run pact:publish

  provider-tests:
    name: Provider Contract Tests
    runs-on: ubuntu-latest
    needs: consumer-tests
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      
      - name: Start test server
        run: |
          python -m app.server --test-mode &
          sleep 5
      
      - name: Verify contracts
        env:
          PACT_BROKER_URL: ${{ secrets.PACT_BROKER_URL }}
          PACT_BROKER_TOKEN: ${{ secrets.PACT_BROKER_TOKEN }}
          GIT_COMMIT: ${{ github.sha }}
        run: python scripts/verify_pacts.py
      
      - name: Can I Deploy?
        if: github.ref == 'refs/heads/main'
        run: |
          npx @pact-foundation/pact-node can-i-deploy \
            --pacticipant TradeFlow-Frontend \
            --version ${{ github.sha }} \
            --to production \
            --broker-base-url ${{ secrets.PACT_BROKER_URL }} \
            --broker-token ${{ secrets.PACT_BROKER_TOKEN }}
```

### 6.2 本地开发工作流

```bash
# package.json scripts
{
  "scripts": {
    "test:contracts": "jest --testMatch='**/*.pact.js'",
    "pact:publish": "node scripts/publish-pacts.js",
    "pact:verify": "python scripts/verify_pacts.py",
    "pact:can-deploy": "pact-broker can-i-deploy --pacticipant TradeFlow-Frontend --latest"
  }
}
```

## 7. 契约版本管理

### 7.1 版本策略

```javascript
// 版本生成策略
const getVersion = () => {
  const gitCommit = process.env.GIT_COMMIT
  const gitBranch = process.env.GIT_BRANCH
  const timestamp = new Date().toISOString()
  
  if (gitCommit) {
    return gitCommit.substring(0, 7)
  }
  
  if (gitBranch === 'main') {
    return require('./package.json').version
  }
  
  return `dev-${timestamp}`
}
```

### 7.2 契约矩阵

| Consumer版本 | Provider版本 | 状态 | 环境 |
|-------------|-------------|------|------|
| 1.0.0 | 1.0.0 | ✅ Verified | production |
| 1.0.1 | 1.0.0 | ✅ Verified | staging |
| 1.1.0-beta | 1.0.0 | ⚠️ Pending | development |
| 1.1.0-beta | 1.1.0-beta | ✅ Verified | development |

## 8. 契约测试最佳实践

### 8.1 测试原则

1. **Consumer驱动**: 契约由Consumer定义，Provider验证
2. **独立性**: 契约测试不依赖外部服务
3. **确定性**: 使用固定的测试数据和状态
4. **版本化**: 每个契约都有明确的版本
5. **自动化**: 契约测试集成到CI/CD流程

### 8.2 常见模式

```javascript
// 1. 使用Matcher而非硬编码值
❌ body: { id: 'usr_123456' }
✅ body: { id: term({ matcher: '^usr_[a-z0-9]+$', generate: 'usr_123456' }) }

// 2. 灵活的数组匹配
❌ items: [{ name: 'Item1' }, { name: 'Item2' }]
✅ items: eachLike({ name: like('Item1') }, { min: 1 })

// 3. 可选字段处理
const response = {
  required_field: like('value'),
  optional_field: like('optional')  // 使用like表示可选
}

// 4. 状态管理
state: 'user exists and has active session'  // 明确的状态描述
```

### 8.3 故障排除

| 问题 | 原因 | 解决方案 |
|-----|------|---------|
| 契约验证失败 | 请求格式不匹配 | 检查Matcher配置 |
| 状态设置失败 | Provider状态未实现 | 实现对应的状态处理器 |
| Broker连接失败 | 认证问题 | 检查Token和URL配置 |
| 版本冲突 | 多分支并行开发 | 使用特性分支标签 |

## 9. 监控和报告

### 9.1 契约覆盖率

```javascript
// 契约覆盖率检查
const checkCoverage = async () => {
  const openApiSpec = await loadOpenApiSpec()
  const pactFiles = await loadPactFiles()
  
  const coverage = {
    total: countEndpoints(openApiSpec),
    covered: countCoveredEndpoints(pactFiles),
    missing: []
  }
  
  // 找出未覆盖的端点
  for (const endpoint of openApiSpec.paths) {
    if (!isEndpointCovered(endpoint, pactFiles)) {
      coverage.missing.push(endpoint)
    }
  }
  
  coverage.percentage = (coverage.covered / coverage.total) * 100
  
  return coverage
}
```

### 9.2 契约健康度仪表板

```python
# 契约健康度监控
from pact_broker import Client

def generate_health_report():
    """生成契约健康度报告"""
    client = Client(broker_url=PACT_BROKER_URL)
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'contracts': [],
        'issues': []
    }
    
    # 检查所有契约
    for pact in client.get_all_pacts():
        status = client.get_verification_status(pact)
        
        contract_health = {
            'consumer': pact.consumer,
            'provider': pact.provider,
            'version': pact.version,
            'verified': status.verified,
            'last_verified': status.last_verified_at,
            'verification_count': status.verification_count
        }
        
        # 检查问题
        if not status.verified:
            report['issues'].append({
                'type': 'unverified',
                'contract': f"{pact.consumer}-{pact.provider}",
                'message': '契约未验证'
            })
        
        if days_since(status.last_verified_at) > 7:
            report['issues'].append({
                'type': 'stale',
                'contract': f"{pact.consumer}-{pact.provider}",
                'message': '契约验证已过期'
            })
        
        report['contracts'].append(contract_health)
    
    return report
```

## 10. 契约演进策略

### 10.1 向后兼容性

```javascript
// 添加新字段（向后兼容）
const v1Response = {
  id: like('123'),
  name: like('Product')
}

const v2Response = {
  ...v1Response,
  description: like('Product description')  // 新增可选字段
}

// 字段重命名（需要版本过渡）
// v1: { product_name: 'LED Light' }
// v1.5: { product_name: 'LED Light', name: 'LED Light' }  // 同时支持
// v2: { name: 'LED Light' }  // 移除旧字段
```

### 10.2 破坏性变更处理

```python
# 使用版本化端点
@app.route('/api/v1/products')  # 旧版本
def get_products_v1():
    return old_format_response()

@app.route('/api/v2/products')  # 新版本
def get_products_v2():
    return new_format_response()

# 或使用请求头版本控制
@app.route('/api/products')
def get_products():
    version = request.headers.get('API-Version', 'v1')
    if version == 'v2':
        return new_format_response()
    return old_format_response()
```

## 11. 参考资源

- [Pact官方文档](https://docs.pact.io/)
- [Pact JS使用指南](https://github.com/pact-foundation/pact-js)
- [Pact Python文档](https://github.com/pact-foundation/pact-python)
- [契约测试最佳实践](https://martinfowler.com/articles/consumerDrivenContracts.html)
- [Pact Broker API文档](https://github.com/pact-foundation/pact_broker)

---

**维护团队**: TradeFlow开发团队  
**最后更新**: 2025-01-07  
**反馈邮箱**: dev@tradeflow.com