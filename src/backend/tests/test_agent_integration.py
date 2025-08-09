"""
Agent集成测试
测试TradeFlowAgent与后端服务的完整集成
"""

import asyncio
import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient

from app.main import app
from app.services.agent_service import agent_service
from app.services.session_manager import session_manager
from app.services.agent_performance_optimizer import performance_optimizer


class TestAgentIntegration:
    """Agent集成测试类"""
    
    @pytest.fixture
    def test_user_id(self):
        """测试用户ID"""
        return str(uuid.uuid4())
    
    @pytest.fixture
    def test_session_id(self):
        """测试会话ID"""
        return str(uuid.uuid4())
    
    @pytest.fixture
    def test_query(self):
        """测试查询"""
        return "帮我查询2024年中国纺织品的出口数据"
    
    @pytest.fixture
    async def mock_agent_response(self):
        """模拟Agent响应"""
        mock_response = MagicMock()
        mock_response.parts = [MagicMock(text="这是模拟的Agent响应内容")]
        return mock_response
    
    @pytest.mark.asyncio
    async def test_agent_service_initialization(self):
        """测试Agent服务初始化"""
        # 重置服务状态
        agent_service._initialized = False
        
        with patch('app.services.agent_service.AgentService._setup_environment'):
            with patch('sys.path.insert'):
                with patch('importlib.import_module') as mock_import:
                    # 模拟成功导入
                    mock_runner = MagicMock()
                    mock_agent = MagicMock()
                    mock_adk = MagicMock()
                    mock_adk.core.Runner.return_value = mock_runner
                    mock_trade_flow = MagicMock()
                    mock_trade_flow.main_agent.root_agent = mock_agent
                    
                    mock_import.side_effect = [mock_adk, mock_trade_flow]
                    
                    await agent_service.initialize()
                    
                    assert agent_service._initialized is True
                    assert agent_service._runner is mock_runner
                    assert agent_service._root_agent is mock_agent
    
    @pytest.mark.asyncio
    async def test_agent_sync_query_with_cache(
        self, 
        test_user_id, 
        test_session_id, 
        test_query, 
        mock_agent_response
    ):
        """测试同步Agent查询（带缓存）"""
        # 准备测试环境
        agent_service._initialized = True
        agent_service._runner = AsyncMock()
        agent_service._root_agent = MagicMock()
        
        # 模拟Runner执行结果
        agent_service._runner.run_async.return_value = mock_agent_response
        
        # 第一次查询（无缓存）
        with patch('app.services.agent_service.performance_optimizer') as mock_optimizer:
            mock_optimizer.get_cached_response_or_none.return_value = None
            mock_optimizer.get_optimized_runner.return_value = agent_service._runner
            mock_optimizer.return_runner = AsyncMock()
            mock_optimizer.cache_response_if_enabled = AsyncMock()
            mock_optimizer.check_token_usage.return_value = True
            
            result1 = await agent_service.query_agent_sync(
                test_user_id, test_session_id, test_query
            )
            
            assert result1["status"] == "success"
            assert "这是模拟的Agent响应内容" in result1["response"]
            assert result1["metadata"]["cached"] is False
        
        # 第二次查询（有缓存）
        cached_response = {
            "response": "这是缓存的响应",
            "cached_at": "2024-01-01T00:00:00Z"
        }
        
        with patch('app.services.agent_service.performance_optimizer') as mock_optimizer:
            mock_optimizer.get_cached_response_or_none.return_value = cached_response
            
            result2 = await agent_service.query_agent_sync(
                test_user_id, test_session_id, test_query
            )
            
            assert result2["status"] == "success"
            assert result2["response"] == "这是缓存的响应"
            assert result2["metadata"]["cached"] is True
    
    @pytest.mark.asyncio
    async def test_agent_stream_query(
        self, 
        test_user_id, 
        test_session_id, 
        test_query, 
        mock_agent_response
    ):
        """测试流式Agent查询"""
        # 准备测试环境
        agent_service._initialized = True
        agent_service._runner = AsyncMock()
        agent_service._root_agent = MagicMock()
        agent_service._runner.run_async.return_value = mock_agent_response
        
        events = []
        async for sse_event in agent_service.query_agent_stream(
            test_user_id, test_session_id, test_query
        ):
            events.append(sse_event)
            # 只收集前5个事件避免测试过长
            if len(events) >= 5:
                break
        
        assert len(events) > 0
        # 检查是否有开始事件
        start_events = [e for e in events if "event: start" in e]
        assert len(start_events) > 0
        
        # 检查是否有chunk事件
        chunk_events = [e for e in events if "event: chunk" in e]
        assert len(chunk_events) > 0
    
    @pytest.mark.asyncio
    async def test_session_management(self, test_user_id):
        """测试会话管理"""
        # 创建会话
        session_id = await session_manager.create_session(
            test_user_id, metadata={"test": "data"}
        )
        
        assert session_id is not None
        
        # 获取会话
        session = await session_manager.get_session(test_user_id, session_id)
        assert session is not None
        assert session["user_id"] == test_user_id
        assert session["status"] == "active"
        
        # 添加消息历史
        await session_manager.add_message_to_history(
            test_user_id, session_id, "user", "测试消息"
        )
        
        # 获取历史
        history = await session_manager.get_message_history(
            test_user_id, session_id
        )
        assert len(history) == 1
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "测试消息"
        
        # 关闭会话
        await session_manager.close_session(test_user_id, session_id)
        
        # 验证会话状态
        updated_session = await session_manager.get_session(test_user_id, session_id)
        assert updated_session["status"] == "closed"
    
    @pytest.mark.asyncio
    async def test_performance_optimization(self):
        """测试性能优化功能"""
        # 测试Runner池
        runner = await performance_optimizer.get_optimized_runner()
        assert runner is not None
        
        await performance_optimizer.return_runner(runner)
        
        # 测试缓存
        test_response = await performance_optimizer.get_cached_response_or_none(
            "test_user", "test_query"
        )
        # 第一次查询应该没有缓存
        assert test_response is None
        
        # 缓存响应
        cached = await performance_optimizer.cache_response_if_enabled(
            "test_user", "test_query", "test_response"
        )
        
        if cached:  # 只有在启用缓存时才验证
            cached_response = await performance_optimizer.get_cached_response_or_none(
                "test_user", "test_query"
            )
            assert cached_response is not None
            assert cached_response["response"] == "test_response"
        
        # 测试Token监控
        usage_ok = await performance_optimizer.check_token_usage(
            "test_user", 100, 200
        )
        assert usage_ok is True  # 正常情况下应该在限额内
        
        # 获取统计信息
        stats = await performance_optimizer.get_performance_stats()
        assert "runner_pool" in stats
        assert "response_cache" in stats
    
    @pytest.mark.asyncio
    async def test_error_handling_and_retry(
        self, test_user_id, test_session_id, test_query
    ):
        """测试错误处理和重试机制"""
        # 准备测试环境
        agent_service._initialized = True
        agent_service._runner = AsyncMock()
        agent_service._root_agent = MagicMock()
        
        # 模拟第一次失败，第二次成功
        call_count = 0
        async def mock_run_async(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("模拟的临时错误")
            else:
                mock_response = MagicMock()
                mock_response.parts = [MagicMock(text="重试后的成功响应")]
                return mock_response
        
        agent_service._runner.run_async.side_effect = mock_run_async
        
        with patch('app.services.agent_service.performance_optimizer') as mock_optimizer:
            mock_optimizer.get_cached_response_or_none.return_value = None
            mock_optimizer.get_optimized_runner.return_value = agent_service._runner
            mock_optimizer.return_runner = AsyncMock()
            mock_optimizer.cache_response_if_enabled = AsyncMock()
            mock_optimizer.check_token_usage.return_value = True
            
            # 由于有重试机制，应该最终成功
            result = await agent_service.query_agent_sync(
                test_user_id, test_session_id, test_query
            )
            
            assert result["status"] == "success"
            assert "重试后的成功响应" in result["response"]
            assert call_count == 2  # 验证确实重试了
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """测试健康检查"""
        # 测试未初始化状态
        agent_service._initialized = False
        health = await agent_service.health_check()
        assert health["healthy"] is False
        assert health["status"] == "not_initialized"
        
        # 测试已初始化状态
        agent_service._initialized = True
        agent_service._runner = MagicMock()
        agent_service._root_agent = MagicMock()
        
        health = await agent_service.health_check()
        assert health["healthy"] is True
        assert health["status"] == "healthy"
        assert "checks" in health


class TestAgentAPIEndpoints:
    """Agent API端点测试"""
    
    @pytest.fixture
    def test_headers(self):
        """测试请求头（模拟认证）"""
        return {"Authorization": "Bearer test_token"}
    
    @pytest.mark.asyncio
    async def test_agent_sync_query_endpoint(self, test_headers):
        """测试同步查询API端点"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            with patch('app.dependencies.auth.get_current_user') as mock_auth:
                # 模拟用户认证
                mock_user = MagicMock()
                mock_user.id = "test_user_123"
                mock_auth.return_value = mock_user
                
                with patch('app.services.agent_service.agent_service') as mock_service:
                    # 模拟服务响应
                    mock_service.query_agent_sync.return_value = {
                        "status": "success",
                        "response": "测试响应",
                        "user_id": "test_user_123",
                        "session_id": "test_session",
                        "metadata": {"response_length": 4}
                    }
                    
                    response = await client.post(
                        "/api/v1/agent/query",
                        headers=test_headers,
                        json={
                            "query": "测试查询",
                            "session_id": "test_session"
                        }
                    )
                    
                    assert response.status_code == 200
                    data = response.json()
                    assert data["status"] == "success"
                    assert data["response"] == "测试响应"
    
    @pytest.mark.asyncio
    async def test_agent_health_endpoint(self):
        """测试健康检查API端点"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            with patch('app.services.agent_service.agent_service') as mock_service:
                mock_service.health_check.return_value = {
                    "status": "healthy",
                    "healthy": True,
                    "message": "所有组件正常"
                }
                
                response = await client.get("/api/v1/agent/health")
                
                assert response.status_code == 200
                data = response.json()
                assert data["healthy"] is True
                assert data["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_session_management_endpoints(self, test_headers):
        """测试会话管理API端点"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            with patch('app.dependencies.auth.get_current_user') as mock_auth:
                mock_user = MagicMock()
                mock_user.id = "test_user_123"
                mock_auth.return_value = mock_user
                
                with patch('app.services.session_manager.session_manager') as mock_session:
                    # 测试创建会话
                    mock_session.create_session.return_value = "new_session_123"
                    mock_session.get_session.return_value = {
                        "user_id": "test_user_123",
                        "session_id": "new_session_123",
                        "created_at": "2024-01-01T00:00:00Z",
                        "last_active": "2024-01-01T00:00:00Z",
                        "message_count": 0,
                        "status": "active",
                        "metadata": {}
                    }
                    
                    response = await client.post(
                        "/api/v1/agent/sessions",
                        headers=test_headers,
                        json={"metadata": {"test": "data"}}
                    )
                    
                    assert response.status_code == 200
                    data = response.json()
                    assert data["session_id"] == "new_session_123"
                    assert data["status"] == "active"


class TestLoadAndStability:
    """负载和稳定性测试"""
    
    @pytest.mark.asyncio
    async def test_concurrent_queries(self):
        """测试并发查询"""
        # 准备测试环境
        agent_service._initialized = True
        agent_service._runner = AsyncMock()
        agent_service._root_agent = MagicMock()
        
        mock_response = MagicMock()
        mock_response.parts = [MagicMock(text="并发测试响应")]
        agent_service._runner.run_async.return_value = mock_response
        
        # 创建10个并发查询
        tasks = []
        for i in range(10):
            task = agent_service.query_agent_sync(
                f"user_{i}", f"session_{i}", f"查询_{i}"
            )
            tasks.append(task)
        
        with patch('app.services.agent_service.performance_optimizer') as mock_optimizer:
            mock_optimizer.get_cached_response_or_none.return_value = None
            mock_optimizer.get_optimized_runner.return_value = agent_service._runner
            mock_optimizer.return_runner = AsyncMock()
            mock_optimizer.cache_response_if_enabled = AsyncMock()
            mock_optimizer.check_token_usage.return_value = True
            
            # 执行并发查询
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 验证结果
            success_count = sum(1 for r in results if isinstance(r, dict) and r.get("status") == "success")
            assert success_count >= 8  # 至少80%成功率
    
    @pytest.mark.asyncio
    async def test_memory_leak_prevention(self):
        """测试内存泄漏预防"""
        # 模拟长时间运行的场景
        initial_pool_size = len(performance_optimizer.runner_pool._pool)
        
        # 执行多次操作
        for i in range(20):
            runner = await performance_optimizer.get_optimized_runner()
            await performance_optimizer.return_runner(runner)
        
        # 检查池大小是否稳定
        final_pool_size = len(performance_optimizer.runner_pool._pool)
        assert final_pool_size <= performance_optimizer.runner_pool.max_pool_size
        
        # 获取统计信息
        stats = await performance_optimizer.get_performance_stats()
        assert stats["runner_pool"]["pool_size"] <= performance_optimizer.runner_pool.max_pool_size
    
    @pytest.mark.asyncio
    async def test_error_recovery(self):
        """测试错误恢复"""
        # 模拟系统错误后的恢复
        agent_service._initialized = False
        
        # 尝试查询应该触发重新初始化
        with patch.object(agent_service, 'initialize', new_callable=AsyncMock):
            with patch('app.services.agent_service.performance_optimizer') as mock_optimizer:
                mock_optimizer.get_cached_response_or_none.return_value = None
                
                try:
                    await agent_service.query_agent_sync(
                        "test_user", "test_session", "test_query"
                    )
                except:
                    pass  # 预期可能失败，主要测试恢复机制
                
                # 验证尝试了初始化
                agent_service.initialize.assert_called_once()


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])