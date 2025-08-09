import React, { useState, useRef, useEffect } from 'react';
import { Layout, Card, Empty, Spin, message } from 'antd';
import { RobotOutlined } from '@ant-design/icons';
import MessageList from './MessageList';
import ChatInput from './ChatInput';
import { useAppDispatch, useAppSelector } from '../../store/hooks';
import { sendMessage, setCurrentSession, fetchMessages } from '../../store/chatSlice';
import { apiService } from '../../services';
import type { Message } from '../../types';

const { Content } = Layout;

interface ChatInterfaceProps {
  sessionId?: string;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ sessionId }) => {
  const dispatch = useAppDispatch();
  const { currentSession, messages, loading } = useAppSelector(state => state.chat);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingMessage, setStreamingMessage] = useState<string>('');
  const messageListRef = useRef<HTMLDivElement>(null);
  const sseRef = useRef<EventSource | null>(null);

  // 加载会话消息
  useEffect(() => {
    if (sessionId && sessionId !== currentSession?.id) {
      dispatch(fetchMessages(sessionId));
    }
  }, [sessionId, currentSession?.id, dispatch]);

  // 建立SSE连接
  const connectSSE = (sessionId: string) => {
    const token = localStorage.getItem('token');
    if (!token) return;

    // 关闭现有连接
    if (sseRef.current) {
      sseRef.current.close();
    }

    try {
      const eventSource = apiService.sse.connect(sessionId, token);
      
      eventSource.addEventListener('message', (event) => {
        const data = JSON.parse(event.data);
        
        switch (data.type) {
          case 'message_chunk':
            setStreamingMessage(prev => prev + data.content);
            break;
          case 'message_complete':
            setStreamingMessage('');
            setIsStreaming(false);
            // 刷新消息列表
            dispatch(fetchMessages(sessionId));
            break;
          case 'error':
            message.error(data.message || '处理消息时出错');
            setIsStreaming(false);
            break;
        }
      });

      eventSource.addEventListener('error', () => {
        message.error('连接中断，正在重连...');
        setIsStreaming(false);
        // 尝试重连
        setTimeout(() => {
          if (currentSession?.id) {
            connectSSE(currentSession.id);
          }
        }, 3000);
      });

      sseRef.current = eventSource;
    } catch (error) {
      console.error('SSE连接失败:', error);
      message.error('无法建立实时连接');
    }
  };

  // 组件卸载时清理SSE连接
  useEffect(() => {
    return () => {
      if (sseRef.current) {
        sseRef.current.close();
      }
    };
  }, []);

  // 发送消息
  const handleSendMessage = async (content: string, files?: File[]) => {
    if (!currentSession) {
      message.warning('请先创建或选择一个会话');
      return;
    }

    try {
      setIsStreaming(true);
      setStreamingMessage('');
      
      // 发送消息到后端
      await dispatch(sendMessage({ 
        content, 
        sessionId: currentSession.id,
        files 
      })).unwrap();

      // 建立SSE连接接收流式响应
      connectSSE(currentSession.id);
      
      // 滚动到底部
      setTimeout(() => {
        messageListRef.current?.scrollTo({
          top: messageListRef.current.scrollHeight,
          behavior: 'smooth'
        });
      }, 100);
    } catch (error) {
      console.error('发送消息失败:', error);
      message.error('发送失败，请重试');
      setIsStreaming(false);
    }
  };

  // 处理文件上传
  const handleFileUpload = async (files: File[]) => {
    const maxSize = 10 * 1024 * 1024; // 10MB
    const oversizedFiles = files.filter(file => file.size > maxSize);
    
    if (oversizedFiles.length > 0) {
      message.warning(`以下文件超过10MB限制：${oversizedFiles.map(f => f.name).join(', ')}`);
      return;
    }

    // 文件将随消息一起发送
    return files;
  };

  // 如果没有当前会话，显示欢迎界面
  if (!currentSession) {
    return (
      <Content className="flex items-center justify-center h-full bg-gray-50">
        <Card className="text-center max-w-md">
          <RobotOutlined className="text-6xl text-blue-500 mb-4" />
          <h2 className="text-2xl font-bold mb-2">欢迎使用 TradeFlow AI 助手</h2>
          <p className="text-gray-600 mb-4">
            我是您的智能贸易助手，可以帮您：
          </p>
          <ul className="text-left text-gray-600 space-y-2 mb-6">
            <li>• 寻找全球优质买家</li>
            <li>• 筛选可靠供应商</li>
            <li>• 分析市场趋势</li>
            <li>• 生成商务文档</li>
          </ul>
          <p className="text-sm text-gray-500">
            点击左侧"新建对话"开始
          </p>
        </Card>
      </Content>
    );
  }

  return (
    <Content className="flex flex-col h-full bg-gray-50">
      {/* 消息列表 */}
      <div 
        ref={messageListRef}
        className="flex-1 overflow-y-auto px-4 py-6"
      >
        {loading && messages.length === 0 ? (
          <div className="flex justify-center items-center h-full">
            <Spin size="large" tip="加载中..." />
          </div>
        ) : messages.length === 0 ? (
          <Empty
            description="暂无消息"
            className="mt-20"
          />
        ) : (
          <MessageList 
            messages={messages}
            streamingMessage={isStreaming ? streamingMessage : undefined}
          />
        )}
      </div>

      {/* 输入框 */}
      <div className="border-t bg-white px-4 py-3">
        <ChatInput
          onSendMessage={handleSendMessage}
          onFileUpload={handleFileUpload}
          disabled={isStreaming}
          placeholder={isStreaming ? 'AI正在思考中...' : '输入消息，按Enter发送'}
        />
      </div>
    </Content>
  );
};

export default ChatInterface;