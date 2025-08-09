#!/usr/bin/env python3
"""
智能体使用代码执行工具的完整示例

展示智能体如何在贸易数据分析场景中使用代码执行工具
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trade_flow.tools.code_execution_tool import code_execution_tool
from trade_flow.tools.trade_data_query import get_trade_data_tool
from trade_flow.tools.artifacts_reader import list_trade_data_artifacts_tool


class MockAgent:
    """模拟智能体类，展示如何使用代码执行工具"""
    
    def __init__(self):
        self.name = "TradeAnalysisAgent"
    
    async def analyze_trade_data(self, query_params: dict) -> str:
        """
        模拟智能体分析贸易数据的完整流程
        
        Args:
            query_params: 查询参数字典
            
        Returns:
            分析结果字符串
        """
        print(f"🤖 [{self.name}] 开始分析贸易数据...")
        
        try:
            # Step 1: 查询贸易数据
            print("📊 正在查询贸易数据...")
            trade_result = await get_trade_data_tool(**query_params)
            
            if trade_result["status"] != "success":
                return f"❌ 数据查询失败: {trade_result.get('error_message', '未知错误')}"
            
            # 检查是否有数据保存到 Artifacts
            if "artifact_info" not in trade_result or not trade_result["artifact_info"].get("saved"):
                return "❌ 数据未成功保存到 Artifacts，无法进行代码分析"
            
            artifact_id = trade_result["artifact_info"]["artifact_id"]
            records_count = len(trade_result["trade_records"])
            
            print(f"✅ 查询成功! 获得 {records_count} 条贸易记录")
            print(f"📁 数据已保存到 Artifact: {artifact_id}")
            
            # Step 2: 生成分析代码
            analysis_code = self._generate_analysis_code(artifact_id, query_params)
            print("🔍 生成数据分析代码...")
            
            # Step 3: 执行代码分析
            print("⚡ 执行代码分析...")
            exec_result = await code_execution_tool(
                code=analysis_code,
                timeout_seconds=30,
                artifacts_access=[artifact_id]
            )
            
            # Step 4: 处理执行结果
            if exec_result["success"]:
                analysis_output = exec_result["stdout"]
                execution_time = exec_result["execution_time"]
                
                return f"""
🎉 **贸易数据分析完成!**

📈 **分析结果:**
```
{analysis_output}
```

⏱️ **执行信息:**
- 执行时间: {execution_time:.3f} 秒
- 处理记录: {records_count} 条
- 数据来源: {artifact_id}

---
*分析由 {self.name} 自动生成并执行*
"""
            else:
                error_info = exec_result["error"]
                return f"❌ 代码执行失败: {error_info}"
                
        except Exception as e:
            return f"❌ 分析过程中发生异常: {str(e)}"
    
    def _generate_analysis_code(self, artifact_id: str, query_params: dict) -> str:
        """
        生成针对性的分析代码
        
        Args:
            artifact_id: Artifact ID
            query_params: 查询参数
            
        Returns:
            Python 分析代码字符串
        """
        # 基础分析代码模板
        base_code = f"""
# 加载贸易数据
print("🔄 正在加载贸易数据...")
df = load_trade_data('{artifact_id}')
print(f"✅ 数据加载完成: {{len(df)}} 条记录, {{len(df.columns)}} 个字段")

print("\\n" + "="*50)
print("📊 贸易数据综合分析报告")  
print("="*50)

# 基础统计信息
print("\\n📋 基础统计信息:")
report = generate_summary_report(df)
for k, v in report.items():
    print(f"   {{k}}: {{v}}")
"""
        
        # 根据查询类型添加特定分析
        if query_params.get("product_desc"):
            product = query_params["product_desc"]
            base_code += f"""
print("\\n🏷️ 产品分析 - {product}:")
try:
    products = analyze_product_categories(df, top_n=8)
    if not products.empty:
        print("   主要产品类别及交易额:")
        for _, row in products.iterrows():
            print(f"   • {{row.iloc[0]}}: ${{row['总交易额']:,.2f}}")
    else:
        print("   未找到产品分类数据")
except Exception as e:
    print(f"   产品分析失败: {{e}}")
"""
        
        if query_params.get("exporter") or query_params.get("importer"):
            base_code += """
# 贸易伙伴分析
print("\\n🏢 贸易伙伴分析:")

# 最活跃进口商
try:
    top_imp = top_importers(df, top_n=5)
    if not top_imp.empty:
        print("   🔝 最活跃进口商 TOP 5:")
        for _, row in top_imp.iterrows():
            print(f"   • {row['importer']}: ${row['总交易额']:,.2f} ({row['交易次数']} 次)")
    else:
        print("   未找到进口商数据")
except Exception as e:
    print(f"   进口商分析失败: {e}")

# 最活跃出口商  
try:
    top_exp = top_exporters(df, top_n=5)
    if not top_exp.empty:
        print("   🔝 最活跃出口商 TOP 5:")
        for _, row in top_exp.iterrows():
            print(f"   • {row['exporter']}: ${row['总交易额']:,.2f} ({row['交易次数']} 次)")
    else:
        print("   未找到出口商数据")
except Exception as e:
    print(f"   出口商分析失败: {e}")
"""
        
        # 时间趋势分析
        if query_params.get("start_date") and query_params.get("end_date"):
            base_code += """
# 时间趋势分析
print("\\n📈 时间趋势分析:")
try:
    trends = analyze_trade_trends(df, period='month')
    if not trends.empty:
        print("   月度贸易趋势:")
        for _, row in trends.iterrows():
            period = row.iloc[0]  # period 列
            total = row['总额']
            count = row['交易次数'] 
            print(f"   • {period}: ${total:,.2f} ({count} 次交易)")
    else:
        print("   未找到趋势数据")
except Exception as e:
    print(f"   趋势分析失败: {e}")
"""
        
        # 地理分布分析
        base_code += """
# 地理分布分析
print("\\n🌍 地理分布分析:")
try:
    # 按目的国分析
    dest_countries = trade_volume_by_country(df, country_type='destination')
    if not dest_countries.empty:
        print("   🎯 主要目的国 TOP 5:")
        for _, row in dest_countries.head(5).iterrows():
            country = row.iloc[0]  # 国家列
            total = row['总交易额']
            print(f"   • {country}: ${total:,.2f}")
    
    # 按原产国分析
    origin_countries = trade_volume_by_country(df, country_type='origin')
    if not origin_countries.empty:
        print("   🏭 主要原产国 TOP 5:")
        for _, row in origin_countries.head(5).iterrows():
            country = row.iloc[0]  # 国家列
            total = row['总交易额']
            print(f"   • {country}: ${total:,.2f}")
            
except Exception as e:
    print(f"   地理分析失败: {e}")

# 贸易指标计算
print("\\n📊 高级贸易指标:")
try:
    metrics = calculate_trade_metrics(df)
    for metric_key, metric_value in metrics.items():
        if isinstance(metric_value, float):
            print(f"   {{metric_key}}: {{metric_value:.4f}}")
        else:
            print(f"   {{metric_key}}: {{metric_value}}")
except Exception as e:
    print(f"   指标计算失败: {e}")

print("\\n" + "="*50)
print("✨ 分析完成! 以上是基于实际贸易数据的综合分析结果")
print("="*50)
"""
        
        return base_code


async def demo_agent_workflow():
    """演示智能体工作流程"""
    print("🚀 智能体代码执行工具演示")
    print("=" * 60)
    
    # 创建模拟智能体
    agent = MockAgent()
    
    # 演示查询参数
    query_scenarios = [
        {
            "name": "电子产品贸易分析",
            "params": {
                "product_desc": "electronic components",
                "start_date": "2023-06-01", 
                "end_date": "2023-06-30",
                "origin_country": "China"
            }
        },
        {
            "name": "特定公司进出口分析", 
            "params": {
                "exporter": "SHENZHEN TECH CO",
                "start_date": "2023-01-01",
                "end_date": "2023-12-31"
            }
        }
    ]
    
    for i, scenario in enumerate(query_scenarios, 1):
        print(f"\n🎯 场景 {i}: {scenario['name']}")
        print("-" * 40)
        
        # 智能体分析数据
        result = await agent.analyze_trade_data(scenario["params"])
        print(result)
        
        if i < len(query_scenarios):
            print("\n⏸️ 暂停 3 秒...")
            await asyncio.sleep(3)
    
    # 列出所有可用的 Artifacts
    print("\n📁 当前可用的数据 Artifacts:")
    artifacts_result = await list_trade_data_artifacts_tool()
    if artifacts_result["success"] and artifacts_result["count"] > 0:
        for artifact in artifacts_result["artifacts"]:
            artifact_id = artifact["artifact_id"]
            metadata = artifact.get("metadata", {})
            records = metadata.get("total_records", "未知")
            print(f"   📄 {artifact_id} ({records} 条记录)")
    else:
        print("   暂无可用 Artifacts")


async def main():
    """主函数"""
    try:
        await demo_agent_workflow()
        print(f"\n🎉 智能体代码执行演示完成!")
        
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())