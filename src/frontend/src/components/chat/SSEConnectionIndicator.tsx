import React from 'react';
import { Badge, Tooltip, Button, Popover, Space, Typography } from 'antd';
import {
  WifiOutlined,
  DisconnectOutlined,
  LoadingOutlined,
  ExclamationCircleOutlined,
  ReloadOutlined,
} from '@ant-design/icons';

const { Text } = Typography;

interface SSEConnectionIndicatorProps {
  isConnected: boolean;
  isConnecting: boolean;
  error: string | null;
  onReconnect?: () => void;
  onDisconnect?: () => void;
  className?: string;
}

const SSEConnectionIndicator: React.FC<SSEConnectionIndicatorProps> = ({
  isConnected,
  isConnecting,
  error,
  onReconnect,
  onDisconnect,
  className = '',
}) => {
  // 获取连接状态信息
  const getConnectionStatus = () => {
    if (isConnecting) {
      return {
        status: 'processing' as const,
        text: '连接中',
        color: '#1890ff',
        icon: <LoadingOutlined className="animate-spin" />,
        description: '正在建立与服务器的连接...',
      };
    } else if (isConnected) {
      return {
        status: 'success' as const,
        text: '已连接',
        color: '#52c41a',
        icon: <WifiOutlined />,
        description: '与服务器连接正常，可以正常使用实时功能',
      };
    } else if (error) {
      return {
        status: 'error' as const,
        text: '连接异常',
        color: '#ff4d4f',
        icon: <ExclamationCircleOutlined />,
        description: error,
      };
    } else {
      return {
        status: 'default' as const,
        text: '已断开',
        color: '#d9d9d9',
        icon: <DisconnectOutlined />,
        description: '未连接到服务器',
      };
    }
  };

  const connectionStatus = getConnectionStatus();

  // 连接详情面板
  const ConnectionDetails = (
    <div className="w-72 p-2">
      <div className="mb-3">
        <div className="flex items-center gap-2 mb-2">
          {connectionStatus.icon}
          <span className="font-medium">{connectionStatus.text}</span>
        </div>
        <Text className="text-sm text-gray-600">
          {connectionStatus.description}
        </Text>
      </div>

      <div className="space-y-2">
        <div className="text-xs text-gray-500">
          <div>协议: Server-Sent Events (SSE)</div>
          <div>用途: 实时消息推送</div>
          {error && (
            <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-red-700">
              错误详情: {error}
            </div>
          )}
        </div>

        {/* 操作按钮 */}
        <div className="pt-2 border-t border-gray-200">
          <Space>
            {(error || !isConnected) && onReconnect && (
              <Button
                size="small"
                type="primary"
                icon={<ReloadOutlined />}
                onClick={onReconnect}
                disabled={isConnecting}
              >
                重新连接
              </Button>
            )}
            
            {isConnected && onDisconnect && (
              <Button
                size="small"
                icon={<DisconnectOutlined />}
                onClick={onDisconnect}
              >
                断开连接
              </Button>
            )}
          </Space>
        </div>
      </div>
    </div>
  );

  return (
    <Popover
      content={ConnectionDetails}
      title="连接状态"
      trigger="hover"
      placement="bottomRight"
    >
      <div className={`flex items-center gap-2 cursor-pointer ${className}`}>
        <Tooltip title={`SSE连接状态: ${connectionStatus.text}`}>
          <Badge
            status={connectionStatus.status}
            className="shrink-0"
          />
        </Tooltip>
        
        <span className="text-sm text-gray-600 hidden sm:inline">
          {connectionStatus.text}
        </span>
      </div>
    </Popover>
  );
};

export default SSEConnectionIndicator;