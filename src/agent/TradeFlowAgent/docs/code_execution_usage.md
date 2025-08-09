# 智能体中使用代码执行工具

## 工具概述

代码执行工具 (`code_execution_tool`) 允许智能体生成并执行 Python 代码，特别适用于贸易数据的深度分析。

## 工具注册

在智能体配置中，代码执行工具已经被注册：

```python
# trade_flow/agents/trade_agent.py
from ..tools import (
    code_execution_tool, read_trade_data_artifact_tool, list_trade_data_artifacts_tool
)

# 在 Agent 配置中
tools=[
    get_trade_data_tool, get_trade_data_count_tool, 
    code_execution_tool,  # 代码执行工具
    read_trade_data_artifact_tool,  # 读取 Artifacts
    list_trade_data_artifacts_tool   # 列出 Artifacts
]
```

## 使用流程

### 1. 典型工作流程

```
用户查询 → 智能体查询贸易数据 → 数据自动保存到 Artifacts → 智能体生成分析代码 → 执行代码 → 返回分析结果
```

### 2. 智能体调用示例

智能体可以这样使用代码执行工具：

#### Step 1: 查询贸易数据
```python
# 智能体首先查询贸易数据
result = await get_trade_data_tool(
    product_desc="electronic components",
    start_date="2023-01-01", 
    end_date="2023-12-31"
)

# 数据自动保存到 Artifacts，获取 artifact_id
artifact_id = result["artifact_info"]["artifact_id"]  # 如: "temp_trade_data_electronics_20231201_143022.csv"
```

#### Step 2: 执行数据分析代码
```python
# 智能体生成并执行分析代码
analysis_code = f"""
# 加载贸易数据
df = load_trade_data('{artifact_id}')

# 生成基础摘要报告
report = generate_summary_report(df)
print("=== 贸易数据摘要 ===")
for key, value in report.items():
    print(f"{key}: {value}")

# 分析最活跃的进口商
print("\\n=== 最活跃进口商 TOP 5 ===")
top_importers_df = top_importers(df, top_n=5)
print(top_importers_df.to_string(index=False))

# 分析最活跃的出口商
print("\\n=== 最活跃出口商 TOP 5 ===")
top_exporters_df = top_exporters(df, top_n=5)  
print(top_exporters_df.to_string(index=False))

# 分析贸易趋势（月度）
print("\\n=== 月度贸易趋势 ===")
trends = analyze_trade_trends(df, period='month')
print(trends.to_string(index=False))
"""

# 执行代码
exec_result = await code_execution_tool(
    code=analysis_code,
    timeout_seconds=30,
    artifacts_access=[artifact_id]  # 允许访问的 Artifacts
)

if exec_result["success"]:
    analysis_output = exec_result["stdout"]
    # 智能体使用分析结果回答用户
    return f"数据分析完成！\\n\\n{analysis_output}"
```

## 预定义函数

智能体可以在代码中使用这些预定义函数：

### 数据加载函数
```python
# 从 Artifact 加载贸易数据
df = load_trade_data(artifact_id)  # 返回 pandas DataFrame
```

### 分析函数
```python
# 生成摘要报告
report = generate_summary_report(df)

# 分析贸易趋势
trends = analyze_trade_trends(df, period='month')  # 'day', 'month', 'quarter', 'year'

# 最活跃进口商
top_imp = top_importers(df, top_n=10)

# 最活跃出口商  
top_exp = top_exporters(df, top_n=10)

# 按国家分析贸易量
countries = trade_volume_by_country(df, country_type='destination')  # 'origin' 或 'destination'

# 产品类别分析
products = analyze_product_categories(df, top_n=15)

# 计算贸易指标
metrics = calculate_trade_metrics(df)
```

### 可视化函数
```python
# 生成时间趋势图代码
plot_code = plot_trade_timeline(df, group_by='month')
exec(plot_code)  # 执行绘图代码

# 生成热门产品图代码
plot_code = plot_top_products(df, top_n=10)
exec(plot_code)  # 执行绘图代码
```

## 实际应用场景

### 场景1: 基础数据分析
```python
# 用户询问: "分析2023年电子产品的贸易情况"

# 智能体执行流程:
# 1. 查询贸易数据
result = await get_trade_data_tool(
    product_desc="electronic products",
    start_date="2023-01-01",
    end_date="2023-12-31"
)

# 2. 执行分析代码
code = f"""
df = load_trade_data('{result["artifact_info"]["artifact_id"]}')
report = generate_summary_report(df)
top_imp = top_importers(df, top_n=3)
trends = analyze_trade_trends(df, period='quarter')

print("电子产品贸易分析报告")
print("=" * 30)
for key, value in report.items():
    print(f"{key}: {value}")

print("\\n主要进口商:")
print(top_imp.to_string(index=False))

print("\\n季度趋势:")
print(trends.to_string(index=False))
"""

exec_result = await code_execution_tool(code=code, artifacts_access=[artifact_id])
```

### 场景2: 复杂数据对比分析
```python
# 用户询问: "对比中国和印度的纺织品出口情况"

# 智能体可以查询两个数据集，然后用代码对比分析
code = """
# 加载两个数据集
china_df = load_trade_data('china_textile_data.csv')
india_df = load_trade_data('india_textile_data.csv')

# 对比分析
china_total = china_df['sumOfUSD'].sum()
india_total = india_df['sumOfUSD'].sum()

print(f"中国纺织品出口总额: ${china_total:,.2f}")
print(f"印度纺织品出口总额: ${india_total:,.2f}")
print(f"中国领先优势: {((china_total - india_total) / india_total * 100):.1f}%")

# 主要目的国对比
china_destinations = china_df.groupby('countryOfDestination')['sumOfUSD'].sum().head(5)
india_destinations = india_df.groupby('countryOfDestination')['sumOfUSD'].sum().head(5)

print("\\n中国主要出口目的国:")
print(china_destinations.to_string())

print("\\n印度主要出口目的国:")  
print(india_destinations.to_string())
"""
```

### 场景3: 时间序列分析
```python
# 用户询问: "分析某公司过去一年的进口趋势"

code = f"""
df = load_trade_data('{artifact_id}')

# 筛选特定公司
company_data = df[df['importer'].str.contains('SPECIFIC COMPANY', na=False)]

if len(company_data) > 0:
    # 月度趋势分析
    monthly_trends = analyze_trade_trends(company_data, period='month')
    
    print(f"公司进口分析 - 共 {{len(company_data)}} 条记录")
    print("月度进口趋势:")
    print(monthly_trends.to_string(index=False))
    
    # 供应商分析
    suppliers = company_data.groupby('exporter')['sumOfUSD'].sum().sort_values(ascending=False)
    print("\\n主要供应商:")
    for supplier, amount in suppliers.head(5).items():
        print(f"{{supplier}}: ${{amount:,.2f}}")
else:
    print("未找到该公司的进口记录")
"""
```

## 错误处理

智能体应该处理代码执行中的错误：

```python
exec_result = await code_execution_tool(code=analysis_code, artifacts_access=[artifact_id])

if exec_result["success"]:
    # 成功执行
    return f"分析完成:\\n{exec_result['stdout']}"
else:
    # 执行失败
    error_msg = exec_result["error"]
    if "timeout" in exec_result["status"]:
        return "分析超时，请尝试简化分析内容"
    elif "security" in exec_result["status"]:
        return "代码包含不安全内容，已被阻止执行"
    else:
        return f"分析过程中出现错误: {error_msg}"
```

## 安全限制

代码执行工具有以下安全限制：
- 禁止导入危险模块 (os, sys, subprocess 等)
- 禁止执行危险函数 (exec, eval, open 等)
- 30秒执行超时限制
- 5MB 输出大小限制
- 无网络和文件系统访问

## 最佳实践

1. **先查询后分析**: 总是先用 `get_trade_data_tool` 查询数据，再用代码分析
2. **利用预定义函数**: 使用 `load_trade_data()`, `generate_summary_report()` 等函数提高效率
3. **错误处理**: 始终检查 `exec_result["success"]` 并处理错误情况
4. **合理超时**: 复杂分析可能需要更长时间，适当设置 `timeout_seconds`
5. **清晰输出**: 在代码中使用清晰的 print 语句格式化输出结果