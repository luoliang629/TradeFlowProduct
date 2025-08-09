import { useState, useEffect, useRef, useCallback } from 'react';
import { message } from 'antd';
import { useAppSelector } from '../store/hooks';

export interface SSEMessage {
  type: 'message_chunk' | 'message_complete' | 'error' | 'connection' | 'heartbeat';
  content?: string;
  messageId?: string;
  error?: string;
  data?: any;
}

export interface SSEOptions {
  sessionId?: string;
  autoReconnect?: boolean;
  maxReconnectAttempts?: number;
  reconnectInterval?: number;
  heartbeatInterval?: number;
  timeout?: number;
}

export interface SSEHookReturn {
  isConnected: boolean;
  isConnecting: boolean;
  error: string | null;
  messages: SSEMessage[];
  lastMessage: SSEMessage | null;
  connect: (sessionId: string) => void;
  disconnect: () => void;
  clearMessages: () => void;
  sendHeartbeat: () => void;
}

/**
 * SSE连接Hook
 * 管理与后端的Server-Sent Events连接，支持断线重连和心跳检测
 */
export const useSSE = (options: SSEOptions = {}): SSEHookReturn => {
  const {
    autoReconnect = true,
    maxReconnectAttempts = 5,
    reconnectInterval = 3000,
    heartbeatInterval = 30000,
    timeout = 60000,
  } = options;

  const { token } = useAppSelector(state => state.auth);
  
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [messages, setMessages] = useState<SSEMessage[]>([]);
  const [lastMessage, setLastMessage] = useState<SSEMessage | null>(null);
  
  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const heartbeatIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const connectionTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const currentSessionRef = useRef<string | null>(null);

  // 清理所有定时器
  const clearTimers = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (heartbeatIntervalRef.current) {
      clearInterval(heartbeatIntervalRef.current);
      heartbeatIntervalRef.current = null;
    }
    if (connectionTimeoutRef.current) {
      clearTimeout(connectionTimeoutRef.current);
      connectionTimeoutRef.current = null;
    }
  }, []);

  // 处理连接成功
  const handleOpen = useCallback(() => {
    console.log('SSE连接已建立');
    setIsConnected(true);
    setIsConnecting(false);
    setError(null);
    reconnectAttemptsRef.current = 0;
    
    // 清除连接超时
    if (connectionTimeoutRef.current) {
      clearTimeout(connectionTimeoutRef.current);
      connectionTimeoutRef.current = null;
    }

    // 启动心跳检测
    if (heartbeatInterval > 0) {
      heartbeatIntervalRef.current = setInterval(() => {
        sendHeartbeat();
      }, heartbeatInterval);
    }

    // 发送连接确认消息
    const connectionMessage: SSEMessage = {
      type: 'connection',
      content: 'SSE connection established',
    };
    setMessages(prev => [...prev, connectionMessage]);
    setLastMessage(connectionMessage);
  }, [heartbeatInterval]);

  // 处理消息接收
  const handleMessage = useCallback((event: MessageEvent) => {
    try {
      const data = JSON.parse(event.data) as SSEMessage;
      
      console.log('收到SSE消息:', data);
      
      // 过滤心跳消息，不添加到消息列表
      if (data.type !== 'heartbeat') {
        setMessages(prev => [...prev, data]);
      }
      
      setLastMessage(data);
      
      // 处理不同类型的消息
      switch (data.type) {
        case 'error':
          setError(data.error || '服务器错误');
          message.error(data.error || '发生未知错误');
          break;
        case 'message_complete':
          console.log('消息接收完成');
          break;
      }
    } catch (err) {
      console.error('解析SSE消息失败:', err, event.data);
      setError('消息解析失败');
    }
  }, []);

  // 处理连接错误
  const handleError = useCallback((event: Event) => {
    console.error('SSE连接错误:', event);
    setIsConnected(false);
    setIsConnecting(false);
    setError('连接错误');
    
    // 清除心跳
    if (heartbeatIntervalRef.current) {
      clearInterval(heartbeatIntervalRef.current);
      heartbeatIntervalRef.current = null;
    }
  }, []);

  // 尝试重连
  const attemptReconnect = useCallback(() => {
    if (reconnectAttemptsRef.current >= maxReconnectAttempts) {
      setError(`连接失败，已达到最大重试次数 (${maxReconnectAttempts})`);
      message.error('连接失败，请刷新页面重试');
      return;
    }

    reconnectAttemptsRef.current++;
    console.log(`尝试重连... (${reconnectAttemptsRef.current}/${maxReconnectAttempts})`);
    
    reconnectTimeoutRef.current = setTimeout(() => {
      if (currentSessionRef.current) {
        connect(currentSessionRef.current);
      }
    }, reconnectInterval);
  }, [maxReconnectAttempts, reconnectInterval]);

  // 连接SSE
  const connect = useCallback((sessionId: string) => {
    if (!token) {
      setError('未授权，请先登录');
      return;
    }

    if (eventSourceRef.current && eventSourceRef.current.readyState === EventSource.OPEN) {
      console.log('SSE连接已存在，先关闭现有连接');
      disconnect();
    }

    setIsConnecting(true);
    setError(null);
    currentSessionRef.current = sessionId;

    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
      const url = `${baseUrl}/chat/stream?session_id=${sessionId}&token=${encodeURIComponent(token)}`;
      
      console.log('建立SSE连接:', url);
      
      const eventSource = new EventSource(url);
      eventSourceRef.current = eventSource;

      // 设置连接超时
      connectionTimeoutRef.current = setTimeout(() => {
        if (eventSource.readyState === EventSource.CONNECTING) {
          console.log('连接超时');
          eventSource.close();
          setError('连接超时');
          setIsConnecting(false);
          
          if (autoReconnect) {
            attemptReconnect();
          }
        }
      }, timeout);

      eventSource.onopen = handleOpen;
      eventSource.onmessage = handleMessage;
      eventSource.onerror = (event) => {
        handleError(event);
        
        // 如果启用自动重连且不是手动断开
        if (autoReconnect && eventSource.readyState === EventSource.CLOSED) {
          attemptReconnect();
        }
      };

    } catch (err) {
      console.error('创建SSE连接失败:', err);
      setError('创建连接失败');
      setIsConnecting(false);
    }
  }, [token, timeout, autoReconnect, handleOpen, handleMessage, handleError, attemptReconnect]);

  // 断开连接
  const disconnect = useCallback(() => {
    console.log('断开SSE连接');
    
    clearTimers();
    
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }

    setIsConnected(false);
    setIsConnecting(false);
    setError(null);
    reconnectAttemptsRef.current = 0;
    currentSessionRef.current = null;
  }, [clearTimers]);

  // 清除消息历史
  const clearMessages = useCallback(() => {
    setMessages([]);
    setLastMessage(null);
  }, []);

  // 发送心跳
  const sendHeartbeat = useCallback(() => {
    // 注意：SSE是单向的，我们不能通过EventSource发送数据
    // 心跳通常由服务器发送，这里只是一个占位符
    console.log('心跳检查 - SSE连接状态:', eventSourceRef.current?.readyState);
    
    // 检查连接状态
    if (eventSourceRef.current?.readyState === EventSource.CLOSED) {
      console.log('检测到连接已断开，尝试重连');
      if (autoReconnect && currentSessionRef.current) {
        attemptReconnect();
      }
    }
  }, [autoReconnect, attemptReconnect]);

  // 组件卸载时清理连接
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  // Token变化时重新连接
  useEffect(() => {
    if (currentSessionRef.current && token && isConnected) {
      console.log('Token变化，重新连接SSE');
      connect(currentSessionRef.current);
    }
  }, [token, connect, isConnected]);

  return {
    isConnected,
    isConnecting,
    error,
    messages,
    lastMessage,
    connect,
    disconnect,
    clearMessages,
    sendHeartbeat,
  };
};