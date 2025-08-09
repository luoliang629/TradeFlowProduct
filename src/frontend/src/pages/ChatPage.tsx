import React, { useState, useEffect, useCallback } from 'react';
import { Layout, Button, message, Tooltip, Dropdown } from 'antd';
import {
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  SettingOutlined,
  ClearOutlined,
  DownloadOutlined,
} from '@ant-design/icons';
import { useParams, useNavigate } from 'react-router-dom';
import { useAppSelector, useAppDispatch } from '../store/hooks';
import SessionList from '../components/chat/SessionList';
import ChatInterface from '../components/chat/ChatInterface';
import SSEConnectionIndicator from '../components/chat/SSEConnectionIndicator';
import { useSSE } from '../hooks/useSSE';
import { apiService } from '../services';
import { setCurrentSession } from '../store/chatSlice';
import type { Session } from '../types';

const { Sider, Content } = Layout;

const ChatPage: React.FC = () => {
  const navigate = useNavigate();
  const { sessionId } = useParams();
  const dispatch = useAppDispatch();
  const { user } = useAppSelector(state => state.auth);
  const { currentSession } = useAppSelector(state => state.chat);
  
  // 状态管理
  const [sessions, setSessions] = useState<Session[]>([]);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [sessionsLoading, setSessionsLoading] = useState(true);
  
  // SSE连接管理
  const sse = useSSE({
    autoReconnect: true,
    maxReconnectAttempts: 3,
    reconnectInterval: 3000,
    heartbeatInterval: 30000,
  });

  // 加载会话列表
  const loadSessions = useCallback(async () => {
    try {
      setSessionsLoading(true);
      const response = await apiService.sessions.getList();
      if (response.success) {
        setSessions(response.data || []);
        
        // 如果没有指定sessionId且有会话，跳转到第一个会话
        if (!sessionId && response.data && response.data.length > 0) {
          navigate(`/chat/${response.data[0].id}`, { replace: true });
        }
      }
    } catch (error) {
      console.error('加载会话列表失败:', error);
      message.error('加载会话列表失败');
    } finally {
      setSessionsLoading(false);
    }
  }, [sessionId, navigate]);


  // 创建新会话
  const createNewSession = async () => {
    try {
      const response = await apiService.sessions.create('新对话');
      if (response.success) {
        const newSession = response.data;
        setSessions(prev => [newSession, ...prev]);
        navigate(`/chat/${newSession.id}`);
        message.success('新对话已创建');
      }
    } catch (error) {
      message.error('创建对话失败');
    }
  };


  // 选择会话
  const handleSessionSelect = (session: Session) => {
    navigate(`/chat/${session.id}`);
  };

  // 清空当前对话
  const clearCurrentChat = async () => {
    if (currentSession) {
      try {
        await apiService.sessions.clear(currentSession.id);
        message.success('对话已清空');
        // 会话清空后，ChatInterface会自动刷新消息
      } catch (error) {
        message.error('清空对话失败');
      }
    }
  };

  // 导出对话
  const exportChat = async () => {
    if (!currentSession) {
      message.warning('没有对话可导出');
      return;
    }
    
    try {
      const response = await apiService.sessions.export(currentSession.id);
      if (response.success && response.data) {
        const blob = new Blob([response.data], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${currentSession.title}_${new Date().toISOString().split('T')[0]}.txt`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        message.success('对话已导出');
      }
    } catch (error) {
      message.error('导出对话失败');
    }
  };

  // 聊天设置菜单
  const chatMenuItems = [
    {
      key: 'clear',
      label: '清空对话',
      icon: <ClearOutlined />,
      onClick: clearCurrentChat,
    },
    {
      key: 'export',
      label: '导出对话',
      icon: <DownloadOutlined />,
      onClick: exportChat,
    },
  ];

  // 初始化加载
  useEffect(() => {
    loadSessions();
  }, [loadSessions]);

  // 当sessionId变化时设置当前会话
  useEffect(() => {
    if (sessionId) {
      const session = sessions.find(s => s.id === sessionId);
      if (session) {
        // 使用Redux action设置当前会话
        dispatch(setCurrentSession(session));
      } else if (sessions.length > 0) {
        // 如果找不到指定的会话，跳转到第一个会话
        navigate(`/chat/${sessions[0].id}`, { replace: true });
      }
    } else {
      dispatch(setCurrentSession(null));
    }
  }, [sessionId, sessions, navigate, dispatch]);

  return (
    <Layout className="h-full bg-white">
      {/* 侧边栏 - 会话列表 */}
      <Sider
        width={320}
        collapsed={sidebarCollapsed}
        collapsedWidth={0}
        className="bg-slate-800 border-r border-gray-200 overflow-hidden"
        trigger={null}
      >
        <div className="h-full flex flex-col">
          <div className="p-4 border-b border-slate-700">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-white">对话历史</h2>
              <Button
                type="primary"
                size="small"
                onClick={createNewSession}
              >
                新对话
              </Button>
            </div>
          </div>
          
          <div className="flex-1 overflow-hidden">
            <SessionList
              sessions={sessions}
              currentSessionId={sessionId}
              onSessionSelect={handleSessionSelect}
              loading={sessionsLoading}
            />
          </div>
        </div>
      </Sider>

      {/* 主要内容区域 */}
      <Layout className="h-full">
        {/* 顶部工具栏 */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-white">
          <div className="flex items-center gap-3">
            <Button
              type="text"
              icon={sidebarCollapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
              className="text-gray-600"
            />
            <div>
              <h1 className="text-lg font-semibold text-gray-900">
                {currentSession?.title || 'TradeFlow AI 助手'}
              </h1>
              <p className="text-sm text-gray-500">
                智能贸易助手，为您提供专业的贸易咨询服务
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <SSEConnectionIndicator
              isConnected={sse.isConnected}
              isConnecting={sse.isConnecting}
              error={sse.error}
              onReconnect={() => currentSession && sse.connect(currentSession.id)}
              onDisconnect={() => sse.disconnect()}
            />
            
            <Dropdown menu={{ items: chatMenuItems }} placement="bottomRight">
              <Tooltip title="聊天设置">
                <Button
                  type="text"
                  icon={<SettingOutlined />}
                  disabled={!currentSession}
                />
              </Tooltip>
            </Dropdown>
          </div>
        </div>

        {/* 消息区域 - 使用新的ChatInterface组件 */}
        <ChatInterface sessionId={sessionId} />
      </Layout>
    </Layout>
  );
};

export default ChatPage;