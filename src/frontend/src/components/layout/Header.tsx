import { Layout, Button, Space, Dropdown, Avatar, Badge, Tooltip, Typography } from 'antd';
import { 
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  FileTextOutlined,
  BellOutlined,
  SettingOutlined,
  UserOutlined,
  LogoutOutlined,
  GlobalOutlined,
} from '@ant-design/icons';
import type { MenuProps } from 'antd';
import { useAppSelector, useAppDispatch } from '../../store/hooks';
import { toggleSidebar, toggleFilePreviewPanel, toggleTheme } from '../../store/uiSlice';
import { logout } from '../../store/authSlice';

const { Header: AntHeader } = Layout;
const { Text } = Typography;

const Header: React.FC = () => {
  const dispatch = useAppDispatch();
  const { sidebarCollapsed, filePreviewPanelOpen, theme, language } = useAppSelector(state => state.ui);
  const { user, isAuthenticated } = useAppSelector(state => state.auth);

  // 用户菜单
  const userMenuItems: MenuProps['items'] = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '个人资料',
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: '账户设置',
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      onClick: () => dispatch(logout()),
    },
  ];

  // 语言切换菜单
  const languageMenuItems: MenuProps['items'] = [
    {
      key: 'zh',
      label: '中文',
    },
    {
      key: 'en',
      label: 'English',
    },
  ];

  return (
    <AntHeader 
      className="bg-white border-b border-gray-200 px-4 flex items-center justify-between h-16"
      style={{
        position: 'sticky',
        top: 0,
        zIndex: 10,
        width: '100%',
        backgroundColor: theme === 'dark' ? '#1f1f1f' : '#ffffff',
        borderBottomColor: theme === 'dark' ? '#404040' : '#e5e7eb',
      }}
    >
      {/* 左侧控制按钮 */}
      <Space size="middle">
        <Button
          type="text"
          icon={sidebarCollapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
          onClick={() => dispatch(toggleSidebar())}
          className="hover:bg-gray-100"
        />
        
        <div className="h-6 w-px bg-gray-300" />
        
        <Button
          type="text"
          icon={<FileTextOutlined />}
          onClick={() => dispatch(toggleFilePreviewPanel())}
          className={`hover:bg-gray-100 ${filePreviewPanelOpen ? 'text-blue-500' : ''}`}
        >
          文件预览
        </Button>
      </Space>

      {/* 中间标题区域 - 当前会话标题 */}
      <div className="flex-1 text-center">
        <Text 
          className="text-lg font-medium text-gray-800"
          style={{ color: theme === 'dark' ? '#ffffff' : '#1f2937' }}
        >
          TradeFlow AI 助手
        </Text>
      </div>

      {/* 右侧用户操作区域 */}
      <Space size="middle">
        {/* 语言切换 */}
        <Dropdown menu={{ items: languageMenuItems }}>
          <Button
            type="text"
            icon={<GlobalOutlined />}
            className="hover:bg-gray-100"
          >
            {language === 'zh' ? '中' : 'EN'}
          </Button>
        </Dropdown>

        {/* 通知 */}
        <Tooltip title="通知">
          <Badge count={3} size="small">
            <Button
              type="text"
              icon={<BellOutlined />}
              className="hover:bg-gray-100"
            />
          </Badge>
        </Tooltip>

        {/* 主题切换 */}
        <Tooltip title={theme === 'dark' ? '切换到亮色模式' : '切换到暗色模式'}>
          <Button
            type="text"
            onClick={() => dispatch(toggleTheme())}
            className="hover:bg-gray-100"
          >
            {theme === 'dark' ? '🌞' : '🌙'}
          </Button>
        </Tooltip>

        {/* 用户菜单 */}
        {isAuthenticated && user && (
          <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
            <div className="flex items-center gap-2 cursor-pointer hover:bg-gray-100 px-2 py-1 rounded">
              <Avatar 
                size={32}
                src={user.avatar}
                icon={<UserOutlined />}
                className="bg-blue-500"
              />
              <div className="hidden sm:block">
                <Text 
                  className="text-sm font-medium block"
                  style={{ color: theme === 'dark' ? '#ffffff' : '#1f2937' }}
                >
                  {user.name}
                </Text>
                <Text 
                  className="text-xs text-gray-500"
                  style={{ color: theme === 'dark' ? '#9ca3af' : '#6b7280' }}
                >
                  {user.subscription?.plan.toUpperCase() || 'FREE'}
                </Text>
              </div>
            </div>
          </Dropdown>
        )}

        {/* 未登录状态 */}
        {!isAuthenticated && (
          <Button type="primary" size="small">
            登录
          </Button>
        )}
      </Space>
    </AntHeader>
  );
};

export default Header;