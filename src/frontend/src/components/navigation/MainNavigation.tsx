import React from 'react';
import { Menu, Badge } from 'antd';
import { useLocation, useNavigate } from 'react-router-dom';
import { useState, useEffect, useMemo } from 'react';
import type { MenuProps } from 'antd';
import { useAppSelector } from '../../store/hooks';
import { navigationConfig, filterMenuByPermissions } from '../../config/navigation';
import type { NavMenuItem } from '../../config/navigation';

interface MainNavigationProps {
  collapsed?: boolean;
  theme?: 'light' | 'dark';
  className?: string;
}

type MenuItem = Required<MenuProps>['items'][number];

const MainNavigation: React.FC<MainNavigationProps> = ({
  collapsed = false,
  theme = 'dark',
  className,
}) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAppSelector(state => state.auth);
  
  const [selectedKeys, setSelectedKeys] = useState<string[]>([]);
  const [openKeys, setOpenKeys] = useState<string[]>([]);

  // 根据用户权限过滤菜单
  const filteredMenuItems = useMemo(() => {
    const userPermissions = user?.permissions || [];
    return filterMenuByPermissions(navigationConfig, userPermissions);
  }, [user?.permissions]);

  // 将导航配置转换为Ant Design Menu格式
  const convertToMenuItems = (items: NavMenuItem[]): MenuItem[] => {
    return items.map(item => {
      const menuItem: MenuItem = {
        key: item.key,
        icon: item.icon ? React.createElement(item.icon) : undefined,
        label: item.badge ? (
          <Badge count={item.badge} size="small" offset={[10, 0]}>
            {item.label}
          </Badge>
        ) : item.label,
        disabled: item.disabled,
        children: item.children ? convertToMenuItems(item.children) : undefined,
      };
      return menuItem;
    });
  };

  const menuItems = useMemo(() => convertToMenuItems(filteredMenuItems), [filteredMenuItems]);

  // 根据当前路径设置选中和展开状态
  useEffect(() => {
    const findSelectedAndOpenKeys = (
      items: NavMenuItem[],
      currentPath: string,
      parentKeys: string[] = []
    ): { selectedKeys: string[]; openKeys: string[] } => {
      for (const item of items) {
        if (item.path === currentPath) {
          return {
            selectedKeys: [item.key],
            openKeys: parentKeys,
          };
        }
        
        if (item.children) {
          const result = findSelectedAndOpenKeys(
            item.children,
            currentPath,
            [...parentKeys, item.key]
          );
          if (result.selectedKeys.length > 0) {
            return result;
          }
        }
        
        // 模糊匹配：如果当前路径以某个菜单项的路径开头
        if (item.path && currentPath.startsWith(item.path) && item.path !== '/') {
          return {
            selectedKeys: [item.key],
            openKeys: parentKeys,
          };
        }
      }
      
      return { selectedKeys: [], openKeys: parentKeys };
    };

    const { selectedKeys: newSelectedKeys, openKeys: newOpenKeys } = findSelectedAndOpenKeys(
      filteredMenuItems,
      location.pathname
    );

    setSelectedKeys(newSelectedKeys);
    
    // 只有在非折叠状态下才设置展开状态
    if (!collapsed) {
      setOpenKeys(newOpenKeys);
    }
  }, [location.pathname, filteredMenuItems, collapsed]);

  // 处理菜单点击
  const handleMenuClick: MenuProps['onClick'] = ({ key }) => {
    // 查找对应的菜单项
    const findMenuItem = (items: NavMenuItem[], targetKey: string): NavMenuItem | null => {
      for (const item of items) {
        if (item.key === targetKey) {
          return item;
        }
        if (item.children) {
          const found = findMenuItem(item.children, targetKey);
          if (found) return found;
        }
      }
      return null;
    };

    const menuItem = findMenuItem(filteredMenuItems, key);
    if (menuItem?.path) {
      navigate(menuItem.path);
    }
  };

  // 处理子菜单展开/收起
  const handleOpenChange = (keys: string[]) => {
    setOpenKeys(keys);
  };

  return (
    <Menu
      mode="inline"
      theme={theme}
      selectedKeys={selectedKeys}
      openKeys={collapsed ? [] : openKeys}
      items={menuItems}
      onClick={handleMenuClick}
      onOpenChange={handleOpenChange}
      inlineCollapsed={collapsed}
      className={className}
      style={{
        height: '100%',
        borderRight: 0,
      }}
    />
  );
};

export default MainNavigation;