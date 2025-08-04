# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

TradeFlow是一款面向全球的，基于对话式AI Agent的全球B2B贸易智能助手，通过自然语言交互帮助用户完成买家开发、供应商采购等贸易业务。

## 技术栈

- **数据库**: PostgreSQL, MongoDB
- **缓存**: Redis
- **后端**: FastAPI (Python)
- **前端**: React
- **支付**: Stripe
- **AI框架**: Google ADK (Agent Development Kit)

## 项目结构

```
TradeFlowProduct/
├── docs/               # 项目文档
├── src/
│   ├── backend/       # FastAPI后端服务
│   ├── agent/       # Google ADK 开发的 Agent
│   ├── frontend/      # React前端应用
│   └── interface_docs/ # 前后端接口文档
```

## 开发指南

### 后端开发 (FastAPI)
- 后端服务位于 `src/backend/`
- 使用FastAPI框架构建RESTful API
- 数据持久化使用PostgreSQL和MongoDB
- 缓存使用Redis

### 前端开发 (React)
- 前端应用位于 `src/frontend/`
- 使用React构建用户界面
- 与后端通过RESTful API通信

### AI Agent开发
- Agent 位于 `src/agent/`
- 使用Google ADK框架开发对话式AI功能
- Agent需要处理贸易相关的自然语言查询
- 支持买家开发和供应商采购场景

## 重要原则

1. **独立部署**: 前端和后端应能在各自根目录下独立启动
2. **接口文档**: 所有API接口需在 `src/interface_docs/` 中明确定义
3. **多语言支持**: 考虑国际贸易场景，需支持多语言交互
4. **数据安全**: 贸易数据敏感，确保适当的安全措施

## 注意事项

- 使用Stripe进行支付集成时，确保遵循PCI合规要求
- AI Agent的设计应考虑贸易领域的专业术语和流程
- 数据库设计需要考虑买家信息、供应商信息、交易记录等核心实体
- 每次根据对话执行完任务，只要涉及到文件改动，就进行 git 提交，但是不要推送