"""安全服务实现."""

import hashlib
import hmac
import re
import secrets
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from app.core.logging import get_logger
from app.config import settings

logger = get_logger(__name__)


class SecurityService:
    """安全服务."""
    
    # SQL注入关键词
    SQL_KEYWORDS = [
        "select", "insert", "update", "delete", "drop", "create",
        "alter", "union", "exec", "execute", "script", "javascript",
        "onload", "onerror", "onclick", "alert", "confirm"
    ]
    
    # XSS危险标签
    XSS_TAGS = [
        "<script", "<iframe", "<object", "<embed", "<form",
        "javascript:", "vbscript:", "onload=", "onerror=", "onclick="
    ]
    
    # 安全的HTML标签（白名单）
    SAFE_TAGS = [
        "p", "br", "strong", "em", "u", "i", "b",
        "h1", "h2", "h3", "h4", "h5", "h6",
        "ul", "ol", "li", "a", "img", "code", "pre",
        "blockquote", "table", "tr", "td", "th"
    ]
    
    def __init__(self):
        """初始化安全服务."""
        self.secret_key = settings.SECRET_KEY
    
    def sanitize_input(self, text: str) -> str:
        """
        清理输入文本.
        
        Args:
            text: 输入文本
            
        Returns:
            清理后的文本
        """
        if not text:
            return text
        
        # 移除危险字符
        text = re.sub(r'[<>\"\'&]', '', text)
        
        # 移除控制字符
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        # 限制长度
        max_length = 10000
        if len(text) > max_length:
            text = text[:max_length]
        
        return text.strip()
    
    def check_sql_injection(self, text: str) -> bool:
        """
        检查SQL注入.
        
        Args:
            text: 输入文本
            
        Returns:
            是否包含SQL注入风险
        """
        if not text:
            return False
        
        text_lower = text.lower()
        
        # 检查SQL关键词
        for keyword in self.SQL_KEYWORDS:
            if re.search(r'\b' + keyword + r'\b', text_lower):
                logger.warning(f"Potential SQL injection detected: {keyword}")
                return True
        
        # 检查特殊字符组合
        dangerous_patterns = [
            r"'\s*or\s*'",
            r"'\s*and\s*'",
            r"--",
            r"/\*",
            r"\*/",
            r"xp_",
            r"sp_"
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, text_lower):
                logger.warning(f"Potential SQL injection pattern detected: {pattern}")
                return True
        
        return False
    
    def check_xss(self, text: str) -> bool:
        """
        检查XSS攻击.
        
        Args:
            text: 输入文本
            
        Returns:
            是否包含XSS风险
        """
        if not text:
            return False
        
        text_lower = text.lower()
        
        # 检查危险标签
        for tag in self.XSS_TAGS:
            if tag.lower() in text_lower:
                logger.warning(f"Potential XSS detected: {tag}")
                return True
        
        # 检查事件处理器
        event_pattern = r'on\w+\s*='
        if re.search(event_pattern, text_lower):
            logger.warning("Potential XSS event handler detected")
            return True
        
        return False
    
    def sanitize_html(self, html: str) -> str:
        """
        清理HTML内容.
        
        Args:
            html: HTML内容
            
        Returns:
            清理后的HTML
        """
        if not html:
            return html
        
        # 移除所有script标签及其内容
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        
        # 移除所有style标签及其内容
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
        
        # 移除所有事件处理器
        html = re.sub(r'\s*on\w+\s*=\s*["\'][^"\']*["\']', '', html, flags=re.IGNORECASE)
        
        # 移除javascript:和vbscript:协议
        html = re.sub(r'(javascript|vbscript):', '', html, flags=re.IGNORECASE)
        
        return html
    
    def validate_url(self, url: str) -> bool:
        """
        验证URL安全性.
        
        Args:
            url: URL地址
            
        Returns:
            是否为安全的URL
        """
        if not url:
            return False
        
        try:
            parsed = urlparse(url)
            
            # 只允许http和https协议
            if parsed.scheme not in ['http', 'https']:
                return False
            
            # 检查是否为内网地址
            if self._is_private_ip(parsed.hostname):
                return False
            
            # 检查是否包含危险字符
            if any(char in url for char in ['<', '>', '"', "'"]):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"URL validation error: {e}")
            return False
    
    def _is_private_ip(self, hostname: Optional[str]) -> bool:
        """
        检查是否为内网IP.
        
        Args:
            hostname: 主机名
            
        Returns:
            是否为内网IP
        """
        if not hostname:
            return False
        
        private_patterns = [
            r'^127\.',
            r'^10\.',
            r'^172\.(1[6-9]|2[0-9]|3[0-1])\.',
            r'^192\.168\.',
            r'^localhost$',
            r'^0\.0\.0\.0$'
        ]
        
        for pattern in private_patterns:
            if re.match(pattern, hostname):
                return True
        
        return False
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """
        加密敏感数据.
        
        Args:
            data: 敏感数据
            
        Returns:
            加密后的数据
        """
        # 简化实现，实际应使用更强的加密算法
        key = self.secret_key.encode()
        data_bytes = data.encode()
        
        signature = hmac.new(key, data_bytes, hashlib.sha256).hexdigest()
        
        # 返回base64编码的加密数据
        import base64
        encrypted = base64.b64encode(f"{data}:{signature}".encode()).decode()
        
        return encrypted
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> Optional[str]:
        """
        解密敏感数据.
        
        Args:
            encrypted_data: 加密的数据
            
        Returns:
            解密后的数据
        """
        try:
            import base64
            decoded = base64.b64decode(encrypted_data.encode()).decode()
            
            data, signature = decoded.rsplit(':', 1)
            
            # 验证签名
            key = self.secret_key.encode()
            data_bytes = data.encode()
            expected_signature = hmac.new(key, data_bytes, hashlib.sha256).hexdigest()
            
            if hmac.compare_digest(signature, expected_signature):
                return data
            
            logger.warning("Invalid signature in encrypted data")
            return None
            
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            return None
    
    def generate_secure_token(self, length: int = 32) -> str:
        """
        生成安全令牌.
        
        Args:
            length: 令牌长度
            
        Returns:
            安全令牌
        """
        return secrets.token_urlsafe(length)
    
    def hash_password(self, password: str) -> str:
        """
        哈希密码.
        
        Args:
            password: 原始密码
            
        Returns:
            哈希后的密码
        """
        # 使用bcrypt或argon2更安全，这里简化实现
        salt = secrets.token_hex(16)
        pwd_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt.encode(),
            100000  # 迭代次数
        )
        
        return f"{salt}:{pwd_hash.hex()}"
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """
        验证密码.
        
        Args:
            password: 原始密码
            hashed: 哈希后的密码
            
        Returns:
            是否匹配
        """
        try:
            salt, pwd_hash = hashed.split(':')
            
            test_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode(),
                salt.encode(),
                100000
            )
            
            return test_hash.hex() == pwd_hash
            
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    def validate_file_type(
        self,
        filename: str,
        allowed_types: List[str]
    ) -> bool:
        """
        验证文件类型.
        
        Args:
            filename: 文件名
            allowed_types: 允许的类型列表
            
        Returns:
            是否为允许的类型
        """
        if not filename:
            return False
        
        # 获取文件扩展名
        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        
        # 检查是否在允许列表中
        if ext not in allowed_types:
            logger.warning(f"File type not allowed: {ext}")
            return False
        
        # 检查双扩展名攻击
        if filename.count('.') > 1:
            parts = filename.split('.')
            for part in parts[:-1]:
                if part.lower() in ['php', 'asp', 'jsp', 'exe', 'sh']:
                    logger.warning(f"Potential double extension attack: {filename}")
                    return False
        
        return True
    
    def sanitize_filename(self, filename: str) -> str:
        """
        清理文件名.
        
        Args:
            filename: 原始文件名
            
        Returns:
            清理后的文件名
        """
        if not filename:
            return "unnamed"
        
        # 移除路径分隔符
        filename = filename.replace('/', '').replace('\\', '')
        
        # 移除特殊字符
        filename = re.sub(r'[<>:"|?*]', '', filename)
        
        # 移除控制字符
        filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)
        
        # 限制长度
        max_length = 255
        if len(filename) > max_length:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            if ext:
                name = name[:max_length - len(ext) - 1]
                filename = f"{name}.{ext}"
            else:
                filename = filename[:max_length]
        
        return filename or "unnamed"


# 全局安全服务实例
security_service = SecurityService()