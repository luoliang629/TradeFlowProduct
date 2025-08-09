import React, { useEffect, useRef, forwardRef, useImperativeHandle } from 'react';
import { Avatar, Tooltip, Button, Space, Dropdown } from 'antd';
import {
  UserOutlined,
  RobotOutlined,
  CopyOutlined,
  RedoOutlined,
  MoreOutlined,
  CheckOutlined,
} from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';
import type { Message } from '../../types';

interface MessageListProps {
  messages: Message[];
  loading?: boolean;
  user?: any;
  onRetry?: (messageId: string) => void;
  onCopy?: (content: string) => void;
}

export interface MessageListRef {
  scrollToBottom: () => void;
}

const MessageList = forwardRef<MessageListRef, MessageListProps>(({
  messages,
  loading = false,
  user,
  onRetry,
  onCopy,
}, ref) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // 暴露滚动到底部的方法
  useImperativeHandle(ref, () => ({
    scrollToBottom: () => {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    },
  }));

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // 复制内容到剪贴板
  const handleCopy = (content: string) => {
    navigator.clipboard.writeText(content).then(() => {
      onCopy?.(content);
    });
  };

  // 重试消息
  const handleRetry = (messageId: string) => {
    onRetry?.(messageId);
  };

  // 格式化时间
  const formatTime = (timestamp: string | Date) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    
    if (diff < 60000) { // 1分钟内
      return '刚刚';
    } else if (diff < 3600000) { // 1小时内
      return `${Math.floor(diff / 60000)}分钟前`;
    } else if (diff < 86400000) { // 24小时内
      return `${Math.floor(diff / 3600000)}小时前`;
    } else {
      return date.toLocaleDateString();
    }
  };

  // 消息操作菜单
  const getMessageActions = (message: Message) => [
    {
      key: 'copy',
      label: '复制',
      icon: <CopyOutlined />,
      onClick: () => handleCopy(message.content),
    },
    ...(message.role === 'assistant' && message.error ? [{
      key: 'retry',
      label: '重试',
      icon: <RedoOutlined />,
      onClick: () => handleRetry(message.id),
    }] : []),
  ];

  // Markdown组件配置
  const MarkdownComponents = {
    code: ({ node, inline, className, children, ...props }: any) => {
      const match = /language-(\w+)/.exec(className || '');
      const language = match ? match[1] : '';
      
      if (!inline && language) {
        return (
          <div className="relative">
            <SyntaxHighlighter
              style={tomorrow}
              language={language}
              PreTag="div"
              className="rounded-md"
              {...props}
            >
              {String(children).replace(/\n$/, '')}
            </SyntaxHighlighter>
            <Button
              size="small"
              type="text"
              icon={<CopyOutlined />}
              className="absolute top-2 right-2 opacity-70 hover:opacity-100"
              onClick={() => handleCopy(String(children))}
            />
          </div>
        );
      }
      
      return (
        <code className="bg-gray-100 px-1 py-0.5 rounded text-sm" {...props}>
          {children}
        </code>
      );
    },
    table: ({ children }: any) => (
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200 border border-gray-300">
          {children}
        </table>
      </div>
    ),
    th: ({ children }: any) => (
      <th className="px-4 py-2 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border-b border-gray-200">
        {children}
      </th>
    ),
    td: ({ children }: any) => (
      <td className="px-4 py-2 text-sm text-gray-900 border-b border-gray-200">
        {children}
      </td>
    ),
  };

  if (messages.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center text-gray-500">
        <div className="text-center">
          <RobotOutlined className="text-6xl mb-4 text-gray-300" />
          <h3 className="text-lg font-medium mb-2">开始新对话</h3>
          <p className="text-sm">向TradeFlow AI助手提问，获取专业的贸易建议</p>
        </div>
      </div>
    );
  }

  return (
    <div 
      ref={containerRef}
      className="flex-1 overflow-y-auto p-4 space-y-4"
      style={{ height: 'calc(100vh - 200px)' }}
    >
      {messages.map((message) => {
        const isUser = message.role === 'user';
        const isError = message.error;
        
        return (
          <div
            key={message.id}
            className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}
          >
            {/* 助手头像 */}
            {!isUser && (
              <Avatar
                size={40}
                icon={<RobotOutlined />}
                className="bg-blue-500 shrink-0"
              />
            )}
            
            <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'} max-w-3xl`}>
              {/* 消息内容 */}
              <div
                className={`relative group px-4 py-3 rounded-lg ${
                  isUser
                    ? 'bg-blue-500 text-white'
                    : isError
                    ? 'bg-red-50 border border-red-200 text-red-800'
                    : 'bg-white border border-gray-200'
                }`}
              >
                {/* 消息操作按钮 */}
                <div className={`absolute ${isUser ? '-left-10' : '-right-10'} top-2 opacity-0 group-hover:opacity-100 transition-opacity`}>
                  <Dropdown
                    menu={{ items: getMessageActions(message) }}
                    trigger={['click']}
                    placement={isUser ? 'bottomRight' : 'bottomLeft'}
                  >
                    <Button
                      type="text"
                      size="small"
                      icon={<MoreOutlined />}
                      className="text-gray-400 hover:text-gray-600"
                    />
                  </Dropdown>
                </div>

                {/* 消息文本 */}
                {isUser ? (
                  <div className="whitespace-pre-wrap break-words">
                    {message.content}
                  </div>
                ) : (
                  <div className="prose prose-sm max-w-none">
                    {isError ? (
                      <div className="flex items-center gap-2">
                        <span>消息发送失败</span>
                        <Button
                          size="small"
                          type="link"
                          onClick={() => handleRetry(message.id)}
                          className="p-0 h-auto text-red-600"
                        >
                          重试
                        </Button>
                      </div>
                    ) : (
                      <ReactMarkdown components={MarkdownComponents}>
                        {message.content}
                      </ReactMarkdown>
                    )}
                  </div>
                )}

                {/* 文件附件 */}
                {message.files && message.files.length > 0 && (
                  <div className="mt-2 space-y-2">
                    {message.files.map((file, index) => (
                      <div
                        key={index}
                        className="flex items-center gap-2 p-2 bg-gray-100 rounded text-sm"
                      >
                        <span>{file.name}</span>
                        <span className="text-gray-500">({(file.size / 1024).toFixed(1)} KB)</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              
              {/* 时间戳和状态 */}
              <div className={`flex items-center gap-2 mt-1 text-xs text-gray-500 ${isUser ? 'flex-row-reverse' : ''}`}>
                <Tooltip title={new Date(message.timestamp).toLocaleString()}>
                  <span>{formatTime(message.timestamp)}</span>
                </Tooltip>
                
                {/* 消息状态 */}
                {isUser && (
                  <div className="flex items-center gap-1">
                    {message.status === 'sending' && (
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse" />
                    )}
                    {message.status === 'sent' && (
                      <CheckOutlined className="w-3 h-3 text-green-500" />
                    )}
                    {message.status === 'error' && (
                      <div className="w-2 h-2 bg-red-500 rounded-full" />
                    )}
                  </div>
                )}
              </div>
            </div>
            
            {/* 用户头像 */}
            {isUser && (
              <Avatar
                size={40}
                src={user?.avatar}
                icon={<UserOutlined />}
                className="shrink-0"
              />
            )}
          </div>
        );
      })}
      
      {/* 加载指示器 */}
      {loading && (
        <div className="flex items-start gap-3">
          <Avatar
            size={40}
            icon={<RobotOutlined />}
            className="bg-blue-500 shrink-0"
          />
          <div className="bg-white border border-gray-200 rounded-lg px-4 py-3">
            <div className="flex items-center gap-2">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
              </div>
              <span className="text-sm text-gray-500">AI助手正在思考...</span>
            </div>
          </div>
        </div>
      )}
      
      {/* 滚动锚点 */}
      <div ref={messagesEndRef} />
    </div>
  );
});

MessageList.displayName = 'MessageList';

export default MessageList;