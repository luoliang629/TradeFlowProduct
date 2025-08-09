#!/usr/bin/env python3
"""
智能体下载贸易数据示例

展示如何在与智能体对话中下载贸易数据
"""

import asyncio
from trade_flow.agents.trade_agent import trade_agent


async def demo_download_workflow():
    """演示下载工作流程"""
    print("🤖 贸易数据智能体 - 下载功能演示")
    print("=" * 60)
    
    # 模拟用户查询
    queries = [
        "查询2023年1月份电子产品的贸易数据",
        "请列出当前会话中所有的贸易数据文件",
        "下载刚才查询的电子产品贸易数据",
        "查询2023年2月份纺织品的进口数据",
        "导出所有查询结果为CSV文件到本地"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n👤 用户查询 {i}: {query}")
        print("-" * 40)
        
        # 获取智能体响应
        response = await trade_agent.run(query)
        
        # 打印响应（简化版）
        print(f"🤖 智能体响应:")
        # 截取响应的前500个字符
        if len(response) > 500:
            print(response[:500] + "...\n[响应已截断]")
        else:
            print(response)
        
        # 暂停以便观察
        if i < len(queries):
            print("\n⏸️  继续下一个查询...")
            await asyncio.sleep(2)
    
    print("\n" + "=" * 60)
    print("✅ 演示完成！请检查 downloads 目录中的 CSV 文件")


async def demo_programmatic_download():
    """演示程序化下载"""
    print("\n\n🔧 程序化下载演示")
    print("=" * 60)
    
    # 直接使用工具进行查询和下载
    from trade_flow.tools import (
        get_trade_data_tool,
        list_trade_data_artifacts_tool,
        download_trade_data_artifact_tool,
        export_all_trade_data_artifacts_tool
    )
    
    print("1. 查询多个贸易数据集...")
    
    # 查询不同类型的数据
    datasets = [
        {"product_desc": "machinery", "start_date": "2023-03-01", "end_date": "2023-03-31"},
        {"product_desc": "chemicals", "start_date": "2023-04-01", "end_date": "2023-04-30"},
        {"exporter": "ABC TRADING", "start_date": "2023-01-01", "end_date": "2023-06-30"}
    ]
    
    for params in datasets:
        result = await get_trade_data_tool(**params)
        if result["status"] == "success":
            records = len(result.get("trade_records", []))
            print(f"   ✓ 查询成功: {params} - {records} 条记录")
    
    print("\n2. 列出所有可下载的数据...")
    artifacts = await list_trade_data_artifacts_tool()
    print(f"   找到 {artifacts['count']} 个数据文件")
    
    print("\n3. 下载特定数据文件...")
    if artifacts['count'] > 0:
        # 下载第一个文件作为示例
        first_artifact = artifacts['artifacts'][0]
        download_result = await download_trade_data_artifact_tool(
            artifact_id=first_artifact['artifact_id'],
            download_path="downloads/demo"
        )
        
        if download_result['success']:
            print(f"   ✓ 下载成功: {download_result['file_name']}")
            print(f"   文件位置: {download_result['file_path']}")
    
    print("\n4. 批量导出所有数据...")
    export_result = await export_all_trade_data_artifacts_tool(
        download_path="downloads/batch_export"
    )
    
    if export_result['success']:
        print(f"   ✓ 成功导出 {export_result['exported_count']} 个文件")
        print(f"   导出目录: {export_result['download_path']}")
    
    print("\n✅ 程序化下载演示完成！")


async def main():
    """主函数"""
    try:
        # 演示智能体对话下载
        await demo_download_workflow()
        
        # 演示程序化下载
        await demo_programmatic_download()
        
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 确保有 .env 文件配置
    import os
    if not os.path.exists('.env'):
        print("❌ 错误: 未找到 .env 配置文件")
        print("请创建 .env 文件并配置必要的 API 密钥")
        exit(1)
    
    asyncio.run(main())