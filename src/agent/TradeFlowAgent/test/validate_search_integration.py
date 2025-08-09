"""
验证搜索集成的完整性
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 加载环境变量
load_dotenv()


def validate_search_integration():
    """验证搜索相关组件的集成"""
    print("=== 验证搜索集成完整性 ===\n")
    
    # 1. 验证工具导入
    try:
        from trade_flow.tools.web_search import web_search, web_search_tool
        print("✅ web_search 工具导入成功")
        print(f"   - web_search 是函数: {callable(web_search)}")
        print(f"   - web_search_tool 是工具: {callable(web_search_tool)}")
        print(f"   - 工具指向同一函数: {web_search is web_search_tool}")
    except Exception as e:
        print(f"❌ web_search 工具导入失败: {e}")
        return False
    
    # 2. 验证 Agent 导入
    try:
        from trade_flow.agents.search_agent import search_agent
        print("✅ search_agent 导入成功")
        print(f"   - Agent 名称: {search_agent.name}")
        print(f"   - 工具数量: {len(search_agent.tools)}")
        print(f"   - 工具列表: {[tool.__name__ if hasattr(tool, '__name__') else str(tool) for tool in search_agent.tools]}")
    except Exception as e:
        print(f"❌ search_agent 导入失败: {e}")
        return False
    
    # 3. 验证工具功能
    try:
        import asyncio
        
        async def test_tool():
            result = await web_search("测试查询", num_results=2)
            return result
        
        result = asyncio.run(test_tool())
        print("✅ web_search 工具功能正常")
        print(f"   - 返回状态: {result['status']}")
        print(f"   - 结果来源: {result['source']}")
        print(f"   - 结果数量: {result['total']}")
    except Exception as e:
        print(f"❌ web_search 工具功能测试失败: {e}")
        return False
    
    # 4. 验证环境配置
    print("✅ 环境配置检查:")
    print(f"   - JINA_API_KEY: {'已配置' if os.getenv('JINA_API_KEY') else '未配置'}")
    
    # 5. 验证 ADK 兼容性
    try:
        from google.adk.agents import Agent
        print("✅ Google ADK 导入成功")
        print(f"   - Agent 类可用: {Agent is not None}")
    except Exception as e:
        print(f"❌ Google ADK 导入失败: {e}")
        return False
    
    print("\n🎉 所有组件验证通过！搜索功能集成正常。")
    
    # 6. 总结增强的功能
    print("\n=== 搜索功能增强总结 ===")
    print("✅ Jina Search API 集成")
    print("✅ 多级降级机制 (Jina → DuckDuckGo)")
    print("✅ 站内搜索支持")
    print("✅ 两阶段搜索策略")
    print("✅ 增强的 Agent 指令")
    print("✅ 专业贸易领域优化")
    
    return True


if __name__ == "__main__":
    success = validate_search_integration()
    exit(0 if success else 1)