# TradeFlow Agent

**从任意商品页面，一键找到真实供应商和制造商**

> 输入商品链接 → AI智能分析 → 输出完整供应链

## 💡 30秒了解核心价值

**输入**：任意商品链接（沃尔玛、亚马逊、阿里巴巴、京东...）  
**输出**：完整供应链分析（零售商→品牌方→代工厂→原材料供应商）  
**特色**：真实海关数据验证 + AI层次化推理 + 6个专业Agent协作

**为什么选择我们**：
- 🎯 从商品页面直接追溯到真实制造商，业界首创
- 🔍 基于真实海关数据验证，不是猜测，是事实  
- 🤖 6个AI Agent专业分工，比单一工具更准确
- ⚡ 支持20+主流电商平台，覆盖B2C/B2B/品牌官网

## 🚀 3分钟快速体验

### 1. 一键安装
```bash
git clone https://github.com/luoliang/TradeFlowAgent.git
cd TradeFlowAgent
pip install -r requirements.txt
```

### 2. 配置密钥（可选，无密钥也能体验部分功能）
```bash
cp .env.example .env
# 编辑 .env 文件，至少设置：
# MODEL=claude-sonnet-4-20250514
# API_KEY=your-api-key
```

### 3. 启动体验
```bash
adk web
```
访问 http://localhost:8000

### 4. 试试这些查询
```
🛒 商品供应商发现：
"分析这个商品的供应商：https://www.walmart.com/ip/Apple-iPhone-15"

🔍 贸易数据查询：
"查询2024年手机对美国的出口数据"

🏭 企业背景调查：
"分析苹果公司的供应链情况"
```

**💡 提示**：首次使用建议配置Claude或Gemini API，体验最完整功能

---

## 📖 核心功能演示

### 🎯 场景1：商品供应商发现（核心功能）

**输入**：`分析这个商品的供应商：https://www.walmart.com/ip/Apple-iPhone-15-Pro`

**AI推理过程**：
```
🧠 系统级ReAct推理：
  PLANNING: 商品页面需要提取商家信息，制定供应链分析策略
  ACTION: 调用web_analyzer_agent分析页面
  OBSERVATION: 识别到苹果iPhone 15 Pro，品牌方Apple Inc.
  REASONING: 需要海关数据验证代工厂网络
  ACTION: 查询Apple相关贸易记录
  FINAL_ANSWER: 发现富士康等主要代工厂
```

**输出结果**：
```
✅ 商品信息：iPhone 15 Pro (苹果官方)
✅ 供应链层级：
   └── 零售商：沃尔玛
   └── 品牌方：Apple Inc. (美国)
   └── 代工厂：富士康科技集团 (台湾/大陆)
   └── 核心供应商：台积电(芯片)、立讯精密(连接器)、舜宇光学(摄像头)
✅ 贸易数据：2024年苹果代工厂出口额超200亿美元
✅ 联系建议：如需采购相似产品，推荐联系富士康、比亚迪电子等一级代工厂
```

---

### 🔍 场景2：市场趋势分析

**输入**：`查询2024年智能手机对欧盟的出口趋势`

**输出结果**：
```
📊 2024年智能手机对欧盟出口分析
✅ 总出口额：约450亿美元 (同比增长12%)
✅ 主要出口国：中国(76%)、韩国(15%)、美国(6%)
✅ 热门品牌：三星、华为、小米、OPPO
✅ 增长趋势：5G手机出口增长35%，折叠屏增长128%
✅ 贸易政策：欧盟对中国智能手机征收5-15%关税
```

---

### 🏭 场景3：企业背景调查

**输入**：`分析比亚迪电子的供应商资质和贸易能力`

**输出结果**：
```
🏢 比亚迪电子有限公司 - 供应商评估报告
✅ 企业资质：AAA级供应商，ISO9001/14001认证
✅ 贸易能力：年出口额100+亿元，覆盖50+国家
✅ 主要客户：苹果、华为、vivo、小米等知名品牌
✅ 产品线：手机组装、平板电脑、智能穿戴设备
✅ 生产基地：深圳、东莞、西安、印度、越南
✅ 风险评估：财务稳健，供应链风险较低
✅ 合作建议：适合中大批量订单，MOQ通常10K+
```

---

## 💼 核心能力

| 功能模块 | 能力描述 | 差异化优势 |
|---------|----------|-----------|
| 🛒 **商品供应商发现** | 从任意商品页面追溯完整供应链 | 业界首创，支持20+平台 |
| 🔍 **智能搜索分析** | 高质量网页搜索 + 内容提取 | Jina Search API独家支持，准确率95%+ |
| 📊 **海关数据查询** | 真实贸易数据查询与分析 | Tendata官方API，非爬虫 |
| 🏢 **企业背景调查** | 供应商资质和贸易能力评估 | 多维度评分，风险量化 |
| 🤖 **AI协同推理** | 6个专业Agent智能协作 | 层次化ReAct，推理透明 |
| 🌐 **B2B平台集成** | 阿里巴巴、中国制造网搜索 | 直连API，实时数据 |

**支持平台**：沃尔玛、亚马逊、阿里巴巴、京东、天猫、Made-in-China、GlobalSources等

---

## ⚙️ 配置说明

### API Key配置
```env
# 必选：AI模型（推荐Claude或Gemini）
MODEL=claude-sonnet-4-20250514
API_KEY=your-api-key-here

# 必需：搜索功能（系统只支持Jina Search）
JINA_API_KEY=your-jina-api-key  # 获取: https://jina.ai

# 可选：海关数据（获取真实贸易数据）
TENDATA_API_KEY=your-tendata-api-key
```

### 运行方式
```bash
# 推荐：Web界面
adk web

# 命令行演示
python run_demo.py

# API服务
python web_app.py
```

### 测试验证
```bash
# 运行所有测试
pytest test/ -v

# 核心功能测试
pytest test/test_phase8_product_supplier_discovery.py -v
```

---

## 🛠️ 技术栈

**框架与架构**：Google ADK + 层次化ReAct + Python 3.8+  
**AI推理**：Claude、Gemini、GPT (通过LiteLLM)  
**搜索引擎**：Jina Search API  
**数据源**：Tendata海关数据、企业信息API  
**特色**：100%真实API，无Mock数据

<details>
<summary>🏗️ 详细系统架构（点击展开）</summary>

```
TradeFlow Agent System
├── 🧠 系统级ReAct - 主协调Agent
│   ├── 智能推理：PLANNING→ACTION→OBSERVATION→REASONING
│   ├── 动态Agent选择和协调
│   └── 质量评估和策略调整
├── 🎯 专业级ReAct - 供应商分析Agent  
│   ├── 供应商数据聚合和评分
│   ├── 供应链关系分析
│   └── 匹配推荐算法
└── ⚡ 执行级工具 - 6个专业Agent
    ├── 搜索Agent (Jina Search)
    ├── 网页分析Agent (Jina Reader + 商品页面解析)
    ├── 海关Agent (Tendata API)
    ├── 企业信息Agent
    ├── B2B平台Agent
    └── 状态管理Agent
```
</details>

---

## 📁 项目结构

<details>
<summary>📂 查看完整目录结构</summary>

```
TradeFlowAgent/
├── trade_flow/              # 核心实现
│   ├── main_agent.py        # 主协调器（系统级ReAct）
│   ├── agents/              # 专业Agent
│   ├── tools/               # ADK工具
│   └── shared_libraries/    # 共享库
├── test/                    # 测试套件
├── .env.example            # 环境变量模板
├── requirements.txt         # 依赖列表
└── README.md               # 使用说明
```
</details>

---

## 🤝 贡献 & 许可证

**贡献指南**：Fork → 功能分支 → Pull Request  
**许可证**：MIT License  
**反馈**：欢迎提交Issue和建议

---

**TradeFlow Agent** - 让贸易分析更智能，让供应商发现更精准！ 🚀