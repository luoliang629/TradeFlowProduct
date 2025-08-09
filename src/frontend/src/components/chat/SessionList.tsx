import { List, Button, Dropdown, Typography, Badge, Empty, Spin } from 'antd';
import { 
  MessageOutlined, 
  MoreOutlined, 
  EditOutlined, 
  DeleteOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons';
import { useState } from 'react';
import type { MenuProps } from 'antd';
import type { Session } from '../../types';

const { Text } = Typography;

interface SessionListProps {
  sessions: Session[];
  currentSessionId?: string;
  onSessionSelect: (session: Session) => void;
  loading?: boolean;
}

const SessionList: React.FC<SessionListProps> = ({
  sessions,
  currentSessionId,
  onSessionSelect,
  loading = false,
}) => {
  const [_editingSessionId, setEditingSessionId] = useState<string | null>(null);

  // 会话操作菜单
  const getSessionMenuItems = (session: Session): MenuProps['items'] => [
    {
      key: 'edit',
      icon: <EditOutlined />,
      label: '重命名',
      onClick: () => setEditingSessionId(session.id),
    },
    {
      type: 'divider',
    },
    {
      key: 'delete',
      icon: <DeleteOutlined />,
      label: '删除会话',
      danger: true,
      onClick: () => handleDeleteSession(session),
    },
  ];

  // 删除会话
  const handleDeleteSession = (session: Session) => {
    // TODO: 实现删除确认和API调用
    console.log('删除会话:', session.id);
  };

  // 格式化时间
  const formatTime = (timestamp: string) => {
    const now = new Date();
    const messageTime = new Date(timestamp);
    const diffInMinutes = Math.floor((now.getTime() - messageTime.getTime()) / (1000 * 60));
    
    if (diffInMinutes < 1) return '刚刚';
    if (diffInMinutes < 60) return `${diffInMinutes}分钟前`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}小时前`;
    return messageTime.toLocaleDateString();
  };

  // 截断文本
  const truncateText = (text: string, maxLength: number = 50) => {
    return text.length > maxLength ? text.slice(0, maxLength) + '...' : text;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-32">
        <Spin />
      </div>
    );
  }

  if (sessions.length === 0) {
    return (
      <div className="p-4">
        <Empty
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          description="暂无对话"
          className="mt-8"
        />
      </div>
    );
  }

  return (
    <div className="overflow-y-auto h-full">
      <List
        size="small"
        dataSource={sessions}
        split={false}
        renderItem={(session) => (
          <List.Item
            className={`cursor-pointer px-4 py-3 hover:bg-slate-700 transition-colors ${
              currentSessionId === session.id 
                ? 'bg-slate-700 border-r-2 border-blue-500' 
                : ''
            }`}
            onClick={() => onSessionSelect(session)}
            style={{
              borderBottom: 'none',
            }}
          >
            <div className="w-full">
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2 flex-1 min-w-0">
                  <MessageOutlined className="text-slate-400 text-sm flex-shrink-0" />
                  <Text 
                    className="text-white text-sm font-medium truncate"
                    title={session.title}
                  >
                    {truncateText(session.title)}
                  </Text>
                </div>
                <Dropdown 
                  menu={{ items: getSessionMenuItems(session) }}
                  trigger={['click']}
                  placement="bottomRight"
                >
                  <Button
                    type="text"
                    size="small"
                    icon={<MoreOutlined />}
                    className="text-slate-400 hover:text-white hover:bg-slate-600 opacity-0 group-hover:opacity-100"
                    onClick={(e) => e.stopPropagation()}
                  />
                </Dropdown>
              </div>
              
              {/* 最后一条消息预览 */}
              {session.last_message_preview && (
                <Text 
                  className="text-slate-400 text-xs block mb-2 leading-relaxed"
                  title={session.last_message_preview}
                >
                  {truncateText(session.last_message_preview, 60)}
                </Text>
              )}
              
              {/* 底部信息 */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-1">
                    <ClockCircleOutlined className="text-slate-500 text-xs" />
                    <Text className="text-slate-500 text-xs">
                      {formatTime(session.updated_at)}
                    </Text>
                  </div>
                  
                  {session.message_count > 0 && (
                    <Badge 
                      count={session.message_count} 
                      size="small"
                      className="bg-slate-600"
                      style={{
                        backgroundColor: '#475569',
                        color: '#e2e8f0',
                        fontSize: '10px',
                      }}
                    />
                  )}
                </div>
                
                {/* 会话状态指示器 */}
                {currentSessionId === session.id && (
                  <div className="w-2 h-2 bg-blue-500 rounded-full" />
                )}
              </div>
            </div>
          </List.Item>
        )}
      />
    </div>
  );
};

export default SessionList;