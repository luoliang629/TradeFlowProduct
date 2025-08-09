import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Layout, Button, message, Tooltip, Dropdown } from 'antd';
import {
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  SettingOutlined,
  ClearOutlined,
  DownloadOutlined,
} from '@ant-design/icons';
import { useParams, useNavigate } from 'react-router-dom';
import { useAppSelector } from '../store/hooks';
import SessionList from '../components/chat/SessionList';
import MessageList, { MessageListRef } from '../components/chat/MessageList';
import MessageInput from '../components/chat/MessageInput';
import SSEConnectionIndicator from '../components/chat/SSEConnectionIndicator';
import { useSSE } from '../hooks/useSSE';
import { apiService } from '../services';
import type { Message, Session } from '../types';

const { Sider, Content } = Layout;

const ChatPage: React.FC = () => {
  const navigate = useNavigate();
  const { sessionId } = useParams();
  const { user } = useAppSelector(state => state.auth);
  
  // 状态管理
  const [sessions, setSessions] = useState<Session[]>([]);
  const [currentSession, setCurrentSession] = useState<Session | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [sessionsLoading, setSessionsLoading] = useState(true);
  
  // Refs
  const messageListRef = useRef<MessageListRef>(null);
  
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

  // 加载消息历史
  const loadMessages = useCallback(async (sessionId: string) => {
    try {
      const response = await apiService.messages.getHistory(sessionId);
      if (response.success) {
        setMessages(response.data || []);
        
        // 滚动到底部
        setTimeout(() => {
          messageListRef.current?.scrollToBottom();
        }, 100);
      }
    } catch (error) {
      console.error('加载消息历史失败:', error);
      message.error('加载消息历史失败');
    }
  }, []);

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

  // 发送消息
  const handleSendMessage = async (content: string, files?: File[]) => {
    if (!currentSession) {
      // 如果没有当前会话，创建新会话
      await createNewSession();
      return;
    }

    const tempMessage: Message = {
      id: `temp_${Date.now()}`,
      content,
      role: 'user',
      timestamp: new Date().toISOString(),
      status: 'sending',
      files: files?.map(f => ({ name: f.name, size: f.size, type: f.type })),
    };

    // 添加临时消息
    setMessages(prev => [...prev, tempMessage]);
    
    try {
      setLoading(true);
      
      // 发送消息
      const response = await apiService.messages.send(content, currentSession.id, files);
      if (response.success) {
        const sentMessage = response.data;
        
        // 更新消息状态
        setMessages(prev =>
          prev.map(msg =>
            msg.id === tempMessage.id
              ? { ...sentMessage, status: 'sent' }
              : msg
          )
        );
        
        // 如果SSE连接正常，等待实时响应；否则使用模拟响应
        if (sse.isConnected) {
          // 通过SSE接收响应
          console.log('等待SSE响应...');
        } else {
          // 模拟AI响应
          setTimeout(() => {
            const aiMessage: Message = {
              id: `ai_${Date.now()}`,
              content: `收到您的消息："${content}"。我是TradeFlow AI助手，很高兴为您服务！\n\n请问我可以如何帮助您？我可以为您提供：\n\n- 🔍 买家开发和推荐\n- 📊 供应商搜索和分析\n- 📈 市场趋势分析\n- 💼 贸易政策解读\n- 📋 合同模板生成\n\n请告诉我您需要什么帮助！`,
              role: 'assistant',
              timestamp: new Date().toISOString(),
              status: 'sent',
            };
            
            setMessages(prev => [...prev, aiMessage]);
            setLoading(false);
          }, 2000);
        }
      }
    } catch (error) {
      // 标记消息发送失败
      setMessages(prev =>
        prev.map(msg =>
          msg.id === tempMessage.id
            ? { ...msg, status: 'error', error: true }
            : msg
        )
      );
      setLoading(false);
      message.error('消息发送失败');
    }
  };

  // 重试消息
  const handleRetryMessage = (messageId: string) => {
    const message = messages.find(m => m.id === messageId);
    if (message && message.role === 'user') {
      handleSendMessage(message.content, message.files?.map(f => new File([], f.name)));
    }
  };

  // 复制消息内容
  const handleCopyMessage = (content: string) => {
    message.success('内容已复制到剪贴板');
  };

  // 选择会话
  const handleSessionSelect = (session: Session) => {
    navigate(`/chat/${session.id}`);
  };

  // 清空当前对话
  const clearCurrentChat = () => {
    if (currentSession) {
      setMessages([]);
      message.success('对话已清空');
    }
  };

  // 导出对话
  const exportChat = () => {
    if (messages.length === 0) {
      message.warning('没有对话内容可导出');
      return;
    }
    
    const chatContent = messages
      .map(msg => `${msg.role === 'user' ? '用户' : 'AI助手'}: ${msg.content}`)
      .join('\n\n');
    
    const blob = new Blob([chatContent], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${currentSession?.title || '对话记录'}_${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    message.success('对话已导出');
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

  // 当sessionId变化时加载对应的会话和消息
  useEffect(() => {
    if (sessionId) {
      const session = sessions.find(s => s.id === sessionId);
      if (session) {
        setCurrentSession(session);
        loadMessages(sessionId);
        
        // 建立SSE连接
        if (!sse.isConnected && !sse.isConnecting) {
          sse.connect(sessionId);
        }
      } else if (sessions.length > 0) {
        // 如果找不到指定的会话，跳转到第一个会话
        navigate(`/chat/${sessions[0].id}`, { replace: true });
      }
    } else {
      setCurrentSession(null);
      setMessages([]);
      sse.disconnect();
    }
  }, [sessionId, sessions, navigate, loadMessages, sse]);

  // 监听SSE消息
  useEffect(() => {
    if (sse.lastMessage) {
      const sseMessage = sse.lastMessage;
      
      switch (sseMessage.type) {
        case 'message_chunk':
          // 处理流式消息块
          if (sseMessage.messageId && sseMessage.content) {
            setMessages(prev => {
              const existingIndex = prev.findIndex(m => m.id === sseMessage.messageId);
              
              if (existingIndex >= 0) {
                // 更新现有消息
                const updated = [...prev];
                updated[existingIndex] = {
                  ...updated[existingIndex],
                  content: updated[existingIndex].content + sseMessage.content,
                };
                return updated;
              } else {
                // 创建新消息
                const newMessage: Message = {
                  id: sseMessage.messageId,
                  content: sseMessage.content,
                  role: 'assistant',
                  timestamp: new Date().toISOString(),
                  status: 'sending',
                };
                return [...prev, newMessage];
              }
            });
          }
          break;
          
        case 'message_complete':
          // 标记消息完成
          if (sseMessage.messageId) {
            setMessages(prev =>
              prev.map(m =>
                m.id === sseMessage.messageId
                  ? { ...m, status: 'sent' }
                  : m
              )
            );
            setLoading(false);
          }
          break;
          
        case 'error':
          message.error(sseMessage.error || '消息处理失败');
          setLoading(false);
          break;
      }
    }
  }, [sse.lastMessage]);

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

        {/* 消息区域 */}
        <Content className="flex flex-col bg-gray-50">
          <MessageList
            ref={messageListRef}
            messages={messages}
            loading={loading}
            user={user}
            onRetry={handleRetryMessage}
            onCopy={handleCopyMessage}
          />

          {/* 输入区域 */}
          <div className="p-4 bg-white border-t border-gray-200">
            <div className="max-w-4xl mx-auto">
              <MessageInput
                onSendMessage={handleSendMessage}
                loading={loading}
                placeholder="输入您的问题，我是专业的贸易助手..."
                showFileUpload={true}
                showEmoji={true}
              />
            </div>
          </div>
        </Content>
      </Layout>
    </Layout>
  );
};

export default ChatPage;