#!/usr/bin/env python3
"""
代码执行工具演示脚本

展示如何使用代码执行工具进行贸易数据分析
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from trade_flow.tools.code_execution_tool import code_execution_tool
from trade_flow.tools.artifacts_manager import save_trade_data_artifact


async def demo_basic_execution():
    """演示基础代码执行"""
    print("=== 演示1: 基础Python代码执行 ===")
    
    code = """
import pandas as pd
import numpy as np

# 基础数学计算
result = 2 + 2
print(f"2 + 2 = {result}")

# 使用numpy
arr = np.array([1, 2, 3, 4, 5])
print(f"数组: {arr}")
print(f"数组平均值: {arr.mean()}")

# 创建简单的DataFrame
df = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35],
    'city': ['New York', 'London', 'Tokyo']
})
print("\\n创建的DataFrame:")
print(df)
print(f"\\n平均年龄: {df['age'].mean()}")
"""
    
    result = await code_execution_tool(code=code, timeout_seconds=15)
    
    if result["success"]:
        print("✅ 代码执行成功!")
        print("输出结果:")
        print(result["stdout"])
    else:
        print("❌ 代码执行失败:")
        print(result["error"])
    
    print(f"执行时间: {result['execution_time']:.3f}秒\n")


async def demo_trade_data_analysis():
    """演示贸易数据分析"""
    print("=== 演示2: 贸易数据分析 ===")
    
    # 模拟贸易数据
    sample_data = [
        {
            "id": "trade_001",
            "date": "2023-06-15",
            "importer": "GLOBAL ELECTRONICS INC",
            "exporter": "SHENZHEN TECH CO",
            "goodsDesc": ["SMARTPHONES", "TABLETS"],
            "hsCode": ["851712", "851730"],
            "countryOfOrigin": "China",
            "countryOfDestination": "USA",
            "quantity": 100,
            "sumOfUSD": 15000.00,
            "unitPrice": 150.00
        },
        {
            "id": "trade_002", 
            "date": "2023-06-20",
            "importer": "EUROPE IMPORTS LTD",
            "exporter": "GUANGZHOU ELECTRONICS",
            "goodsDesc": ["COMPUTER COMPONENTS"],
            "hsCode": ["847330"],
            "countryOfOrigin": "China", 
            "countryOfDestination": "Germany",
            "quantity": 200,
            "sumOfUSD": 8000.00,
            "unitPrice": 40.00
        },
        {
            "id": "trade_003",
            "date": "2023-06-25",
            "importer": "GLOBAL ELECTRONICS INC",  # 重复客户
            "exporter": "BEIJING TECH EXPORTS",
            "goodsDesc": ["ELECTRONIC ACCESSORIES"],
            "hsCode": ["851890"],
            "countryOfOrigin": "China",
            "countryOfDestination": "USA",
            "quantity": 150,
            "sumOfUSD": 4500.00,
            "unitPrice": 30.00
        }
    ]
    
    # 保存数据到Artifacts
    print("保存贸易数据到 Artifacts...")
    artifact_result = await save_trade_data_artifact(
        trade_records=sample_data,
        query_params={"product_desc": "electronics", "start_date": "2023-06-01", "end_date": "2023-06-30"},
        context=None
    )
    
    if not artifact_result["success"]:
        print(f"❌ 保存数据失败: {artifact_result['error']}")
        return
    
    artifact_id = artifact_result["artifact_id"]
    print(f"✅ 数据已保存到 Artifact: {artifact_id}")
    
    # 分析代码
    analysis_code = f"""
# 加载贸易数据
df = load_trade_data('{artifact_id}')

print("=== 贸易数据分析报告 ===")
print(f"数据概览: {{len(df)}} 条贸易记录")
print(f"数据字段: {{len(df.columns)}} 个字段")
print(f"时间范围: {{df['date'].min()}} 至 {{df['date'].max()}}")

# 基础统计
total_value = df['sumOfUSD'].sum()
avg_value = df['sumOfUSD'].mean()
total_quantity = df['quantity'].sum()

print(f"\\n=== 交易统计 ===")
print(f"总交易额: ${{total_value:,.2f}}")
print(f"平均交易额: ${{avg_value:,.2f}}")
print(f"总交易数量: {{total_quantity:,}} 件")

# 进口商分析
print(f"\\n=== 进口商分析 ===")
top_importers = df.groupby('importer')['sumOfUSD'].agg(['sum', 'count']).sort_values('sum', ascending=False)
for importer, data in top_importers.iterrows():
    print(f"{{importer}}: ${{data['sum']:,.2f}} ({{data['count']}} 次交易)")

# 出口商分析
print(f"\\n=== 出口商分析 ===")
top_exporters = df.groupby('exporter')['sumOfUSD'].sum().sort_values(ascending=False)
for exporter, total in top_exporters.items():
    print(f"{{exporter}}: ${{total:,.2f}}")

# 产品分析
print(f"\\n=== 产品分析 ===")
if 'goodsDesc' in df.columns:
    for idx, row in df.iterrows():
        goods = row['goodsDesc']
        value = row['sumOfUSD']
        print(f"{{goods}}: ${{value:,.2f}}")

# 单价分析
print(f"\\n=== 单价分析 ===")
print(f"最高单价: ${{df['unitPrice'].max():.2f}}")
print(f"最低单价: ${{df['unitPrice'].min():.2f}}")
print(f"平均单价: ${{df['unitPrice'].mean():.2f}}")

print(f"\\n✅ 分析完成! 数据已成功处理")
"""
    
    # 执行分析
    print("\n执行贸易数据分析...")
    result = await code_execution_tool(
        code=analysis_code,
        timeout_seconds=20,
        artifacts_access=[artifact_id]
    )
    
    if result["success"]:
        print("✅ 贸易数据分析成功!")
        print("\n分析结果:")
        print(result["stdout"])
    else:
        print("❌ 分析失败:")
        print(result["error"])
        if result["stderr"]:
            print("错误详情:")
            print(result["stderr"])
    
    print(f"执行时间: {result['execution_time']:.3f}秒\n")


async def demo_error_handling():
    """演示错误处理"""
    print("=== 演示3: 错误处理 ===")
    
    # 包含错误的代码
    error_code = """
# 正常代码
print("开始执行...")
result = 10 / 2
print(f"10 / 2 = {result}")

# 故意引发错误
try:
    error_result = 10 / 0  # 除零错误
except ZeroDivisionError as e:
    print(f"捕获到预期错误: {e}")

# 继续执行
print("错误已处理，继续执行...")
final_result = 5 * 6
print(f"5 * 6 = {final_result}")
print("执行完成!")
"""
    
    result = await code_execution_tool(code=error_code, timeout_seconds=10)
    
    if result["success"]:
        print("✅ 错误处理演示成功!")
        print("输出结果:")
        print(result["stdout"])
    else:
        print("❌ 执行失败:")
        print(result["error"])
    
    print(f"执行时间: {result['execution_time']:.3f}秒\n")


async def demo_security_validation():
    """演示安全验证"""
    print("=== 演示4: 安全验证 ===")
    
    # 危险代码示例
    dangerous_code = """
import os
os.system('ls -la')  # 尝试执行系统命令
"""
    
    result = await code_execution_tool(code=dangerous_code, timeout_seconds=5)
    
    if result["success"]:
        print("⚠️ 危险代码意外通过了验证!")
        print(result["stdout"])
    else:
        print("✅ 危险代码被成功阻止!")
        print(f"错误信息: {result['error']}")
    
    print(f"执行时间: {result['execution_time']:.3f}秒\n")


async def main():
    """主演示函数"""
    print("🚀 代码执行工具演示")
    print("=" * 50)
    
    try:
        await demo_basic_execution()
        await demo_trade_data_analysis()
        await demo_error_handling()
        await demo_security_validation()
        
        print("🎉 所有演示完成!")
        
    except Exception as e:
        print(f"❌ 演示过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())