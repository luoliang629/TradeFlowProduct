"""
Tendata API 认证系统
处理 API Key 到访问令牌的转换和令牌管理
"""

import asyncio
import time
from typing import Dict, Optional, Any
import httpx
from datetime import datetime, timedelta


class TendataAuth:
    """Tendata API 认证管理器"""

    def __init__(self, api_key: str, base_url: str = "https://open-api.tendata.cn"):
        """
        初始化认证管理器

        Args:
            api_key: Tendata API 密钥
            base_url: API 基础 URL
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
        self._lock = asyncio.Lock()

    async def get_access_token(self) -> str:
        """
        获取有效的访问令牌，必要时自动刷新

        Returns:
            有效的访问令牌

        Raises:
            Exception: 获取令牌失败
        """
        async with self._lock:
            # 检查令牌是否需要刷新
            if self._needs_refresh():
                await self._refresh_token()

            if not self._access_token:
                raise Exception("无法获取访问令牌")

            return self._access_token

    def _needs_refresh(self) -> bool:
        """检查令牌是否需要刷新"""
        if not self._access_token or not self._token_expires_at:
            return True

        # 提前 5 分钟刷新令牌
        buffer_time = timedelta(minutes=5)
        return datetime.now() >= (self._token_expires_at - buffer_time)

    async def _refresh_token(self) -> None:
        """刷新访问令牌"""
        url = f"{self.base_url}/v2/access-token"
        params = {"apiKey": self.api_key}

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()

                data = response.json()
                if data.get("success") and data.get("data"):
                    token_data = data["data"]
                    self._access_token = token_data.get("accessToken")
                    expires_in = token_data.get("expiresIn", 7200)

                    # 设置过期时间
                    self._token_expires_at = datetime.now() + timedelta(seconds=expires_in)
                else:
                    error_msg = data.get("msg", "未知错误")
                    raise Exception(f"获取令牌失败: {error_msg}")

            except httpx.HTTPStatusError as e:
                raise Exception(f"HTTP 错误: {e.response.status_code}")
            except Exception as e:
                raise Exception(f"获取访问令牌失败: {str(e)}")

    async def make_authenticated_request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        发起认证的 API 请求

        Args:
            method: HTTP 方法 (GET, POST 等)
            endpoint: API 端点路径
            **kwargs: 传递给 httpx 的其他参数

        Returns:
            API 响应数据

        Raises:
            Exception: 请求失败
        """
        # 获取有效的访问令牌
        access_token = await self.get_access_token()

        # 设置认证头
        headers = kwargs.get("headers", {})
        headers["Authorization"] = f"Bearer {access_token}"
        kwargs["headers"] = headers

        # 构建完整 URL
        if not endpoint.startswith("http"):
            url = f"{self.base_url}{endpoint}"
        else:
            url = endpoint

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.request(method, url, **kwargs)
                response.raise_for_status()

                data = response.json()
                if not data.get("success"):
                    # 检查是否是令牌过期错误
                    error_code = data.get("code")
                    if error_code in [40301, 40302]:  # 令牌无效或过期
                        # 重置令牌并重试一次
                        self._access_token = None
                        self._token_expires_at = None
                        return await self.make_authenticated_request(method, endpoint, **kwargs)
                    else:
                        error_msg = data.get("msg", "未知错误")
                        raise Exception(f"API 错误 [{error_code}]: {error_msg}")

                return data

            except httpx.HTTPStatusError as e:
                raise Exception(f"HTTP 错误: {e.response.status_code}")
            except Exception as e:
                raise Exception(f"请求失败: {str(e)}")


class RateLimiter:
    """API 请求速率限制器"""

    def __init__(self, max_requests: int = 200, window_seconds: int = 60):
        """
        初始化速率限制器

        Args:
            max_requests: 时间窗口内最大请求数
            window_seconds: 时间窗口大小（秒）
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: list[float] = []
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """获取请求许可，必要时等待"""
        async with self._lock:
            now = time.time()
            # 清理过期的请求记录
            self.requests = [req_time for req_time in self.requests if now - req_time < self.window_seconds]

            # 如果达到限制，等待
            if len(self.requests) >= self.max_requests:
                oldest_request = self.requests[0]
                wait_time = self.window_seconds - (now - oldest_request) + 0.1
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
                    # 递归调用重新检查
                    await self.acquire()
                    return

            # 记录新请求
            self.requests.append(now)
