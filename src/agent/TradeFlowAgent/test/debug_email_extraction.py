"""
调试邮箱提取问题
"""

import re

test_content = """
邮箱：sales@example.com
Email: info@example.com
"""

# 测试正则表达式
email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
matches = re.findall(email_pattern, test_content)
print(f"找到的邮箱: {matches}")

# 检查example.com是否被过滤
exclude_domains = ['example.com', 'test.com', 'localhost']
filtered_emails = []
for email in set(matches):
    domain = email.split('@')[1].lower()
    if domain not in exclude_domains:
        filtered_emails.append(email.lower())
        
print(f"过滤后的邮箱: {filtered_emails}")

# 看看如果不过滤会怎样
if matches and not filtered_emails:
    print("问题：所有邮箱都被过滤掉了，因为使用了example.com域名")