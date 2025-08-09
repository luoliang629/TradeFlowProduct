import { createSlice } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';
import type { Theme, Language } from '../types';

interface UIState {
  theme: Theme;
  language: Language;
  sidebarCollapsed: boolean;
  filePreviewPanelOpen: boolean;
  selectedFileId: string | null;
  globalLoading: boolean;
  notifications: Notification[];
}

interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  duration?: number;
}

const initialState: UIState = {
  theme: 'light',
  language: 'zh',
  sidebarCollapsed: false,
  filePreviewPanelOpen: true,
  selectedFileId: null,
  globalLoading: false,
  notifications: [],
};

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    setTheme: (state, action: PayloadAction<Theme>) => {
      state.theme = action.payload;
      // 更新HTML的data-theme属性
      document.documentElement.setAttribute('data-theme', action.payload);
    },
    toggleTheme: state => {
      state.theme = state.theme === 'light' ? 'dark' : 'light';
      document.documentElement.setAttribute('data-theme', state.theme);
    },
    setLanguage: (state, action: PayloadAction<Language>) => {
      state.language = action.payload;
    },
    toggleLanguage: state => {
      state.language = state.language === 'zh' ? 'en' : 'zh';
    },
    setSidebarCollapsed: (state, action: PayloadAction<boolean>) => {
      state.sidebarCollapsed = action.payload;
    },
    toggleSidebar: state => {
      state.sidebarCollapsed = !state.sidebarCollapsed;
    },
    setFilePreviewPanelOpen: (state, action: PayloadAction<boolean>) => {
      state.filePreviewPanelOpen = action.payload;
    },
    toggleFilePreviewPanel: state => {
      state.filePreviewPanelOpen = !state.filePreviewPanelOpen;
    },
    setSelectedFile: (state, action: PayloadAction<string | null>) => {
      state.selectedFileId = action.payload;
      // 如果选择了文件，确保预览面板打开
      if (action.payload) {
        state.filePreviewPanelOpen = true;
      }
    },
    setGlobalLoading: (state, action: PayloadAction<boolean>) => {
      state.globalLoading = action.payload;
    },
    addNotification: (state, action: PayloadAction<Omit<Notification, 'id'>>) => {
      const notification: Notification = {
        id: `notification_${Date.now()}`,
        duration: 4000, // 默认4秒
        ...action.payload,
      };
      state.notifications.push(notification);
    },
    removeNotification: (state, action: PayloadAction<string>) => {
      state.notifications = state.notifications.filter(
        n => n.id !== action.payload
      );
    },
    clearNotifications: state => {
      state.notifications = [];
    },
  },
});

export const {
  setTheme,
  toggleTheme,
  setLanguage,
  toggleLanguage,
  setSidebarCollapsed,
  toggleSidebar,
  setFilePreviewPanelOpen,
  toggleFilePreviewPanel,
  setSelectedFile,
  setGlobalLoading,
  addNotification,
  removeNotification,
  clearNotifications,
} = uiSlice.actions;

export default uiSlice.reducer;