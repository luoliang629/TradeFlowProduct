import { ConfigProvider } from 'antd';
import { useEffect } from 'react';
import { useAppSelector } from '../../store/hooks';
import { lightTheme, darkTheme } from '../../styles/theme';
import zhCN from 'antd/locale/zh_CN';
import enUS from 'antd/locale/en_US';

interface ThemeProviderProps {
  children: React.ReactNode;
}

const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const { theme, language } = useAppSelector(state => state.ui);

  // 应用主题到HTML元素
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  // 根据当前主题选择配置
  const currentTheme = theme === 'dark' ? darkTheme : lightTheme;
  
  // 根据语言选择Ant Design国际化配置
  const locale = language === 'zh' ? zhCN : enUS;

  return (
    <ConfigProvider theme={currentTheme} locale={locale}>
      {children}
    </ConfigProvider>
  );
};

export default ThemeProvider;