"""
调试 Jina Search 响应格式
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from trade_flow.tools.web_search import _jina_search


async def debug_jina_response():
    """调试 Jina Search 响应格式"""
    print("=== 调试 Jina Search 响应 ===\n")
    
    try:
        # 执行一个简单的搜索
        result = await _jina_search("AI technology 2024", 3)
        
        print(f"状态: {result['status']}")
        print(f"来源: {result['source']}")
        print(f"结果总数: {result['total']}")
        print("\n原始结果:")
        
        for i, item in enumerate(result['results'], 1):
            print(f"\n{i}. 标题: {item.get('title', 'N/A')}")
            print(f"   URL: {item.get('url', 'N/A')}")
            print(f"   域名: {item.get('displayLink', 'N/A')}")
            print(f"   摘要: {item.get('snippet', 'N/A')}")
            
    except Exception as e:
        print(f"错误: {str(e)}")


if __name__ == "__main__":
    asyncio.run(debug_jina_response())