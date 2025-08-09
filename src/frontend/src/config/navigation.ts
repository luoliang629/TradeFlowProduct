import { 
  HomeOutlined,
  MessageOutlined,
  ShoppingOutlined,
  TeamOutlined,
  FileTextOutlined,
  BarChartOutlined,
  SettingOutlined,
  QuestionCircleOutlined,
} from '@ant-design/icons';

export interface NavMenuItem {
  key: string;
  label: string;
  icon?: React.ComponentType;
  path?: string;
  children?: NavMenuItem[];
  permissions?: string[]; // 权限控制
  badge?: number | string; // 徽标数字
  disabled?: boolean;
}

export const navigationConfig: NavMenuItem[] = [
  {
    key: 'dashboard',
    label: '工作台',
    icon: HomeOutlined,
    path: '/',
  },
  {
    key: 'chat',
    label: 'AI助手',
    icon: MessageOutlined,
    path: '/chat',
    badge: 'NEW',
  },
  {
    key: 'trade',
    label: '贸易业务',
    icon: ShoppingOutlined,
    children: [
      {
        key: 'buyers',
        label: '买家开发',
        path: '/trade/buyers',
        permissions: ['trade:read'],
      },
      {
        key: 'suppliers',
        label: '供应商管理',
        path: '/trade/suppliers',
        permissions: ['trade:read'],
      },
      {
        key: 'products',
        label: '产品管理',
        path: '/trade/products',
        permissions: ['trade:read'],
      },
      {
        key: 'orders',
        label: '订单跟踪',
        path: '/trade/orders',
        permissions: ['trade:read'],
      },
    ],
  },
  {
    key: 'contacts',
    label: '客户管理',
    icon: TeamOutlined,
    path: '/contacts',
    permissions: ['contacts:read'],
  },
  {
    key: 'documents',
    label: '文档中心',
    icon: FileTextOutlined,
    path: '/documents',
    children: [
      {
        key: 'templates',
        label: '模板库',
        path: '/documents/templates',
      },
      {
        key: 'contracts',
        label: '合同管理',
        path: '/documents/contracts',
        permissions: ['documents:read'],
      },
      {
        key: 'reports',
        label: '分析报告',
        path: '/documents/reports',
        permissions: ['reports:read'],
      },
    ],
  },
  {
    key: 'analytics',
    label: '数据分析',
    icon: BarChartOutlined,
    path: '/analytics',
    permissions: ['analytics:read'],
  },
  {
    key: 'settings',
    label: '系统设置',
    icon: SettingOutlined,
    children: [
      {
        key: 'profile',
        label: '个人资料',
        path: '/profile',
      },
      {
        key: 'preferences',
        label: '偏好设置',
        path: '/settings/preferences',
      },
      {
        key: 'subscription',
        label: '订阅管理',
        path: '/settings/subscription',
      },
      {
        key: 'team',
        label: '团队管理',
        path: '/settings/team',
        permissions: ['admin:read'],
      },
    ],
  },
  {
    key: 'help',
    label: '帮助中心',
    icon: QuestionCircleOutlined,
    path: '/help',
  },
];

// 根据用户权限过滤菜单项
export const filterMenuByPermissions = (
  menuItems: NavMenuItem[],
  userPermissions: string[] = []
): NavMenuItem[] => {
  return menuItems
    .filter(item => {
      // 如果没有权限要求，或用户有相应权限，则显示
      if (!item.permissions || item.permissions.length === 0) {
        return true;
      }
      return item.permissions.some(permission => userPermissions.includes(permission));
    })
    .map(item => ({
      ...item,
      children: item.children
        ? filterMenuByPermissions(item.children, userPermissions)
        : undefined,
    }))
    .filter(item => !item.children || item.children.length > 0);
};