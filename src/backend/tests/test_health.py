"""健康检查API测试."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_basic_health_check(test_client: AsyncClient):
    """测试基础健康检查."""
    response = await test_client.get("/api/v1/health")
    
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"
    assert "uptime" in data
    assert "timestamp" in data
    assert isinstance(data["uptime"], (int, float))


@pytest.mark.asyncio
async def test_detailed_health_check(test_client: AsyncClient):
    """测试详细健康检查."""
    response = await test_client.get("/api/v1/health/detailed")
    
    # 注意：在测试环境中，某些依赖可能不可用，所以可能返回503
    # 但响应格式应该是正确的
    data = response.json()
    
    if response.status_code == 200:
        assert data["success"] is True
        assert data["status"] in ["healthy", "degraded"]
        assert "dependencies" in data
        assert isinstance(data["dependencies"], dict)
    elif response.status_code == 503:
        # 服务不健康的情况
        assert "detail" in data or "message" in data
    else:
        pytest.fail(f"Unexpected status code: {response.status_code}")


@pytest.mark.asyncio
async def test_liveness_check(test_client: AsyncClient):
    """测试存活性检查."""
    response = await test_client.get("/api/v1/health/liveness")
    
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "alive"


@pytest.mark.asyncio
async def test_readiness_check(test_client: AsyncClient):
    """测试就绪性检查."""
    response = await test_client.get("/api/v1/health/readiness")
    
    # 在测试环境中，某些依赖可能不可用
    data = response.json()
    
    if response.status_code == 200:
        assert data["status"] == "ready"
    elif response.status_code == 503:
        assert "detail" in data
    else:
        pytest.fail(f"Unexpected status code: {response.status_code}")


@pytest.mark.asyncio
async def test_root_endpoint(test_client: AsyncClient):
    """测试根路径端点."""
    response = await test_client.get("/")
    
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert data["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_request_headers(test_client: AsyncClient):
    """测试响应头部."""
    response = await test_client.get("/api/v1/health")
    
    # 检查性能相关的头部
    assert "X-Request-ID" in response.headers
    assert "X-Process-Time" in response.headers
    
    # 验证响应时间格式
    process_time = response.headers["X-Process-Time"]
    assert process_time.replace(".", "", 1).isdigit()  # 应该是数字格式