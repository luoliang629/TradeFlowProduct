import type { ThemeConfig } from 'antd';

export const lightTheme: ThemeConfig = {
  token: {
    // 主色调配置 - 参考UI原型的蓝色主题
    colorPrimary: '#1e3a8a',
    colorPrimaryHover: '#1e40af',
    colorPrimaryActive: '#1d4ed8',
    
    // 辅助色调
    colorSuccess: '#059669',
    colorWarning: '#d97706',
    colorError: '#dc2626',
    colorInfo: '#0284c7',
    
    // 文字颜色
    colorText: '#111827',
    colorTextSecondary: '#6b7280',
    colorTextTertiary: '#9ca3af',
    
    // 背景色
    colorBgContainer: '#ffffff',
    colorBgElevated: '#ffffff',
    colorBgLayout: '#f8fafc',
    colorBgSpotlight: '#f1f5f9',
    
    // 边框色
    colorBorder: '#e2e8f0',
    colorBorderSecondary: '#f1f5f9',
    
    // 字体配置
    fontFamily: "'Inter', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif",
    fontSize: 14,
    fontSizeLG: 16,
    fontSizeSM: 12,
    
    // 圆角配置
    borderRadius: 8,
    borderRadiusLG: 12,
    borderRadiusSM: 6,
    
    // 阴影
    boxShadow: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
    boxShadowSecondary: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
    
    // 布局间距
    padding: 16,
    paddingLG: 24,
    paddingSM: 12,
    margin: 16,
    marginLG: 24,
    marginSM: 12,
  },
  components: {
    // 按钮组件配置
    Button: {
      primaryShadow: '0 2px 4px rgba(30, 58, 138, 0.2)',
      defaultShadow: '0 1px 2px rgba(0, 0, 0, 0.05)',
    },
    // 输入框组件配置
    Input: {
      hoverBorderColor: '#1e3a8a',
      activeBorderColor: '#1e3a8a',
    },
    // 菜单组件配置
    Menu: {
      itemBg: 'transparent',
      itemSelectedBg: 'rgba(30, 58, 138, 0.1)',
      itemSelectedColor: '#1e3a8a',
      itemHoverBg: 'rgba(30, 58, 138, 0.05)',
    },
    // 卡片组件配置
    Card: {
      boxShadowTertiary: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
    },
    // 模态框配置
    Modal: {
      zIndexPopupBase: 1000,
    },
  },
};

export const darkTheme: ThemeConfig = {
  ...lightTheme,
  token: {
    ...lightTheme.token,
    // 暗色主题配色
    colorText: '#f9fafb',
    colorTextSecondary: '#d1d5db',
    colorTextTertiary: '#9ca3af',
    
    colorBgContainer: '#1f2937',
    colorBgElevated: '#1f2937',
    colorBgLayout: '#111827',
    colorBgSpotlight: '#374151',
    
    colorBorder: '#374151',
    colorBorderSecondary: '#4b5563',
  },
};