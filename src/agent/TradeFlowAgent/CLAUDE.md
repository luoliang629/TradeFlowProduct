# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在此代码库工作时提供指导。

## 项目概述

TradeFlowAgent 是一个基于 Google ADK (Agent Development Kit,也简称为 ADK) 的多智能体贸易信息查询系统，采用 ReAct（推理-行动）模式。系统通过专门的智能体处理贸易相关查询。

## 架构设计

系统采用层次化ReAct智能体架构：

### 🧠 系统级ReAct（智能协调层）
- **主协调 Agent**：使用PlanReActPlanner进行系统级推理，动态选择和协调子智能体，整合结果并提供综合决策

### 🎯 专业级ReAct（复杂决策层）  
- **供应商分析 Agent**：使用PlanReActPlanner进行专业级推理，多维评估、策略调整、迭代优化

### ⚡ 执行级工具（高效执行层）
- **搜索 Agent**：处理贸易信息的网页搜索查询
- **海关 Agent**：查询和分析进出口数据  
- **企业信息 Agent**：企业资质查询和背景调查
- **网页分析 Agent**：商品页面和企业网站深度分析
- **B2B平台 Agent**：B2B平台搜索和供应商发现

### 架构原则
- **精准ReAct**：只在需要复杂推理的层次使用ReAct（系统级协调 + 专业级分析）
- **高效执行**：工具Agent保持简洁高效，专注任务执行
- **智能协同**：系统级ReAct负责整体推理和Agent间协调

## 技术栈
- **框架**: Google Agent Development Kit (ADK)
- **语言**: Python 3.8+

## 开发命令

```bash
# 安装依赖
pip install -r requirements.txt

# 运行代码检查
flake8 trade_flow/

# 运行类型检查
mypy trade_flow/

# 格式化代码
black trade_flow/

# 运行测试
pytest

# 运行异步测试
pytest -v --asyncio-mode=auto

# 运行智能体系统（实现后）
python -m trade_flow.agent
```

## 配置说明

在项目根目录创建 `.env` 文件：
```
MODEL=gemini-2.0-flash
API_KEY=your-api-key-here
TEMPERATURE=0.7
JINA_API_KEY=your-jina-api-key
TENDATA_API_KEY=your-tendata-api-key
```

`trade_flow/shared_libraries/constants.py` 文件会自动加载这些环境变量。

## 实施进度
1. 完整计划参考`plan.md`
2. 在实施执行`plan.md`中的执行阶段时，按照执行动作，拆分到`current_proc.md`
3. 每完成`current_proc.md`中的一个小节，更新`current_proc.md`，并进行一次 git 提交
4. 当所有`current_proc`,更新`plan.md`
5. 开始新的阶段时，更新`current_proc.md`


## 关键实施准则

1. **真实API优先**：所有工具都应使用真实API，不再提供模拟实现
2. **默认异步**：除MCP工具外，所有工具处理器和智能体方法使用 `async def`
3. **类型提示**：全代码库使用 Python 类型提示
4. **工具结构**：除MCP工具外，工具遵循 Google ADK Tool 模式，包含 name、description、parameters 和 handler

## 测试策略

- 使用 pytest 和 pytest-asyncio 对工具进行单元测试
- 对智能体协作进行集成测试
- 测试场景见 plan.md（如"查询2023年纺织品出口数据"）
- 测试脚本统一放在`test`目录下
- 验证和demo代码统一放到test目录中
非常重要
每开发完一个阶段，使用`adk run`测试`main agent`进行验证

## 重要文件

- `plan.md`：包含代码示例的完整实施计划
- `trade_flow/config.py`：中央配置管理

## 工具开发原则

- MCP工具和其他工具都使用真实API，失败时给出友好提示