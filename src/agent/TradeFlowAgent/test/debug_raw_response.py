"""
查看 Jina Search 原始响应格式
"""

import asyncio
import os
import sys
import httpx
from urllib.parse import quote
from pathlib import Path
from dotenv import load_dotenv

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 加载环境变量
load_dotenv()


async def debug_raw_response():
    """查看 Jina Search 原始响应"""
    print("=== Jina Search 原始响应格式 ===\n")
    
    query = "AI technology 2024"
    encoded_query = quote(query)
    base_url = f"https://s.jina.ai/{encoded_query}"
    
    print(f"请求URL: {base_url}")
    print("-" * 60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            headers = {
                "Accept": "text/plain",
                "User-Agent": "TradeFlowAgent/1.0"
            }
            
            api_key = os.getenv("JINA_API_KEY")
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            
            response = await client.get(base_url, headers=headers)
            response.raise_for_status()
            
            print(f"状态码: {response.status_code}")
            print(f"内容类型: {response.headers.get('content-type')}")
            print(f"内容长度: {len(response.text)}")
            print("\n原始响应内容（前2000字符）:")
            print("=" * 60)
            print(response.text[:2000])
            print("=" * 60)
            
            # 分析结构
            print("\n内容结构分析:")
            lines = response.text.split('\n')
            for i, line in enumerate(lines[:30]):  # 只看前30行
                if line.strip():
                    if line.startswith('#'):
                        print(f"第{i+1}行 [标题]: {line}")
                    elif line.startswith('[') and '](' in line:
                        print(f"第{i+1}行 [链接]: {line}")
                    elif len(line) > 50:
                        print(f"第{i+1}行 [内容]: {line[:50]}...")
                    else:
                        print(f"第{i+1}行: {line}")
                        
        except Exception as e:
            print(f"错误: {e}")
            if hasattr(e, 'response'):
                print(f"响应状态: {e.response.status_code}")
                print(f"响应内容: {e.response.text[:500]}")


if __name__ == "__main__":
    asyncio.run(debug_raw_response())