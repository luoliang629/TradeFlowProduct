# TradeFlow 前端开发规范文档

## 文档概述

本文档基于 TradeFlow MVP 三栏布局设计，为前端开发团队提供全面的开发规范和最佳实践指南。确保代码质量、可维护性和团队协作效率。

---

## 1. 技术栈规范

### 1.1 核心技术栈

```json
{
  "框架": "React 18+",
  "状态管理": "Redux Toolkit + RTK Query",
  "路由": "React Router v6",
  "UI组件库": "自研组件系统 + Headless UI",
  "样式": "CSS Modules + PostCSS",
  "构建工具": "Vite",
  "包管理": "pnpm",
  "类型检查": "TypeScript 5.0+",
  "测试": "Vitest + React Testing Library + Playwright",
  "代码格式化": "Prettier + ESLint",
  "Git Hooks": "Husky + lint-staged"
}
```

### 1.2 开发环境要求

- **Node.js**: >= 18.0.0
- **pnpm**: >= 8.0.0
- **TypeScript**: >= 5.0.0
- **React DevTools**: 浏览器扩展
- **VS Code**: 推荐编辑器 + 必要扩展

### 1.3 必要的 VS Code 扩展

```json
{
  "推荐扩展": [
    "bradlc.vscode-tailwindcss",
    "esbenp.prettier-vscode",
    "dbaeumer.vscode-eslint",
    "ms-vscode.vscode-typescript-next",
    "formulahendry.auto-rename-tag",
    "christian-kohler.path-intellisense",
    "ms-playwright.playwright"
  ]
}
```

---

## 2. 项目结构和文件组织

### 2.1 目录结构

```
src/frontend/
├── public/                          # 静态资源
│   ├── favicon.ico
│   ├── manifest.json
│   └── locales/                     # 国际化资源
│       ├── en.json
│       └── zh.json
├── src/
│   ├── components/                  # 可复用组件
│   │   ├── ui/                      # 基础UI组件
│   │   │   ├── Button/
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Button.module.css
│   │   │   │   ├── Button.test.tsx
│   │   │   │   └── index.ts
│   │   │   ├── Input/
│   │   │   ├── Modal/
│   │   │   └── index.ts
│   │   ├── layout/                  # 布局组件
│   │   │   ├── ThreeColumnLayout/
│   │   │   ├── Sidebar/
│   │   │   ├── Header/
│   │   │   └── AgentPanel/
│   │   ├── business/                # 业务组件
│   │   │   ├── ChatInterface/
│   │   │   ├── QuickActions/
│   │   │   ├── MessageBubble/
│   │   │   └── ActivityLog/
│   │   └── common/                  # 通用组件
│   │       ├── Loading/
│   │       ├── ErrorBoundary/
│   │       └── NotFound/
│   ├── pages/                       # 页面组件
│   │   ├── Chat/
│   │   ├── BuyerDevelopment/
│   │   ├── SupplierMatching/
│   │   ├── History/
│   │   └── Settings/
│   ├── hooks/                       # 自定义Hook
│   │   ├── useSSE.ts                # Server-Sent Events
│   │   ├── useChat.ts               # 聊天逻辑
│   │   ├── useI18n.ts               # 国际化
│   │   ├── useLocalStorage.ts       # 本地存储
│   │   └── useAgentStatus.ts        # Agent状态管理
│   ├── store/                       # 状态管理
│   │   ├── index.ts                 # Store配置
│   │   ├── slices/                  # Redux Slices
│   │   │   ├── chatSlice.ts
│   │   │   ├── userSlice.ts
│   │   │   ├── agentSlice.ts
│   │   │   └── uiSlice.ts
│   │   └── api/                     # RTK Query API
│   │       ├── chatApi.ts
│   │       ├── userApi.ts
│   │       └── tradeApi.ts
│   ├── services/                    # 服务层
│   │   ├── api.ts                   # API配置
│   │   ├── sse.ts                   # SSE服务
│   │   ├── auth.ts                  # 认证服务
│   │   └── storage.ts               # 存储服务
│   ├── utils/                       # 工具函数
│   │   ├── constants.ts             # 常量定义
│   │   ├── formatters.ts            # 格式化函数
│   │   ├── validators.ts            # 验证函数
│   │   ├── helpers.ts               # 辅助函数
│   │   └── types.ts                 # 类型定义
│   ├── styles/                      # 全局样式
│   │   ├── globals.css              # 全局样式
│   │   ├── variables.css            # CSS变量
│   │   ├── animations.css           # 动画样式
│   │   └── utilities.css            # 工具类
│   ├── assets/                      # 资源文件
│   │   ├── images/
│   │   ├── icons/
│   │   └── fonts/
│   ├── types/                       # TypeScript类型
│   │   ├── api.ts
│   │   ├── chat.ts
│   │   ├── user.ts
│   │   └── global.d.ts
│   ├── App.tsx                      # 根组件
│   ├── main.tsx                     # 入口文件
│   └── vite-env.d.ts               # Vite类型声明
├── tests/                           # 测试文件
│   ├── __mocks__/                   # Mock文件
│   ├── e2e/                         # E2E测试
│   ├── integration/                 # 集成测试
│   └── utils/                       # 测试工具
├── package.json
├── vite.config.ts
├── tsconfig.json
├── tailwind.config.js
├── postcss.config.js
├── playwright.config.ts
└── README.md
```

### 2.2 文件命名规范

- **组件文件**: PascalCase (例: `Button.tsx`, `ChatInterface.tsx`)
- **Hook文件**: camelCase, 以 `use` 开头 (例: `useChat.ts`, `useSSE.ts`)
- **工具文件**: camelCase (例: `formatters.ts`, `validators.ts`)
- **常量文件**: camelCase (例: `constants.ts`, `config.ts`)
- **样式文件**: 与组件同名 + `.module.css` (例: `Button.module.css`)
- **测试文件**: 与目标文件同名 + `.test.tsx` (例: `Button.test.tsx`)

---

## 3. 组件开发规范

### 3.1 组件架构模式

采用**原子设计**（Atomic Design）模式:

```
Atoms (原子) → Molecules (分子) → Organisms (有机体) → Templates (模板) → Pages (页面)
```

### 3.2 组件开发标准

#### 3.2.1 函数组件模板

```tsx
// src/components/ui/Button/Button.tsx
import React, { forwardRef } from 'react';
import cn from 'classnames';
import styles from './Button.module.css';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  /** 按钮变体 */
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  /** 按钮尺寸 */
  size?: 'sm' | 'md' | 'lg';
  /** 是否为加载状态 */
  loading?: boolean;
  /** 是否为全宽 */
  fullWidth?: boolean;
  /** 按钮图标 */
  icon?: React.ReactNode;
  /** 图标位置 */
  iconPosition?: 'left' | 'right';
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({
    children,
    variant = 'primary',
    size = 'md',
    loading = false,
    fullWidth = false,
    icon,
    iconPosition = 'left',
    className,
    disabled,
    ...props
  }, ref) => {
    const buttonClasses = cn(
      styles.button,
      styles[variant],
      styles[size],
      {
        [styles.loading]: loading,
        [styles.fullWidth]: fullWidth,
      },
      className
    );

    const isDisabled = disabled || loading;

    return (
      <button
        ref={ref}
        className={buttonClasses}
        disabled={isDisabled}
        aria-busy={loading}
        {...props}
      >
        {loading && <span className={styles.spinner} />}
        {!loading && icon && iconPosition === 'left' && (
          <span className={styles.iconLeft}>{icon}</span>
        )}
        {children && <span className={styles.content}>{children}</span>}
        {!loading && icon && iconPosition === 'right' && (
          <span className={styles.iconRight}>{icon}</span>
        )}
      </button>
    );
  }
);

Button.displayName = 'Button';
```

#### 3.2.2 业务组件模板

```tsx
// src/components/business/ChatInterface/ChatInterface.tsx
import React, { useState, useCallback, useRef, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useTranslation } from 'react-i18next';

import { MessageBubble } from '../MessageBubble';
import { ChatInput } from '../ChatInput';
import { useSSE } from '../../../hooks/useSSE';
import { sendMessage, selectMessages, selectIsLoading } from '../../../store/slices/chatSlice';
import type { RootState } from '../../../store';
import type { Message } from '../../../types/chat';

import styles from './ChatInterface.module.css';

export interface ChatInterfaceProps {
  /** 聊天窗口ID */
  chatId?: string;
  /** 是否显示欢迎消息 */
  showWelcome?: boolean;
  /** 自定义类名 */
  className?: string;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  chatId,
  showWelcome = true,
  className
}) => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Redux state
  const messages = useSelector((state: RootState) => selectMessages(state, chatId));
  const isLoading = useSelector((state: RootState) => selectIsLoading(state));
  
  // Local state
  const [inputValue, setInputValue] = useState('');
  
  // SSE connection for real-time updates
  const { connect, disconnect, isConnected } = useSSE({
    url: `/api/chat/${chatId}/stream`,
    onMessage: (data) => {
      // Handle real-time message updates
    }
  });

  // Auto scroll to bottom
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  // Handle message send
  const handleSendMessage = useCallback(async (content: string) => {
    if (!content.trim() || isLoading) return;
    
    try {
      await dispatch(sendMessage({ content, chatId }));
      setInputValue('');
      scrollToBottom();
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  }, [dispatch, chatId, isLoading]);

  // Effects
  useEffect(() => {
    if (chatId) {
      connect();
    }
    return () => disconnect();
  }, [chatId, connect, disconnect]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  return (
    <div className={cn(styles.chatInterface, className)}>
      {/* Welcome Section */}
      {showWelcome && messages.length === 0 && (
        <div className={styles.welcomeSection}>
          <h2 className={styles.welcomeTitle}>
            {t('chat.welcome.title')}
          </h2>
          <p className={styles.welcomeSubtitle}>
            {t('chat.welcome.subtitle')}
          </p>
        </div>
      )}

      {/* Messages */}
      <div className={styles.messagesContainer}>
        {messages.map((message) => (
          <MessageBubble
            key={message.id}
            message={message}
            className={styles.messageBubble}
          />
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <ChatInput
        value={inputValue}
        onChange={setInputValue}
        onSend={handleSendMessage}
        disabled={isLoading}
        placeholder={t('chat.input.placeholder')}
        className={styles.chatInput}
      />
    </div>
  );
};
```

### 3.3 组件Props和TypeScript规范

#### 3.3.1 Props接口定义

```tsx
// 基础组件Props
export interface BaseComponentProps {
  /** 自定义类名 */
  className?: string;
  /** 自定义样式 */
  style?: React.CSSProperties;
  /** 测试ID */
  'data-testid'?: string;
  /** 子元素 */
  children?: React.ReactNode;
}

// 业务组件Props继承基础Props
export interface ChatInterfaceProps extends BaseComponentProps {
  chatId?: string;
  showWelcome?: boolean;
  onMessageSend?: (message: string) => void;
}
```

#### 3.3.2 必需的JSDoc注释

```tsx
/**
 * 聊天界面组件
 * 
 * @description 提供完整的聊天交互功能，包括消息展示、输入、实时更新等
 * @example
 * ```tsx
 * <ChatInterface 
 *   chatId="chat-123"
 *   showWelcome={true}
 *   onMessageSend={handleMessage}
 * />
 * ```
 */
export const ChatInterface: React.FC<ChatInterfaceProps> = ({ ... }) => {
  // 组件实现
};
```

---

## 4. 样式系统规范

### 4.1 CSS Variables 设计系统

基于HTML设计文件提取的设计系统：

```css
/* src/styles/variables.css */
:root {
  /* 色彩系统 */
  --color-primary: #1e3a8a;
  --color-primary-dark: #1e40af;
  --color-primary-light: #3b82f6;
  
  --color-accent: #f97316;
  --color-accent-hover: #ea580c;
  --color-accent-light: #fb923c;
  
  --color-success: #059669;
  --color-warning: #d97706;
  --color-error: #dc2626;
  --color-info: #0284c7;
  
  /* 文本颜色 */
  --text-primary: #111827;
  --text-secondary: #6b7280;
  --text-light: #9ca3af;
  --text-inverse: #ffffff;
  
  /* 背景颜色 */
  --bg-primary: #ffffff;
  --bg-secondary: #f9fafb;
  --bg-tertiary: #f3f4f6;
  --bg-dark: #1f2937;
  
  /* 边框 */
  --border-color: #e5e7eb;
  --border-hover: #d1d5db;
  --border-focus: var(--color-primary);
  
  /* 阴影 */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
  --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
  
  /* 圆角 */
  --radius-sm: 0.375rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  --radius-xl: 1rem;
  --radius-2xl: 1.5rem;
  
  /* 间距系统 */
  --spacing-xs: 0.25rem;    /* 4px */
  --spacing-sm: 0.5rem;     /* 8px */
  --spacing-md: 1rem;       /* 16px */
  --spacing-lg: 1.5rem;     /* 24px */
  --spacing-xl: 2rem;       /* 32px */
  --spacing-2xl: 3rem;      /* 48px */
  --spacing-3xl: 4rem;      /* 64px */
  
  /* 字体系统 */
  --font-family: 'Inter', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  --font-mono: 'JetBrains Mono', 'SF Mono', Consolas, monospace;
  
  /* 字体大小 */
  --text-xs: 0.75rem;       /* 12px */
  --text-sm: 0.875rem;      /* 14px */
  --text-base: 1rem;        /* 16px */
  --text-lg: 1.125rem;      /* 18px */
  --text-xl: 1.25rem;       /* 20px */
  --text-2xl: 1.5rem;       /* 24px */
  --text-3xl: 1.875rem;     /* 30px */
  --text-4xl: 2.25rem;      /* 36px */
  
  /* 字重 */
  --font-light: 300;
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;
  
  /* 行高 */
  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.75;
  
  /* 布局尺寸 */
  --sidebar-width: 280px;
  --agent-panel-width: 320px;
  --header-height: 64px;
  
  /* 过渡动画 */
  --transition-fast: 150ms ease;
  --transition-normal: 250ms ease;
  --transition-slow: 350ms ease;
  
  /* Z-index层级 */
  --z-dropdown: 1000;
  --z-sticky: 1020;
  --z-fixed: 1030;
  --z-modal-backdrop: 1040;
  --z-modal: 1050;
  --z-popover: 1060;
  --z-tooltip: 1070;
  --z-toast: 1080;
}

/* 暗色主题变量 */
[data-theme="dark"] {
  --text-primary: #f9fafb;
  --text-secondary: #d1d5db;
  --text-light: #9ca3af;
  --text-inverse: #111827;
  
  --bg-primary: #1f2937;
  --bg-secondary: #111827;
  --bg-tertiary: #374151;
  --bg-dark: #000000;
  
  --border-color: #374151;
  --border-hover: #4b5563;
}
```

### 4.2 CSS Modules 命名规范

```css
/* Button.module.css */
.button {
  /* 基础样式 */
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-family);
  font-weight: var(--font-medium);
  transition: var(--transition-fast);
  cursor: pointer;
  user-select: none;
  
  /* 默认状态 */
  &:focus-visible {
    outline: 2px solid var(--border-focus);
    outline-offset: 2px;
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

/* 变体样式 */
.primary {
  background-color: var(--color-primary);
  color: var(--text-inverse);
  border: 1px solid var(--color-primary);
  
  &:hover:not(:disabled) {
    background-color: var(--color-primary-dark);
  }
}

.secondary {
  background-color: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  
  &:hover:not(:disabled) {
    background-color: var(--bg-tertiary);
  }
}

/* 尺寸样式 */
.sm {
  padding: var(--spacing-sm) var(--spacing-md);
  font-size: var(--text-sm);
  border-radius: var(--radius-sm);
  min-height: 32px;
}

.md {
  padding: var(--spacing-md) var(--spacing-lg);
  font-size: var(--text-base);
  border-radius: var(--radius-md);
  min-height: 40px;
}

.lg {
  padding: var(--spacing-lg) var(--spacing-xl);
  font-size: var(--text-lg);
  border-radius: var(--radius-lg);
  min-height: 48px;
}

/* 状态样式 */
.loading {
  position: relative;
  color: transparent;
}

.fullWidth {
  width: 100%;
}

/* 图标样式 */
.iconLeft {
  margin-right: var(--spacing-sm);
}

.iconRight {
  margin-left: var(--spacing-sm);
}

/* 加载动画 */
.spinner {
  position: absolute;
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
```

### 4.3 工具类系统

```css
/* src/styles/utilities.css */

/* 显示工具类 */
.hidden { display: none !important; }
.block { display: block !important; }
.inline { display: inline !important; }
.inline-block { display: inline-block !important; }
.flex { display: flex !important; }
.inline-flex { display: inline-flex !important; }
.grid { display: grid !important; }

/* Flexbox工具类 */
.flex-row { flex-direction: row !important; }
.flex-col { flex-direction: column !important; }
.flex-wrap { flex-wrap: wrap !important; }
.flex-nowrap { flex-wrap: nowrap !important; }

.items-start { align-items: flex-start !important; }
.items-center { align-items: center !important; }
.items-end { align-items: flex-end !important; }
.items-stretch { align-items: stretch !important; }

.justify-start { justify-content: flex-start !important; }
.justify-center { justify-content: center !important; }
.justify-end { justify-content: flex-end !important; }
.justify-between { justify-content: space-between !important; }
.justify-around { justify-content: space-around !important; }

/* 间距工具类 */
.m-0 { margin: 0 !important; }
.m-auto { margin: auto !important; }
.mt-sm { margin-top: var(--spacing-sm) !important; }
.mr-md { margin-right: var(--spacing-md) !important; }
.mb-lg { margin-bottom: var(--spacing-lg) !important; }
.ml-xl { margin-left: var(--spacing-xl) !important; }

.p-0 { padding: 0 !important; }
.pt-sm { padding-top: var(--spacing-sm) !important; }
.pr-md { padding-right: var(--spacing-md) !important; }
.pb-lg { padding-bottom: var(--spacing-lg) !important; }
.pl-xl { padding-left: var(--spacing-xl) !important; }

/* 文本工具类 */
.text-left { text-align: left !important; }
.text-center { text-align: center !important; }
.text-right { text-align: right !important; }

.text-xs { font-size: var(--text-xs) !important; }
.text-sm { font-size: var(--text-sm) !important; }
.text-base { font-size: var(--text-base) !important; }
.text-lg { font-size: var(--text-lg) !important; }

.font-light { font-weight: var(--font-light) !important; }
.font-normal { font-weight: var(--font-normal) !important; }
.font-medium { font-weight: var(--font-medium) !important; }
.font-semibold { font-weight: var(--font-semibold) !important; }
.font-bold { font-weight: var(--font-bold) !important; }

/* 颜色工具类 */
.text-primary { color: var(--text-primary) !important; }
.text-secondary { color: var(--text-secondary) !important; }
.text-light { color: var(--text-light) !important; }
.text-inverse { color: var(--text-inverse) !important; }

.bg-primary { background-color: var(--bg-primary) !important; }
.bg-secondary { background-color: var(--bg-secondary) !important; }
.bg-tertiary { background-color: var(--bg-tertiary) !important; }

/* 响应式工具类 */
@media (max-width: 640px) {
  .sm\:hidden { display: none !important; }
  .sm\:block { display: block !important; }
}

@media (max-width: 768px) {
  .md\:hidden { display: none !important; }
  .md\:block { display: block !important; }
}

@media (max-width: 1024px) {
  .lg\:hidden { display: none !important; }
  .lg\:block { display: block !important; }
}
```

---

## 5. 状态管理规范

### 5.1 Redux Toolkit 架构

```tsx
// src/store/index.ts
import { configureStore } from '@reduxjs/toolkit';
import { chatApi } from './api/chatApi';
import { userApi } from './api/userApi';
import chatReducer from './slices/chatSlice';
import userReducer from './slices/userSlice';
import agentReducer from './slices/agentSlice';
import uiReducer from './slices/uiSlice';

export const store = configureStore({
  reducer: {
    chat: chatReducer,
    user: userReducer,
    agent: agentReducer,
    ui: uiReducer,
    // RTK Query APIs
    [chatApi.reducerPath]: chatApi.reducer,
    [userApi.reducerPath]: userApi.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE'],
      },
    })
      .concat(chatApi.middleware)
      .concat(userApi.middleware),
  devTools: process.env.NODE_ENV !== 'production',
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

// 类型化的hooks
export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;
```

### 5.2 Slice 开发规范

```tsx
// src/store/slices/chatSlice.ts
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import type { RootState } from '../index';
import type { Message, ChatSession } from '../../types/chat';

// 异步action
export const sendMessage = createAsyncThunk(
  'chat/sendMessage',
  async ({ content, chatId }: { content: string; chatId?: string }) => {
    const response = await fetch('/api/chat/send', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content, chatId }),
    });
    
    if (!response.ok) {
      throw new Error('Failed to send message');
    }
    
    return response.json();
  }
);

// State接口
interface ChatState {
  sessions: Record<string, ChatSession>;
  currentSessionId: string | null;
  isLoading: boolean;
  error: string | null;
}

// 初始状态
const initialState: ChatState = {
  sessions: {},
  currentSessionId: null,
  isLoading: false,
  error: null,
};

// Slice定义
const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    // 同步actions
    setCurrentSession: (state, action: PayloadAction<string>) => {
      state.currentSessionId = action.payload;
    },
    
    addMessage: (state, action: PayloadAction<{ sessionId: string; message: Message }>) => {
      const { sessionId, message } = action.payload;
      if (!state.sessions[sessionId]) {
        state.sessions[sessionId] = {
          id: sessionId,
          messages: [],
          createdAt: new Date().toISOString(),
        };
      }
      state.sessions[sessionId].messages.push(message);
    },
    
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    // 异步action的处理
    builder
      .addCase(sendMessage.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(sendMessage.fulfilled, (state, action) => {
        state.isLoading = false;
        // 处理成功响应
      })
      .addCase(sendMessage.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Failed to send message';
      });
  },
});

// Actions导出
export const { setCurrentSession, addMessage, clearError } = chatSlice.actions;

// Selectors
export const selectCurrentSession = (state: RootState) => {
  const sessionId = state.chat.currentSessionId;
  return sessionId ? state.chat.sessions[sessionId] : null;
};

export const selectMessages = (state: RootState, sessionId?: string) => {
  const targetSessionId = sessionId || state.chat.currentSessionId;
  return targetSessionId ? state.chat.sessions[targetSessionId]?.messages || [] : [];
};

export const selectIsLoading = (state: RootState) => state.chat.isLoading;

export default chatSlice.reducer;
```

### 5.3 RTK Query API规范

```tsx
// src/store/api/chatApi.ts
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import type { Message, ChatSession } from '../../types/chat';

export const chatApi = createApi({
  reducerPath: 'chatApi',
  baseQuery: fetchBaseQuery({
    baseUrl: '/api/chat',
    prepareHeaders: (headers, { getState }) => {
      // 添加认证头等
      const token = (getState() as RootState).user.token;
      if (token) {
        headers.set('authorization', `Bearer ${token}`);
      }
      return headers;
    },
  }),
  tagTypes: ['Chat', 'Message'],
  endpoints: (builder) => ({
    // 查询聊天列表
    getChatSessions: builder.query<ChatSession[], void>({
      query: () => '/sessions',
      providesTags: ['Chat'],
    }),
    
    // 获取聊天历史
    getChatHistory: builder.query<Message[], string>({
      query: (sessionId) => `/sessions/${sessionId}/messages`,
      providesTags: (result, error, sessionId) => [
        { type: 'Message', id: sessionId },
      ],
    }),
    
    // 发送消息
    sendMessage: builder.mutation<Message, { sessionId: string; content: string }>({
      query: ({ sessionId, content }) => ({
        url: `/sessions/${sessionId}/messages`,
        method: 'POST',
        body: { content },
      }),
      invalidatesTags: (result, error, { sessionId }) => [
        { type: 'Message', id: sessionId },
      ],
    }),
    
    // 创建新会话
    createChatSession: builder.mutation<ChatSession, { title?: string }>({
      query: ({ title }) => ({
        url: '/sessions',
        method: 'POST',
        body: { title },
      }),
      invalidatesTags: ['Chat'],
    }),
  }),
});

// 导出hooks
export const {
  useGetChatSessionsQuery,
  useGetChatHistoryQuery,
  useSendMessageMutation,
  useCreateChatSessionMutation,
} = chatApi;
```

---

## 6. 国际化（i18n）实现规范

### 6.1 i18next配置

```tsx
// src/services/i18n.ts
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import Backend from 'i18next-http-backend';
import LanguageDetector from 'i18next-browser-languagedetector';

import enTranslations from '../locales/en.json';
import zhTranslations from '../locales/zh.json';

i18n
  .use(Backend)
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    fallbackLng: 'en',
    debug: process.env.NODE_ENV === 'development',
    
    resources: {
      en: { translation: enTranslations },
      zh: { translation: zhTranslations },
    },
    
    detection: {
      order: ['localStorage', 'navigator', 'htmlTag'],
      caches: ['localStorage'],
    },
    
    interpolation: {
      escapeValue: false,
    },
    
    backend: {
      loadPath: '/locales/{{lng}}.json',
    },
  });

export default i18n;
```

### 6.2 翻译资源结构

```json
// src/locales/en.json
{
  "common": {
    "loading": "Loading...",
    "error": "Error",
    "success": "Success",
    "cancel": "Cancel",
    "confirm": "Confirm",
    "save": "Save",
    "delete": "Delete",
    "edit": "Edit",
    "search": "Search",
    "send": "Send"
  },
  "navigation": {
    "chat": "AI Assistant",
    "buyerDevelopment": "Buyer Development",
    "supplierMatching": "Supplier Matching",
    "history": "Usage History",
    "settings": "Settings"
  },
  "chat": {
    "welcome": {
      "title": "How can I help you with international trade today?",
      "subtitle": "I'm your AI assistant for buyer development, supplier matching, and trade intelligence."
    },
    "input": {
      "placeholder": "Type your message here...",
      "attachFile": "Attach file"
    },
    "quickActions": {
      "findBuyers": {
        "title": "Find Buyers",
        "description": "Discover potential buyers for your products in global markets"
      },
      "findSuppliers": {
        "title": "Find Suppliers", 
        "description": "Connect with reliable suppliers for your procurement needs"
      }
    }
  },
  "agent": {
    "status": {
      "ready": "Ready to assist you",
      "thinking": "Processing your request...",
      "searching": "Searching global database...",
      "analyzing": "Analyzing results..."
    },
    "activity": {
      "title": "Recent Activity",
      "showAll": "Show All",
      "showLess": "Show Less"
    }
  },
  "errors": {
    "network": "Network connection error",
    "unauthorized": "Please log in to continue",
    "serverError": "Server error, please try again later",
    "validation": {
      "required": "This field is required",
      "email": "Please enter a valid email address",
      "minLength": "Must be at least {{min}} characters"
    }
  }
}
```

```json
// src/locales/zh.json
{
  "common": {
    "loading": "加载中...",
    "error": "错误",
    "success": "成功",
    "cancel": "取消",
    "confirm": "确认",
    "save": "保存",
    "delete": "删除",
    "edit": "编辑",
    "search": "搜索",
    "send": "发送"
  },
  "navigation": {
    "chat": "AI助手",
    "buyerDevelopment": "买家开发",
    "supplierMatching": "供应商匹配",
    "history": "使用历史",
    "settings": "设置"
  },
  "chat": {
    "welcome": {
      "title": "今天我如何帮助您处理国际贸易事务？",
      "subtitle": "我是您的AI助手，专门协助买家开发、供应商匹配和贸易情报分析。"
    },
    "input": {
      "placeholder": "在此输入您的消息...",
      "attachFile": "附加文件"
    },
    "quickActions": {
      "findBuyers": {
        "title": "寻找买家",
        "description": "在全球市场中发现您产品的潜在买家"
      },
      "findSuppliers": {
        "title": "寻找供应商",
        "description": "为您的采购需求连接可靠的供应商"
      }
    }
  },
  "agent": {
    "status": {
      "ready": "准备为您服务",
      "thinking": "正在处理您的请求...",
      "searching": "正在搜索全球数据库...",
      "analyzing": "正在分析结果..."
    },
    "activity": {
      "title": "最近活动",
      "showAll": "显示全部",
      "showLess": "收起"
    }
  },
  "errors": {
    "network": "网络连接错误",
    "unauthorized": "请登录后继续",
    "serverError": "服务器错误，请稍后重试",
    "validation": {
      "required": "此字段为必填项",
      "email": "请输入有效的邮箱地址",
      "minLength": "至少需要{{min}}个字符"
    }
  }
}
```

### 6.3 Hook使用规范

```tsx
// src/hooks/useI18n.ts
import { useTranslation } from 'react-i18next';
import { useCallback } from 'react';

export const useI18n = () => {
  const { t, i18n } = useTranslation();
  
  const changeLanguage = useCallback((language: string) => {
    i18n.changeLanguage(language);
  }, [i18n]);
  
  const formatMessage = useCallback((key: string, values?: Record<string, any>) => {
    return t(key, values);
  }, [t]);
  
  return {
    t: formatMessage,
    currentLanguage: i18n.language,
    changeLanguage,
    languages: ['en', 'zh'],
  };
};

// 使用示例
const MyComponent: React.FC = () => {
  const { t, changeLanguage, currentLanguage } = useI18n();
  
  return (
    <div>
      <h1>{t('chat.welcome.title')}</h1>
      <button onClick={() => changeLanguage(currentLanguage === 'en' ? 'zh' : 'en')}>
        {currentLanguage === 'en' ? '中文' : 'English'}
      </button>
    </div>
  );
};
```

---

## 7. 性能优化指南

### 7.1 React优化策略

#### 7.1.1 组件级优化

```tsx
// 使用React.memo防止不必要的重渲染
export const MessageBubble = React.memo<MessageBubbleProps>(({ message, onEdit, onDelete }) => {
  // 组件逻辑
}, (prevProps, nextProps) => {
  // 自定义比较函数
  return (
    prevProps.message.id === nextProps.message.id &&
    prevProps.message.content === nextProps.message.content &&
    prevProps.message.timestamp === nextProps.message.timestamp
  );
});

// 使用useMemo缓存计算结果
const ChatInterface: React.FC = () => {
  const messages = useSelector(selectMessages);
  
  const groupedMessages = useMemo(() => {
    return messages.reduce((groups, message) => {
      const date = new Date(message.timestamp).toDateString();
      if (!groups[date]) {
        groups[date] = [];
      }
      groups[date].push(message);
      return groups;
    }, {} as Record<string, Message[]>);
  }, [messages]);
  
  return (
    // JSX
  );
};

// 使用useCallback稳定函数引用
const ChatInput: React.FC<ChatInputProps> = ({ onSend }) => {
  const [value, setValue] = useState('');
  
  const handleSubmit = useCallback((e: React.FormEvent) => {
    e.preventDefault();
    if (value.trim()) {
      onSend(value);
      setValue('');
    }
  }, [value, onSend]);
  
  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  }, [handleSubmit]);
  
  return (
    // JSX
  );
};
```

#### 7.1.2 代码分割

```tsx
// 路由级代码分割
import { lazy, Suspense } from 'react';
import { ErrorBoundary } from '../components/common/ErrorBoundary';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';

// 懒加载页面组件
const ChatPage = lazy(() => import('../pages/Chat/ChatPage'));
const BuyerDevelopmentPage = lazy(() => import('../pages/BuyerDevelopment/BuyerDevelopmentPage'));
const SupplierMatchingPage = lazy(() => import('../pages/SupplierMatching/SupplierMatchingPage'));

// 路由配置
export const AppRouter: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route
          path="/chat"
          element={
            <ErrorBoundary>
              <Suspense fallback={<LoadingSpinner />}>
                <ChatPage />
              </Suspense>
            </ErrorBoundary>
          }
        />
        <Route
          path="/buyer-development"
          element={
            <ErrorBoundary>
              <Suspense fallback={<LoadingSpinner />}>
                <BuyerDevelopmentPage />
              </Suspense>
            </ErrorBoundary>
          }
        />
        {/* 其他路由 */}
      </Routes>
    </Router>
  );
};

// 组件级代码分割
const HeavyComponent = lazy(() => 
  import('./HeavyComponent').then(module => ({ default: module.HeavyComponent }))
);
```

### 7.2 资源优化

#### 7.2.1 图片优化

```tsx
// 图片懒加载Hook
export const useLazyImage = (src: string, placeholder?: string) => {
  const [imageSrc, setImageSrc] = useState(placeholder || '');
  const [isLoaded, setIsLoaded] = useState(false);
  const imgRef = useRef<HTMLImageElement>(null);

  useEffect(() => {
    let observer: IntersectionObserver;
    
    if (imgRef.current) {
      observer = new IntersectionObserver(
        ([entry]) => {
          if (entry.isIntersecting) {
            setImageSrc(src);
            observer.unobserve(entry.target);
          }
        },
        { threshold: 0.1 }
      );
      
      observer.observe(imgRef.current);
    }
    
    return () => {
      if (observer) {
        observer.disconnect();
      }
    };
  }, [src]);

  const handleLoad = useCallback(() => {
    setIsLoaded(true);
  }, []);

  return {
    imgRef,
    imageSrc,
    isLoaded,
    handleLoad,
  };
};

// 优化的图片组件
interface OptimizedImageProps {
  src: string;
  alt: string;
  placeholder?: string;
  className?: string;
}

export const OptimizedImage: React.FC<OptimizedImageProps> = ({
  src,
  alt,
  placeholder,
  className
}) => {
  const { imgRef, imageSrc, isLoaded, handleLoad } = useLazyImage(src, placeholder);

  return (
    <div className={cn('relative overflow-hidden', className)}>
      <img
        ref={imgRef}
        src={imageSrc}
        alt={alt}
        onLoad={handleLoad}
        className={cn(
          'transition-opacity duration-300',
          { 'opacity-0': !isLoaded, 'opacity-100': isLoaded }
        )}
      />
      {!isLoaded && (
        <div className="absolute inset-0 bg-gray-200 animate-pulse flex items-center justify-center">
          <span className="text-gray-400">Loading...</span>
        </div>
      )}
    </div>
  );
};
```

#### 7.2.2 虚拟滚动

```tsx
// 虚拟滚动Hook
export const useVirtualScroll = <T>(
  items: T[],
  itemHeight: number,
  containerHeight: number,
  overscan = 5
) => {
  const [scrollTop, setScrollTop] = useState(0);
  const scrollElementRef = useRef<HTMLDivElement>(null);

  const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
  const endIndex = Math.min(
    items.length - 1,
    Math.floor((scrollTop + containerHeight) / itemHeight) + overscan
  );

  const visibleItems = items.slice(startIndex, endIndex + 1).map((item, index) => ({
    item,
    index: startIndex + index,
  }));

  const totalHeight = items.length * itemHeight;
  const offsetY = startIndex * itemHeight;

  const handleScroll = useCallback((e: React.UIEvent<HTMLDivElement>) => {
    setScrollTop(e.currentTarget.scrollTop);
  }, []);

  return {
    scrollElementRef,
    visibleItems,
    totalHeight,
    offsetY,
    handleScroll,
  };
};

// 虚拟化消息列表
export const VirtualizedMessageList: React.FC<{ messages: Message[] }> = ({
  messages
}) => {
  const containerHeight = 400;
  const itemHeight = 80;
  
  const {
    scrollElementRef,
    visibleItems,
    totalHeight,
    offsetY,
    handleScroll,
  } = useVirtualScroll(messages, itemHeight, containerHeight);

  return (
    <div
      ref={scrollElementRef}
      className="h-96 overflow-auto"
      onScroll={handleScroll}
    >
      <div style={{ height: totalHeight, position: 'relative' }}>
        <div style={{ transform: `translateY(${offsetY}px)` }}>
          {visibleItems.map(({ item: message, index }) => (
            <MessageBubble
              key={message.id}
              message={message}
              style={{ height: itemHeight }}
            />
          ))}
        </div>
      </div>
    </div>
  );
};
```

### 7.3 网络优化

```tsx
// API缓存配置
const apiCacheConfig = {
  // 启用缓存
  keepUnusedDataFor: 60, // 60秒
  // 重新获取策略
  refetchOnMountOrArgChange: true,
  refetchOnFocus: false,
  refetchOnReconnect: true,
};

// RTK Query with caching
export const chatApi = createApi({
  // ...其他配置
  endpoints: (builder) => ({
    getChatHistory: builder.query<Message[], string>({
      query: (sessionId) => `/sessions/${sessionId}/messages`,
      ...apiCacheConfig,
      // 乐观更新
      async onQueryStarted(sessionId, { dispatch, queryFulfilled }) {
        try {
          await queryFulfilled;
        } catch {
          // 处理错误
        }
      },
    }),
  }),
});

// 请求去重Hook
export const useDebounceQuery = <T>(
  queryFn: (params: T) => Promise<any>,
  params: T,
  delay = 300
) => {
  const [debouncedParams, setDebouncedParams] = useState(params);
  
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedParams(params);
    }, delay);
    
    return () => clearTimeout(timer);
  }, [params, delay]);
  
  return useQuery({
    queryKey: ['debounced', debouncedParams],
    queryFn: () => queryFn(debouncedParams),
    enabled: !!debouncedParams,
  });
};
```

---

## 8. 响应式设计规范

### 8.1 断点系统

```css
/* src/styles/breakpoints.css */
:root {
  --breakpoint-sm: 640px;   /* 移动设备 */
  --breakpoint-md: 768px;   /* 平板设备 */
  --breakpoint-lg: 1024px;  /* 桌面设备 */
  --breakpoint-xl: 1280px;  /* 大屏设备 */
  --breakpoint-2xl: 1536px; /* 超大屏设备 */
}

/* 媒体查询混合宏 */
@custom-media --sm (max-width: 640px);
@custom-media --md (max-width: 768px);
@custom-media --lg (max-width: 1024px);
@custom-media --xl (max-width: 1280px);
@custom-media --2xl (max-width: 1536px);

/* 反向查询 */
@custom-media --sm-up (min-width: 641px);
@custom-media --md-up (min-width: 769px);
@custom-media --lg-up (min-width: 1025px);
@custom-media --xl-up (min-width: 1281px);
@custom-media --2xl-up (min-width: 1537px);
```

### 8.2 响应式布局

```css
/* 三栏布局响应式 */
.three-column-layout {
  display: grid;
  grid-template-columns: var(--sidebar-width) 1fr var(--agent-panel-width);
  grid-template-rows: auto 1fr;
  grid-template-areas: 
    "sidebar header agent-panel"
    "sidebar main agent-panel";
  height: 100vh;
  
  @media --lg {
    /* 大屏隐藏agent面板 */
    grid-template-columns: var(--sidebar-width) 1fr;
    grid-template-areas: 
      "sidebar header"
      "sidebar main";
  }
  
  @media --md {
    /* 平板模式：侧边栏折叠 */
    grid-template-columns: 1fr;
    grid-template-areas: 
      "header"
      "main";
  }
}

.sidebar {
  grid-area: sidebar;
  
  @media --md {
    /* 移动端侧边栏变为浮层 */
    position: fixed;
    top: 0;
    left: 0;
    height: 100vh;
    z-index: var(--z-modal);
    transform: translateX(-100%);
    transition: transform var(--transition-normal);
    
    &.show {
      transform: translateX(0);
    }
  }
}

.main-content {
  grid-area: main;
  min-width: 0; /* 防止flex子元素溢出 */
}

.agent-panel {
  grid-area: agent-panel;
  
  @media --lg {
    display: none;
  }
}

/* 响应式字体 */
.responsive-text {
  font-size: clamp(1rem, 2.5vw, 1.5rem);
  line-height: 1.5;
}

/* 响应式间距 */
.responsive-padding {
  padding: clamp(1rem, 4vw, 2rem);
}

/* 响应式组件 */
.chat-container {
  padding: var(--spacing-xl);
  
  @media --md {
    padding: var(--spacing-lg);
  }
  
  @media --sm {
    padding: var(--spacing-md);
  }
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--spacing-lg);
  
  @media --sm {
    grid-template-columns: 1fr;
    gap: var(--spacing-md);
  }
}
```

### 8.3 响应式Hook

```tsx
// 响应式断点Hook
export const useBreakpoint = () => {
  const [breakpoint, setBreakpoint] = useState<string>('xl');
  
  useEffect(() => {
    const breakpoints = {
      sm: '(max-width: 640px)',
      md: '(max-width: 768px)',
      lg: '(max-width: 1024px)',
      xl: '(max-width: 1280px)',
      '2xl': '(min-width: 1281px)',
    };
    
    const mediaQueries = Object.entries(breakpoints).map(([key, query]) => ({
      key,
      mq: window.matchMedia(query),
    }));
    
    const handleChange = () => {
      const activeBreakpoint = mediaQueries.find(({ mq }) => mq.matches);
      setBreakpoint(activeBreakpoint?.key || '2xl');
    };
    
    // 初始检查
    handleChange();
    
    // 添加监听器
    mediaQueries.forEach(({ mq }) => {
      mq.addEventListener('change', handleChange);
    });
    
    return () => {
      mediaQueries.forEach(({ mq }) => {
        mq.removeEventListener('change', handleChange);
      });
    };
  }, []);
  
  return {
    breakpoint,
    isMobile: ['sm', 'md'].includes(breakpoint),
    isTablet: breakpoint === 'lg',
    isDesktop: ['xl', '2xl'].includes(breakpoint),
  };
};

// 使用示例
const ThreeColumnLayout: React.FC = ({ children }) => {
  const { isMobile, isTablet } = useBreakpoint();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  
  return (
    <div className={styles.layout}>
      <Sidebar 
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        className={cn({ [styles.mobile]: isMobile })}
      />
      
      <main className={styles.main}>
        {isMobile && (
          <MobileHeader onMenuClick={() => setSidebarOpen(true)} />
        )}
        {children}
      </main>
      
      {!isMobile && !isTablet && (
        <AgentPanel className={styles.agentPanel} />
      )}
    </div>
  );
};
```

### 8.4 触摸友好交互

```tsx
// 触摸手势Hook
export const useSwipeGesture = (
  onSwipeLeft?: () => void,
  onSwipeRight?: () => void,
  threshold = 50
) => {
  const touchStart = useRef<{ x: number; y: number } | null>(null);
  
  const handleTouchStart = useCallback((e: TouchEvent) => {
    const touch = e.touches[0];
    touchStart.current = { x: touch.clientX, y: touch.clientY };
  }, []);
  
  const handleTouchEnd = useCallback((e: TouchEvent) => {
    if (!touchStart.current) return;
    
    const touch = e.changedTouches[0];
    const deltaX = touch.clientX - touchStart.current.x;
    const deltaY = touch.clientY - touchStart.current.y;
    
    // 确保是水平滑动
    if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > threshold) {
      if (deltaX > 0) {
        onSwipeRight?.();
      } else {
        onSwipeLeft?.();
      }
    }
    
    touchStart.current = null;
  }, [onSwipeLeft, onSwipeRight, threshold]);
  
  return {
    onTouchStart: handleTouchStart,
    onTouchEnd: handleTouchEnd,
  };
};

// 移动端友好的侧边栏
const MobileSidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const swipeHandlers = useSwipeGesture(() => onClose());
  
  return (
    <>
      {/* 遮罩层 */}
      {isOpen && (
        <div 
          className={styles.overlay}
          onClick={onClose}
          {...swipeHandlers}
        />
      )}
      
      {/* 侧边栏 */}
      <aside 
        className={cn(styles.sidebar, { [styles.open]: isOpen })}
        {...swipeHandlers}
      >
        {/* 侧边栏内容 */}
      </aside>
    </>
  );
};
```

---

## 9. 代码质量标准

### 9.1 ESLint 配置

```json
// .eslintrc.json
{
  "extends": [
    "eslint:recommended",
    "@typescript-eslint/recommended",
    "react-hooks/recommended",
    "plugin:react/recommended",
    "plugin:react/jsx-runtime",
    "plugin:jsx-a11y/recommended",
    "plugin:import/recommended",
    "plugin:import/typescript",
    "prettier"
  ],
  "parser": "@typescript-eslint/parser",
  "parserOptions": {
    "ecmaVersion": "latest",
    "sourceType": "module",
    "ecmaFeatures": {
      "jsx": true
    }
  },
  "plugins": [
    "@typescript-eslint",
    "react",
    "react-hooks",
    "jsx-a11y",
    "import"
  ],
  "rules": {
    // React规则
    "react/prop-types": "off",
    "react/react-in-jsx-scope": "off",
    "react/jsx-uses-react": "off",
    "react-hooks/rules-of-hooks": "error",
    "react-hooks/exhaustive-deps": "warn",
    
    // TypeScript规则
    "@typescript-eslint/no-unused-vars": ["error", { "argsIgnorePattern": "^_" }],
    "@typescript-eslint/explicit-function-return-type": "off",
    "@typescript-eslint/explicit-module-boundary-types": "off",
    "@typescript-eslint/no-explicit-any": "warn",
    "@typescript-eslint/prefer-const": "error",
    
    // 导入规则
    "import/order": [
      "error",
      {
        "groups": [
          "builtin",
          "external",
          "internal",
          "parent",
          "sibling",
          "index"
        ],
        "newlines-between": "always",
        "alphabetize": {
          "order": "asc",
          "caseInsensitive": true
        }
      }
    ],
    "import/no-unresolved": "error",
    "import/no-cycle": "error",
    
    // 无障碍规则
    "jsx-a11y/alt-text": "error",
    "jsx-a11y/aria-props": "error",
    "jsx-a11y/aria-proptypes": "error",
    "jsx-a11y/aria-unsupported-elements": "error",
    "jsx-a11y/role-has-required-aria-props": "error",
    "jsx-a11y/role-supports-aria-props": "error",
    
    // 通用规则
    "no-console": ["warn", { "allow": ["warn", "error"] }],
    "no-debugger": "error",
    "prefer-const": "error",
    "no-var": "error"
  },
  "settings": {
    "react": {
      "version": "detect"
    },
    "import/resolver": {
      "typescript": {
        "alwaysTryTypes": true
      }
    }
  }
}
```

### 9.2 Prettier 配置

```json
// .prettierrc
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2,
  "useTabs": false,
  "quoteProps": "as-needed",
  "bracketSpacing": true,
  "bracketSameLine": false,
  "arrowParens": "always",
  "endOfLine": "lf",
  "jsxSingleQuote": true,
  "overrides": [
    {
      "files": "*.json",
      "options": {
        "singleQuote": false
      }
    }
  ]
}
```

### 9.3 TypeScript 配置

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    
    /* 模块解析 */
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    
    /* 类型检查 */
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    
    /* 路径映射 */
    "baseUrl": "./src",
    "paths": {
      "@/*": ["*"],
      "@/components/*": ["components/*"],
      "@/hooks/*": ["hooks/*"],
      "@/store/*": ["store/*"],
      "@/utils/*": ["utils/*"],
      "@/types/*": ["types/*"],
      "@/services/*": ["services/*"],
      "@/assets/*": ["assets/*"]
    }
  },
  "include": [
    "src/**/*",
    "tests/**/*"
  ],
  "exclude": [
    "node_modules",
    "dist",
    "build"
  ],
  "references": [
    { "path": "./tsconfig.node.json" }
  ]
}
```

### 9.4 Husky + lint-staged 配置

```json
// package.json
{
  "scripts": {
    "prepare": "husky install"
  },
  "lint-staged": {
    "*.{ts,tsx}": [
      "eslint --fix",
      "prettier --write",
      "git add"
    ],
    "*.{css,scss,less}": [
      "prettier --write",
      "git add"
    ],
    "*.{json,md}": [
      "prettier --write",
      "git add"
    ]
  }
}
```

```bash
# .husky/pre-commit
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

npx lint-staged
```

```bash
# .husky/commit-msg
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

npx commitlint --edit $1
```

### 9.5 Commitlint 配置

```js
// commitlint.config.cjs
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [
      2,
      'always',
      [
        'feat',     // 新功能
        'fix',      // Bug修复
        'docs',     // 文档更新
        'style',    // 代码格式
        'refactor', // 重构
        'perf',     // 性能优化
        'test',     // 测试
        'chore',    // 构建过程或辅助工具的变动
        'revert',   // 回滚
        'build',    // 构建系统
        'ci',       // CI配置
      ],
    ],
    'type-case': [2, 'always', 'lower-case'],
    'type-empty': [2, 'never'],
    'scope-empty': [0],
    'scope-case': [2, 'always', 'lower-case'],
    'subject-empty': [2, 'never'],
    'subject-full-stop': [2, 'never', '.'],
    'subject-case': [2, 'always', 'lower-case'],
    'header-max-length': [2, 'always', 100],
  },
};
```

---

## 10. 测试规范

### 10.1 单元测试（Vitest + React Testing Library）

#### 10.1.1 测试配置

```ts
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/tests/setup.ts',
    css: true,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/tests/',
        '**/*.d.ts',
        '**/*.config.*',
      ],
    },
  },
});
```

```ts
// src/tests/setup.ts
import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';
import { afterEach, vi } from 'vitest';

// 清理DOM
afterEach(() => {
  cleanup();
});

// Mock ResizeObserver
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));

// Mock IntersectionObserver
global.IntersectionObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});
```

#### 10.1.2 组件测试示例

```tsx
// src/components/ui/Button/Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';

import { Button } from './Button';

describe('Button Component', () => {
  it('renders with correct text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument();
  });

  it('handles click events', async () => {
    const user = userEvent.setup();
    const handleClick = vi.fn();
    
    render(<Button onClick={handleClick}>Click me</Button>);
    
    await user.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('applies correct variant classes', () => {
    const { rerender } = render(<Button variant="primary">Primary</Button>);
    expect(screen.getByRole('button')).toHaveClass('primary');

    rerender(<Button variant="secondary">Secondary</Button>);
    expect(screen.getByRole('button')).toHaveClass('secondary');
  });

  it('disables button when loading', () => {
    render(<Button loading>Loading</Button>);
    const button = screen.getByRole('button');
    
    expect(button).toBeDisabled();
    expect(button).toHaveAttribute('aria-busy', 'true');
  });

  it('shows loading spinner when loading', () => {
    render(<Button loading>Loading</Button>);
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
  });

  it('supports keyboard navigation', async () => {
    const user = userEvent.setup();
    const handleClick = vi.fn();
    
    render(<Button onClick={handleClick}>Button</Button>);
    
    const button = screen.getByRole('button');
    button.focus();
    
    await user.keyboard('{Enter}');
    expect(handleClick).toHaveBeenCalledTimes(1);
    
    await user.keyboard(' ');
    expect(handleClick).toHaveBeenCalledTimes(2);
  });
});
```

#### 10.1.3 Hook测试示例

```tsx
// src/hooks/useChat.test.ts
import { renderHook, act } from '@testing-library/react';
import { vi } from 'vitest';

import { useChat } from './useChat';

// Mock Redux store
const mockDispatch = vi.fn();
vi.mock('react-redux', () => ({
  useDispatch: () => mockDispatch,
  useSelector: vi.fn(),
}));

describe('useChat Hook', () => {
  beforeEach(() => {
    mockDispatch.mockClear();
  });

  it('initializes with empty message list', () => {
    const { result } = renderHook(() => useChat('session-1'));
    
    expect(result.current.messages).toEqual([]);
    expect(result.current.isLoading).toBe(false);
  });

  it('sends message correctly', async () => {
    const { result } = renderHook(() => useChat('session-1'));
    
    await act(async () => {
      await result.current.sendMessage('Hello, world!');
    });
    
    expect(mockDispatch).toHaveBeenCalled();
  });

  it('handles errors gracefully', async () => {
    mockDispatch.mockRejectedValue(new Error('Network error'));
    
    const { result } = renderHook(() => useChat('session-1'));
    
    await act(async () => {
      await result.current.sendMessage('Hello');
    });
    
    expect(result.current.error).toBeTruthy();
  });
});
```

### 10.2 集成测试

```tsx
// src/tests/integration/ChatFlow.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';

import { store } from '../../store';
import { ChatInterface } from '../../components/business/ChatInterface';

const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <Provider store={store}>
      <BrowserRouter>
        {component}
      </BrowserRouter>
    </Provider>
  );
};

describe('Chat Flow Integration', () => {
  it('completes full chat flow', async () => {
    const user = userEvent.setup();
    
    renderWithProviders(<ChatInterface />);
    
    // 1. 用户输入消息
    const input = screen.getByPlaceholderText(/type your message/i);
    await user.type(input, 'Hello, I need help finding suppliers');
    
    // 2. 点击发送按钮
    const sendButton = screen.getByRole('button', { name: /send/i });
    await user.click(sendButton);
    
    // 3. 验证消息显示
    expect(screen.getByText('Hello, I need help finding suppliers')).toBeInTheDocument();
    
    // 4. 等待AI响应
    await waitFor(() => {
      expect(screen.getByText(/i'll help you find suppliers/i)).toBeInTheDocument();
    });
    
    // 5. 验证输入框已清空
    expect(input).toHaveValue('');
  });
});
```

### 10.3 E2E测试（Playwright）

#### 10.3.1 Playwright配置

```ts
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],

  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

#### 10.3.2 E2E测试示例

```ts
// tests/e2e/chat.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Chat Interface', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should send and receive messages', async ({ page }) => {
    // 等待页面加载
    await expect(page.locator('[data-testid="chat-interface"]')).toBeVisible();

    // 输入消息
    const input = page.locator('[data-testid="chat-input"]');
    await input.fill('I need help finding suppliers for electronics');

    // 发送消息
    await page.click('[data-testid="send-button"]');

    // 验证用户消息显示
    await expect(page.locator('.message.user')).toContainText('I need help finding suppliers for electronics');

    // 等待AI响应
    await expect(page.locator('.message.assistant')).toBeVisible({ timeout: 10000 });

    // 验证Agent面板更新
    await expect(page.locator('[data-testid="agent-status"]')).toContainText('Processing');
  });

  test('should handle quick actions', async ({ page }) => {
    // 点击快速操作
    await page.click('[data-testid="quick-action-buyers"]');

    // 验证预填充的消息
    const input = page.locator('[data-testid="chat-input"]');
    await expect(input).toHaveValue(/find buyers/i);

    // 发送消息
    await page.click('[data-testid="send-button"]');

    // 验证结果显示
    await expect(page.locator('[data-testid="results-section"]')).toBeVisible({ timeout: 15000 });
  });

  test('should be responsive on mobile', async ({ page }) => {
    // 切换到移动端视图
    await page.setViewportSize({ width: 375, height: 667 });

    // 验证移动端布局
    await expect(page.locator('[data-testid="sidebar"]')).toBeHidden();
    await expect(page.locator('[data-testid="mobile-menu-button"]')).toBeVisible();

    // 打开侧边栏
    await page.click('[data-testid="mobile-menu-button"]');
    await expect(page.locator('[data-testid="sidebar"]')).toBeVisible();

    // 点击遮罩关闭
    await page.click('[data-testid="sidebar-overlay"]');
    await expect(page.locator('[data-testid="sidebar"]')).toBeHidden();
  });
});
```

### 10.4 测试工具函数

```tsx
// src/tests/utils/test-utils.tsx
import React from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { I18nextProvider } from 'react-i18next';

import { store } from '../../store';
import i18n from '../../services/i18n';

// 自定义渲染函数
const AllTheProviders: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <Provider store={store}>
      <BrowserRouter>
        <I18nextProvider i18n={i18n}>
          {children}
        </I18nextProvider>
      </BrowserRouter>
    </Provider>
  );
};

const customRender = (ui: React.ReactElement, options?: RenderOptions) =>
  render(ui, { wrapper: AllTheProviders, ...options });

// Mock数据生成器
export const createMockMessage = (overrides = {}) => ({
  id: Math.random().toString(36),
  content: 'Test message',
  sender: 'user',
  timestamp: new Date().toISOString(),
  ...overrides,
});

export const createMockChatSession = (overrides = {}) => ({
  id: Math.random().toString(36),
  title: 'Test Chat',
  messages: [],
  createdAt: new Date().toISOString(),
  ...overrides,
});

// 事件模拟工具
export const mockIntersectionObserver = () => {
  const mockIntersectionObserver = vi.fn();
  mockIntersectionObserver.mockReturnValue({
    observe: () => null,
    unobserve: () => null,
    disconnect: () => null,
  });
  window.IntersectionObserver = mockIntersectionObserver;
  window.IntersectionObserverEntry = vi.fn();
};

// 重新导出所有Testing Library工具
export * from '@testing-library/react';
export { customRender as render };
```

---

## 11. SSE（Server-Sent Events）集成规范

### 11.1 SSE Hook实现

```tsx
// src/hooks/useSSE.ts
import { useEffect, useRef, useCallback, useState } from 'react';

export interface SSEOptions {
  url: string;
  onMessage?: (data: any) => void;
  onError?: (error: Event) => void;
  onOpen?: () => void;
  onClose?: () => void;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

export const useSSE = ({
  url,
  onMessage,
  onError,
  onOpen,
  onClose,
  reconnectInterval = 3000,
  maxReconnectAttempts = 5,
}: SSEOptions) => {
  const [isConnected, setIsConnected] = useState(false);
  const [reconnectCount, setReconnectCount] = useState(0);
  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const connect = useCallback(() => {
    if (eventSourceRef.current?.readyState === EventSource.OPEN) {
      return; // 已连接
    }

    try {
      const eventSource = new EventSource(url, {
        withCredentials: true,
      });

      eventSource.onopen = () => {
        console.log('SSE connected to:', url);
        setIsConnected(true);
        setReconnectCount(0);
        onOpen?.();
      };

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          onMessage?.(data);
        } catch (error) {
          console.error('Error parsing SSE message:', error);
          onMessage?.(event.data); // 发送原始数据
        }
      };

      eventSource.onerror = (error) => {
        console.error('SSE error:', error);
        setIsConnected(false);
        onError?.(error);

        // 自动重连
        if (reconnectCount < maxReconnectAttempts) {
          console.log(`Attempting to reconnect SSE (${reconnectCount + 1}/${maxReconnectAttempts})`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            setReconnectCount(prev => prev + 1);
            connect();
          }, reconnectInterval);
        } else {
          console.error('Max reconnection attempts reached');
          onClose?.();
        }
      };

      eventSourceRef.current = eventSource;
    } catch (error) {
      console.error('Failed to create SSE connection:', error);
      onError?.(error as Event);
    }
  }, [url, onMessage, onError, onOpen, onClose, reconnectCount, maxReconnectAttempts, reconnectInterval]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
      setIsConnected(false);
      console.log('SSE disconnected from:', url);
      onClose?.();
    }
  }, [url, onClose]);

  // 发送自定义事件监听
  const addEventListener = useCallback((eventType: string, handler: (event: MessageEvent) => void) => {
    if (eventSourceRef.current) {
      eventSourceRef.current.addEventListener(eventType, handler);
    }
  }, []);

  const removeEventListener = useCallback((eventType: string, handler: (event: MessageEvent) => void) => {
    if (eventSourceRef.current) {
      eventSourceRef.current.removeEventListener(eventType, handler);
    }
  }, []);

  // 清理连接
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    connect,
    disconnect,
    isConnected,
    reconnectCount,
    addEventListener,
    removeEventListener,
  };
};
```

### 11.2 Agent状态实时更新

```tsx
// src/hooks/useAgentStatus.ts
import { useEffect, useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';

import { useSSE } from './useSSE';
import { 
  updateAgentStatus, 
  updateProgress, 
  addActivity, 
  setThinking 
} from '../store/slices/agentSlice';
import type { RootState } from '../store';

export const useAgentStatus = (sessionId?: string) => {
  const dispatch = useDispatch();
  const agentState = useSelector((state: RootState) => state.agent);

  // SSE消息处理器
  const handleAgentMessage = useCallback((data: any) => {
    switch (data.type) {
      case 'status_update':
        dispatch(updateAgentStatus({
          status: data.status,
          message: data.message,
        }));
        break;

      case 'progress_update':
        dispatch(updateProgress({
          percentage: data.percentage,
          message: data.message,
        }));
        break;

      case 'activity_log':
        dispatch(addActivity({
          id: data.id,
          message: data.message,
          status: data.status,
          timestamp: data.timestamp,
        }));
        break;

      case 'thinking_update':
        dispatch(setThinking({
          isThinking: data.isThinking,
          content: data.content,
        }));
        break;

      case 'results_preview':
        dispatch(updateResults({
          results: data.results,
          count: data.count,
        }));
        break;

      default:
        console.log('Unknown agent message type:', data.type);
    }
  }, [dispatch]);

  // SSE连接
  const { connect, disconnect, isConnected } = useSSE({
    url: sessionId ? `/api/agent/status/${sessionId}` : '/api/agent/status',
    onMessage: handleAgentMessage,
    onError: (error) => {
      console.error('Agent SSE error:', error);
      dispatch(updateAgentStatus({
        status: 'error',
        message: 'Connection lost',
      }));
    },
    onOpen: () => {
      dispatch(updateAgentStatus({
        status: 'ready',
        message: 'Ready to assist you',
      }));
    },
  });

  // 连接管理
  useEffect(() => {
    if (sessionId) {
      connect();
    }
    return () => disconnect();
  }, [sessionId, connect, disconnect]);

  return {
    agentState,
    isConnected,
    connect,
    disconnect,
  };
};
```

### 11.3 聊天消息流式更新

```tsx
// src/hooks/useStreamingChat.ts
import { useState, useCallback, useRef } from 'react';
import { useDispatch } from 'react-redux';

import { useSSE } from './useSSE';
import { addMessage, updateMessage } from '../store/slices/chatSlice';

export const useStreamingChat = (sessionId: string) => {
  const dispatch = useDispatch();
  const [streamingMessageId, setStreamingMessageId] = useState<string | null>(null);
  const currentMessageRef = useRef<string>('');

  const handleStreamMessage = useCallback((data: any) => {
    switch (data.type) {
      case 'message_start':
        // 开始新的流式消息
        const messageId = data.messageId;
        setStreamingMessageId(messageId);
        currentMessageRef.current = '';
        
        dispatch(addMessage({
          sessionId,
          message: {
            id: messageId,
            content: '',
            sender: 'assistant',
            timestamp: new Date().toISOString(),
            isStreaming: true,
          },
        }));
        break;

      case 'message_chunk':
        // 累加消息内容
        if (streamingMessageId === data.messageId) {
          currentMessageRef.current += data.content;
          
          dispatch(updateMessage({
            sessionId,
            messageId: data.messageId,
            updates: {
              content: currentMessageRef.current,
            },
          }));
        }
        break;

      case 'message_end':
        // 完成流式消息
        if (streamingMessageId === data.messageId) {
          dispatch(updateMessage({
            sessionId,
            messageId: data.messageId,
            updates: {
              isStreaming: false,
              metadata: data.metadata,
            },
          }));
          
          setStreamingMessageId(null);
          currentMessageRef.current = '';
        }
        break;

      case 'message_error':
        // 处理错误
        if (streamingMessageId === data.messageId) {
          dispatch(updateMessage({
            sessionId,
            messageId: data.messageId,
            updates: {
              content: 'Sorry, an error occurred while processing your message.',
              isStreaming: false,
              hasError: true,
            },
          }));
          
          setStreamingMessageId(null);
          currentMessageRef.current = '';
        }
        break;
    }
  }, [dispatch, sessionId, streamingMessageId]);

  // SSE连接用于消息流
  const { connect, disconnect, isConnected } = useSSE({
    url: `/api/chat/${sessionId}/stream`,
    onMessage: handleStreamMessage,
    onError: (error) => {
      console.error('Chat streaming error:', error);
      // 如果有正在流式传输的消息，标记为错误
      if (streamingMessageId) {
        dispatch(updateMessage({
          sessionId,
          messageId: streamingMessageId,
          updates: {
            content: currentMessageRef.current || 'Connection interrupted.',
            isStreaming: false,
            hasError: true,
          },
        }));
        setStreamingMessageId(null);
      }
    },
  });

  return {
    connect,
    disconnect,
    isConnected,
    isStreaming: !!streamingMessageId,
  };
};
```

### 11.4 流式消息组件

```tsx
// src/components/business/StreamingMessage/StreamingMessage.tsx
import React, { useEffect, useRef } from 'react';
import { TypeAnimation } from 'react-type-animation';

import styles from './StreamingMessage.module.css';

interface StreamingMessageProps {
  content: string;
  isStreaming: boolean;
  hasError?: boolean;
  onStreamComplete?: () => void;
}

export const StreamingMessage: React.FC<StreamingMessageProps> = ({
  content,
  isStreaming,
  hasError = false,
  onStreamComplete,
}) => {
  const previousContentRef = useRef('');
  const containerRef = useRef<HTMLDivElement>(null);

  // 自动滚动到底部
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }
  }, [content]);

  // 流式完成时的回调
  useEffect(() => {
    if (!isStreaming && previousContentRef.current !== content) {
      previousContentRef.current = content;
      onStreamComplete?.();
    }
  }, [isStreaming, content, onStreamComplete]);

  return (
    <div 
      ref={containerRef}
      className={cn(styles.streamingMessage, {
        [styles.streaming]: isStreaming,
        [styles.error]: hasError,
      })}
    >
      {/* 消息内容 */}
      <div className={styles.content}>
        {isStreaming ? (
          <TypeAnimation
            sequence={[content]}
            wrapper="span"
            speed={99} // 最快速度，因为内容是实时流入的
            style={{ whiteSpace: 'pre-wrap' }}
            cursor={false}
          />
        ) : (
          <span style={{ whiteSpace: 'pre-wrap' }}>{content}</span>
        )}
      </div>

      {/* 流式指示器 */}
      {isStreaming && (
        <div className={styles.streamingIndicator}>
          <div className={styles.dot} />
          <div className={styles.dot} />
          <div className={styles.dot} />
        </div>
      )}

      {/* 错误指示器 */}
      {hasError && (
        <div className={styles.errorIndicator}>
          <span className={styles.errorIcon}>⚠️</span>
          <span className={styles.errorText}>Message delivery failed</span>
        </div>
      )}
    </div>
  );
};
```

---

## 12. 部署和构建规范

### 12.1 Vite构建配置

```ts
// vite.config.ts
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig(({ command, mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  
  return {
    plugins: [
      react({
        jsxImportSource: '@emotion/react',
        babel: {
          plugins: ['@emotion/babel-plugin'],
        },
      }),
    ],
    
    // 路径解析
    resolve: {
      alias: {
        '@': resolve(__dirname, './src'),
        '@/components': resolve(__dirname, './src/components'),
        '@/hooks': resolve(__dirname, './src/hooks'),
        '@/store': resolve(__dirname, './src/store'),
        '@/utils': resolve(__dirname, './src/utils'),
        '@/types': resolve(__dirname, './src/types'),
        '@/services': resolve(__dirname, './src/services'),
        '@/assets': resolve(__dirname, './src/assets'),
      },
    },
    
    // 开发服务器配置
    server: {
      port: 3000,
      open: true,
      cors: true,
      proxy: {
        '/api': {
          target: env.VITE_API_BASE_URL || 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
        },
      },
    },
    
    // 构建配置
    build: {
      outDir: 'dist',
      sourcemap: mode === 'development',
      minify: 'terser',
      terserOptions: {
        compress: {
          drop_console: mode === 'production',
          drop_debugger: true,
        },
      },
      rollupOptions: {
        output: {
          // 代码分割
          manualChunks: {
            vendor: ['react', 'react-dom'],
            ui: ['@headlessui/react', 'framer-motion'],
            state: ['@reduxjs/toolkit', 'react-redux'],
            router: ['react-router-dom'],
            utils: ['date-fns', 'lodash-es'],
          },
          // 资源文件命名
          chunkFileNames: 'js/[name]-[hash].js',
          entryFileNames: 'js/[name]-[hash].js',
          assetFileNames: (assetInfo) => {
            const info = assetInfo.name!.split('.');
            const ext = info[info.length - 1];
            if (/\.(mp4|webm|ogg|mp3|wav|flac|aac)$/.test(assetInfo.name!)) {
              return `media/[name]-[hash].${ext}`;
            }
            if (/\.(png|jpe?g|gif|svg|ico|webp)$/.test(assetInfo.name!)) {
              return `images/[name]-[hash].${ext}`;
            }
            if (/\.(woff2?|eot|ttf|otf)$/.test(assetInfo.name!)) {
              return `fonts/[name]-[hash].${ext}`;
            }
            return `assets/[name]-[hash].${ext}`;
          },
        },
      },
      // 压缩设置
      chunkSizeWarningLimit: 1000,
    },
    
    // 环境变量
    define: {
      __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
      __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
    },
  };
});
```

### 12.2 环境变量配置

```bash
# .env.development
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE=TradeFlow Development
VITE_ENABLE_MOCK=true
VITE_LOG_LEVEL=debug

# WebSocket/SSE配置
VITE_WS_URL=ws://localhost:8000/ws
VITE_SSE_URL=http://localhost:8000/api/events

# 第三方服务
VITE_SENTRY_DSN=""
VITE_GA_TRACKING_ID=""
```

```bash
# .env.production
VITE_API_BASE_URL=https://api.tradeflow.com
VITE_APP_TITLE=TradeFlow
VITE_ENABLE_MOCK=false
VITE_LOG_LEVEL=error

# WebSocket/SSE配置
VITE_WS_URL=wss://api.tradeflow.com/ws
VITE_SSE_URL=https://api.tradeflow.com/api/events

# 第三方服务
VITE_SENTRY_DSN=https://your-sentry-dsn
VITE_GA_TRACKING_ID=G-XXXXXXXXXX

# CDN配置
VITE_CDN_BASE_URL=https://cdn.tradeflow.com
```

### 12.3 Docker配置

```dockerfile
# Dockerfile
# 构建阶段
FROM node:18-alpine AS builder

# 设置工作目录
WORKDIR /app

# 复制package文件
COPY package*.json pnpm-lock.yaml ./

# 安装pnpm
RUN npm install -g pnpm

# 安装依赖
RUN pnpm install --frozen-lockfile

# 复制源代码
COPY . .

# 构建应用
RUN pnpm run build

# 生产阶段
FROM nginx:alpine AS production

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制nginx配置
COPY nginx.conf /etc/nginx/nginx.conf

# 暴露端口
EXPOSE 80

# 启动nginx
CMD ["nginx", "-g", "daemon off;"]
```

```nginx
# nginx.conf
events {
  worker_connections 1024;
}

http {
  include /etc/nginx/mime.types;
  default_type application/octet-stream;

  # 启用gzip压缩
  gzip on;
  gzip_vary on;
  gzip_min_length 1024;
  gzip_types
    text/plain
    text/css
    text/xml
    text/javascript
    application/javascript
    application/json
    application/xml+rss;

  server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
      expires 1y;
      add_header Cache-Control "public, immutable";
    }

    # HTML文件不缓存
    location ~* \.html$ {
      expires -1;
      add_header Cache-Control "no-cache, no-store, must-revalidate";
    }

    # API代理
    location /api/ {
      proxy_pass http://backend:8000;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto $scheme;
    }

    # SSE代理
    location /api/events/ {
      proxy_pass http://backend:8000;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto $scheme;
      
      # SSE特殊配置
      proxy_buffering off;
      proxy_cache off;
      proxy_set_header Connection '';
      proxy_http_version 1.1;
      chunked_transfer_encoding off;
    }

    # SPA路由处理
    location / {
      try_files $uri $uri/ /index.html;
    }

    # 健康检查
    location /health {
      access_log off;
      return 200 "healthy\n";
      add_header Content-Type text/plain;
    }
  }
}
```

### 12.4 CI/CD配置

```yaml
# .github/workflows/deploy.yml
name: Deploy Frontend

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'pnpm'

      - name: Install pnpm
        uses: pnpm/action-setup@v2
        with:
          version: 8

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Run linting
        run: pnpm run lint

      - name: Run type checking
        run: pnpm run type-check

      - name: Run unit tests
        run: pnpm run test:unit

      - name: Run E2E tests
        run: pnpm run test:e2e

      - name: Upload coverage reports
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage/lcov.info

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'pnpm'

      - name: Install pnpm
        uses: pnpm/action-setup@v2
        with:
          version: 8

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Build application
        run: pnpm run build
        env:
          VITE_API_BASE_URL: ${{ secrets.PROD_API_BASE_URL }}
          VITE_SENTRY_DSN: ${{ secrets.SENTRY_DSN }}

      - name: Build Docker image
        run: |
          docker build -t tradeflow-frontend:${{ github.sha }} .
          docker tag tradeflow-frontend:${{ github.sha }} tradeflow-frontend:latest

      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker push tradeflow-frontend:${{ github.sha }}
          docker push tradeflow-frontend:latest

      - name: Deploy to production
        uses: appleboy/ssh-action@v0.1.5
        with:
          host: ${{ secrets.PROD_HOST }}
          username: ${{ secrets.PROD_USERNAME }}
          key: ${{ secrets.PROD_SSH_KEY }}
          script: |
            docker pull tradeflow-frontend:latest
            docker stop tradeflow-frontend || true
            docker rm tradeflow-frontend || true
            docker run -d --name tradeflow-frontend -p 80:80 tradeflow-frontend:latest
```

---

## 总结

本前端开发规范文档涵盖了TradeFlow项目的完整前端开发指南，包括：

1. **技术栈标准化** - React 18 + TypeScript + Vite现代化技术栈
2. **架构设计** - 基于原子设计的组件化架构和模块化代码组织
3. **样式系统** - CSS Variables + CSS Modules的可维护样式方案
4. **状态管理** - Redux Toolkit + RTK Query的现代状态管理
5. **国际化支持** - 完整的多语言解决方案
6. **性能优化** - 代码分割、懒加载、缓存等优化策略
7. **响应式设计** - 移动优先的响应式布局系统
8. **代码质量** - ESLint + Prettier + TypeScript的质量保障
9. **测试规范** - 单元测试 + 集成测试 + E2E测试的完整测试策略  
10. **实时通信** - 基于SSE的实时数据更新机制
11. **部署方案** - Docker + CI/CD的自动化部署流程

这份规范确保了代码的一致性、可维护性和可扩展性，为TradeFlow项目的前端开发提供了坚实的技术基础。

开发团队应严格遵循本规范，并根据项目进展适时更新和完善相关标准。