import React, { forwardRef } from 'react';
import { Avatar, Card, Typography, Space, Tooltip, Button, Tag } from 'antd';
import {
  UserOutlined,
  RobotOutlined,
  CopyOutlined,
  CheckOutlined,
  FileTextOutlined,
  DownloadOutlined,
} from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';
import type { Message } from '../../types';

const { Text, Paragraph } = Typography;

interface MessageListProps {
  messages: Message[];
  streamingMessage?: string;
  onCopyMessage?: (content: string) => void;
}

const MessageList = forwardRef<HTMLDivElement, MessageListProps>(
  ({ messages, streamingMessage, onCopyMessage }, ref) => {
    const [copiedId, setCopiedId] = React.useState<string | null>(null);

    const handleCopy = (content: string, messageId: string) => {
      navigator.clipboard.writeText(content);
      setCopiedId(messageId);
      setTimeout(() => setCopiedId(null), 2000);
      onCopyMessage?.(content);
    };

    const formatTime = (timestamp: string) => {
      const date = new Date(timestamp);
      return date.toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit',
      });
    };

    const renderMessage = (message: Message) => {
      const isUser = message.role === 'user';
      
      return (
        <div
          key={message.id}
          className={`flex gap-3 mb-6 ${isUser ? 'flex-row-reverse' : ''}`}
        >
          {/* 头像 */}
          <Avatar
            size={36}
            icon={isUser ? <UserOutlined /> : <RobotOutlined />}
            className={isUser ? 'bg-blue-500' : 'bg-green-500'}
          />

          {/* 消息内容 */}
          <div className={`flex-1 max-w-3xl ${isUser ? 'text-right' : ''}`}>
            {/* 发送者和时间 */}
            <div className="flex items-center gap-2 mb-1">
              {!isUser && (
                <Text className="font-medium text-gray-700">AI 助手</Text>
              )}
              <Text className="text-xs text-gray-500">
                {formatTime(message.timestamp)}
              </Text>
              {isUser && (
                <Text className="font-medium text-gray-700">您</Text>
              )}
            </div>

            {/* 消息卡片 */}
            <Card
              className={`inline-block text-left ${
                isUser 
                  ? 'bg-blue-50 border-blue-200' 
                  : 'bg-white border-gray-200'
              }`}
              bodyStyle={{ padding: '12px 16px' }}
            >
              {/* 消息正文 */}
              {isUser ? (
                <Paragraph className="mb-0 whitespace-pre-wrap">
                  {message.content}
                </Paragraph>
              ) : (
                <div className="markdown-body">
                  <ReactMarkdown
                    components={{
                      code({ node, inline, className, children, ...props }) {
                        const match = /language-(\w+)/.exec(className || '');
                        return !inline && match ? (
                          <div className="relative">
                            <SyntaxHighlighter
                              style={tomorrow}
                              language={match[1]}
                              PreTag="div"
                              {...props}
                            >
                              {String(children).replace(/\n$/, '')}
                            </SyntaxHighlighter>
                            <Button
                              size="small"
                              icon={<CopyOutlined />}
                              className="absolute top-2 right-2 opacity-70 hover:opacity-100"
                              onClick={() => handleCopy(String(children), message.id)}
                            >
                              复制
                            </Button>
                          </div>
                        ) : (
                          <code className={className} {...props}>
                            {children}
                          </code>
                        );
                      },
                      table({ children }) {
                        return (
                          <div className="overflow-x-auto my-4">
                            <table className="min-w-full border-collapse border border-gray-300">
                              {children}
                            </table>
                          </div>
                        );
                      },
                      th({ children }) {
                        return (
                          <th className="border border-gray-300 bg-gray-100 px-4 py-2 text-left">
                            {children}
                          </th>
                        );
                      },
                      td({ children }) {
                        return (
                          <td className="border border-gray-300 px-4 py-2">
                            {children}
                          </td>
                        );
                      },
                    }}
                  >
                    {message.content}
                  </ReactMarkdown>
                </div>
              )}

              {/* 附件 */}
              {message.attachments && message.attachments.length > 0 && (
                <div className="mt-3 pt-3 border-t border-gray-200">
                  <Space wrap>
                    {message.attachments.map((file, index) => (
                      <Tag
                        key={index}
                        icon={<FileTextOutlined />}
                        className="cursor-pointer"
                      >
                        <a
                          href={file.url}
                          download={file.name}
                          className="text-blue-600"
                        >
                          {file.name}
                        </a>
                      </Tag>
                    ))}
                  </Space>
                </div>
              )}

              {/* 操作按钮 */}
              {!isUser && (
                <div className="mt-3 pt-3 border-t border-gray-100">
                  <Space>
                    <Tooltip title={copiedId === message.id ? '已复制' : '复制'}>
                      <Button
                        size="small"
                        type="text"
                        icon={copiedId === message.id ? <CheckOutlined /> : <CopyOutlined />}
                        onClick={() => handleCopy(message.content, message.id)}
                      >
                        {copiedId === message.id ? '已复制' : '复制'}
                      </Button>
                    </Tooltip>
                  </Space>
                </div>
              )}
            </Card>
          </div>
        </div>
      );
    };

    return (
      <div ref={ref} className="px-4">
        {messages.map(renderMessage)}
        
        {/* 流式消息 */}
        {streamingMessage && (
          <div className="flex gap-3 mb-6">
            <Avatar
              size={36}
              icon={<RobotOutlined />}
              className="bg-green-500"
            />
            <div className="flex-1 max-w-3xl">
              <div className="flex items-center gap-2 mb-1">
                <Text className="font-medium text-gray-700">AI 助手</Text>
                <Text className="text-xs text-gray-500">正在输入...</Text>
              </div>
              <Card
                className="inline-block text-left bg-white border-gray-200"
                bodyStyle={{ padding: '12px 16px' }}
              >
                <div className="markdown-body">
                  <ReactMarkdown>{streamingMessage}</ReactMarkdown>
                </div>
                <div className="typing-indicator mt-2">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </Card>
            </div>
          </div>
        )}
      </div>
    );
  }
);

MessageList.displayName = 'MessageList';

export default MessageList;