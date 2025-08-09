"""
调试网站提取问题
"""

import re

test_content = """网站：www.example-led.com"""

print(f"测试内容: '{test_content}'")

# 测试网站提取模式
website_patterns = [
    r'(网站|Website|官网|Site)[:：]\s*(https?://[^\s<>\"\']+)',
    r'(网址|URL|Web)[:：]\s*(www\.[^\s<>\"\']+)',
    r'https?://(?:www\.)?([a-zA-Z0-9-]+\.[a-zA-Z]{2,})[^\s<>\"\']+'
]

for i, pattern in enumerate(website_patterns):
    match = re.search(pattern, test_content, re.IGNORECASE)
    if match:
        print(f"模式 {i+1} 匹配成功: {match.groups()}")
        website = match.group(2) if len(match.groups()) >= 2 else match.group(0)
        print(f"提取的网站: {website}")
    else:
        print(f"模式 {i+1} 未匹配")