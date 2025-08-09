import { Layout, Button, Input, Space, Typography, Avatar, Badge, Tooltip } from 'antd';
import { 
  PlusOutlined, 
  SearchOutlined,
  SettingOutlined,
  UserOutlined,
  CreditCardOutlined,
  QuestionCircleOutlined
} from '@ant-design/icons';
import { useState, useEffect } from 'react';
import { useAppSelector, useAppDispatch } from '../../store/hooks';
import { createNewSession, setCurrentSession, fetchSessions } from '../../store/chatSlice';
import SessionList from '../chat/SessionList';
import MainNavigation from '../navigation/MainNavigation';

const { Sider } = Layout;
const { Text } = Typography;

interface SidebarProps {
  collapsed?: boolean;
}

const Sidebar: React.FC<SidebarProps> = ({ collapsed = false }) => {
  const dispatch = useAppDispatch();
  const { sessions, currentSession, loading } = useAppSelector(state => state.chat);
  const { user } = useAppSelector(state => state.auth);
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredSessions, setFilteredSessions] = useState(sessions);

  // 组件加载时获取会话列表
  useEffect(() => {
    dispatch(fetchSessions());
  }, [dispatch]);

  // 过滤会话
  useEffect(() => {
    if (searchQuery.trim()) {
      const filtered = sessions.filter(session =>
        session.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        session.last_message_preview?.toLowerCase().includes(searchQuery.toLowerCase())
      );
      setFilteredSessions(filtered);
    } else {
      setFilteredSessions(sessions);
    }
  }, [searchQuery, sessions]);

  // 创建新会话
  const handleCreateNewSession = async () => {
    try {
      const newSession = await dispatch(createNewSession()).unwrap();
      dispatch(setCurrentSession(newSession));
    } catch (error) {
      console.error('创建会话失败:', error);
    }
  };

  return (
    <Sider
      width={280}
      collapsedWidth={0}
      collapsed={collapsed}
      className="bg-slate-900 border-r border-slate-700"
      style={{
        overflow: 'hidden',
        height: '100vh',
        position: 'fixed',
        left: 0,
        top: 0,
        bottom: 0,
        zIndex: 100,
      }}
    >
      <div className="flex flex-col h-full">
        {/* 顶部Logo和新建按钮 */}
        <div className="p-4 border-b border-slate-700">
          <div className="flex items-center justify-between mb-4">
            <div>
              <Text className="text-white text-lg font-bold">TradeFlow</Text>
              <div className="text-slate-400 text-xs mt-1">AI贸易助手</div>
            </div>
          </div>
          
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleCreateNewSession}
            loading={loading}
            className="w-full h-10"
            style={{
              backgroundColor: 'var(--primary-color)',
              borderColor: 'var(--primary-color)',
            }}
          >
            新建对话
          </Button>
        </div>

        {/* 主导航菜单 */}
        <div className="flex-1 overflow-hidden">
          <MainNavigation 
            collapsed={collapsed} 
            theme="dark"
            className="bg-transparent border-0"
          />
        </div>

        {/* 聊天会话区域 - 可折叠 */}
        {!collapsed && (
          <>
            <div className="px-4 py-2 border-t border-slate-700">
              <Text className="text-slate-400 text-xs font-medium">
                最近对话
              </Text>
            </div>

            {/* 搜索框 */}
            <div className="px-4 pb-2">
              <Input
                placeholder="搜索对话..."
                prefix={<SearchOutlined className="text-slate-400" />}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="bg-slate-800 border-slate-600 text-white"
                size="small"
                style={{
                  backgroundColor: 'rgb(30 41 59)',
                  borderColor: 'rgb(71 85 105)',
                  color: 'white',
                }}
              />
            </div>

            {/* 会话列表 */}
            <div className="flex-1 overflow-hidden max-h-60">
              <SessionList
                sessions={filteredSessions.slice(0, 5)} // 只显示最近5个会话
                currentSessionId={currentSession?.id}
                onSessionSelect={(session) => dispatch(setCurrentSession(session))}
                loading={loading}
              />
            </div>
          </>
        )}

        {/* 底部用户信息和设置 */}
        <div className="p-4 border-t border-slate-700">
          {/* 用户信息 */}
          <div className="flex items-center gap-3 mb-4">
            <Avatar 
              size={40}
              icon={<UserOutlined />}
              src={user?.avatar}
              className="bg-slate-600"
            />
            <div className="flex-1 min-w-0">
              <Text className="text-white text-sm font-medium block truncate">
                {user?.name || '未登录'}
              </Text>
              <Text className="text-slate-400 text-xs block truncate">
                {user?.email}
              </Text>
            </div>
          </div>

          {/* 使用情况 */}
          {user?.subscription && (
            <div className="mb-4 p-3 bg-slate-800 rounded-lg">
              <div className="flex justify-between items-center mb-2">
                <Text className="text-slate-300 text-xs">本月使用</Text>
                <Badge 
                  count={user.subscription.plan.toUpperCase()} 
                  className="bg-orange-500"
                />
              </div>
              <div className="w-full bg-slate-700 rounded-full h-2">
                <div 
                  className="bg-gradient-to-r from-blue-500 to-blue-600 h-2 rounded-full transition-all"
                  style={{ 
                    width: `${(user.subscription.credits_used / user.subscription.credits_limit) * 100}%` 
                  }}
                />
              </div>
              <Text className="text-slate-400 text-xs mt-1">
                {user.subscription.credits_used} / {user.subscription.credits_limit} 积分
              </Text>
            </div>
          )}

          {/* 底部操作按钮 */}
          <Space className="w-full justify-between">
            <Tooltip title="账户设置">
              <Button
                type="text"
                icon={<SettingOutlined />}
                className="text-slate-400 hover:text-white hover:bg-slate-700"
                size="small"
              />
            </Tooltip>
            
            <Tooltip title="订阅管理">
              <Button
                type="text"
                icon={<CreditCardOutlined />}
                className="text-slate-400 hover:text-white hover:bg-slate-700"
                size="small"
              />
            </Tooltip>
            
            <Tooltip title="帮助中心">
              <Button
                type="text"
                icon={<QuestionCircleOutlined />}
                className="text-slate-400 hover:text-white hover:bg-slate-700"
                size="small"
              />
            </Tooltip>
          </Space>
        </div>
      </div>
    </Sider>
  );
};

export default Sidebar;