import { createBrowserRouter, Navigate } from 'react-router-dom';
import { lazy, Suspense } from 'react';

import AppLayout from '../layouts/AppLayout';
// TODO: 这些组件将在后续任务中实现
// import AuthLayout from '../layouts/AuthLayout';
// import LoadingSpinner from '../components/common/LoadingSpinner';
// import ProtectedRoute from './ProtectedRoute';

// 临时LoadingSpinner组件
const LoadingSpinner = () => <div className="flex justify-center items-center h-32">加载中...</div>;

// 懒加载页面组件
const Dashboard = lazy(() => import('../pages/Dashboard'));
const ChatPage = lazy(() => import('../pages/ChatPage'));
const TradePage = lazy(() => import('../pages/TradePage'));
const LoginPage = lazy(() => import('../pages/auth/LoginPage'));
const OAuthCallbackPage = lazy(() => import('../pages/auth/OAuthCallbackPage'));
const UserProfilePage = lazy(() => import('../pages/user/UserProfilePage'));

// TODO: 这些页面组件将在后续任务中实现
const ContactsPage = () => <div className="p-6">客户管理 - 待实现</div>;
const DocumentsPage = () => <div className="p-6">文档中心 - 待实现</div>;
const AnalyticsPage = () => <div className="p-6">数据分析 - 待实现</div>;
const SettingsPage = () => <div className="p-6">系统设置 - 待实现</div>;
const HelpPage = () => <div className="p-6">帮助中心 - 待实现</div>;
const NotFoundPage = () => <div className="p-6">页面未找到</div>;

// 贸易相关子页面
const BuyersPage = () => <div className="p-6">买家开发 - 待实现</div>;
const SuppliersPage = () => <div className="p-6">供应商管理 - 待实现</div>;
const ProductsPage = () => <div className="p-6">产品管理 - 待实现</div>;
const OrdersPage = () => <div className="p-6">订单跟踪 - 待实现</div>;

// 路由加载包装器
const RouteWrapper = ({ children }: { children: React.ReactNode }) => (
  <Suspense fallback={<LoadingSpinner />}>{children}</Suspense>
);

export const router = createBrowserRouter([
  {
    path: '/auth',
    element: <div>Auth Layout</div>, // TODO: AuthLayout组件
    children: [
      {
        path: 'login',
        element: (
          <RouteWrapper>
            <LoginPage />
          </RouteWrapper>
        ),
      },
      {
        path: 'callback',
        element: (
          <RouteWrapper>
            <OAuthCallbackPage />
          </RouteWrapper>
        ),
      },
      {
        path: '',
        element: <Navigate to="/auth/login" replace />,
      },
    ],
  },
  {
    path: '/',
    element: <AppLayout />, // 暂时去掉ProtectedRoute，方便开发测试
    children: [
      {
        path: '',
        element: <Navigate to="/dashboard" replace />,
      },
      {
        path: 'dashboard',
        element: (
          <RouteWrapper>
            <Dashboard />
          </RouteWrapper>
        ),
      },
      {
        path: 'chat',
        element: (
          <RouteWrapper>
            <ChatPage />
          </RouteWrapper>
        ),
      },
      {
        path: 'chat/:sessionId',
        element: (
          <RouteWrapper>
            <ChatPage />
          </RouteWrapper>
        ),
      },
      {
        path: 'trade',
        element: (
          <RouteWrapper>
            <TradePage />
          </RouteWrapper>
        ),
        children: [
          {
            path: 'buyers',
            element: <BuyersPage />,
          },
          {
            path: 'suppliers',
            element: <SuppliersPage />,
          },
          {
            path: 'products',
            element: <ProductsPage />,
          },
          {
            path: 'orders',
            element: <OrdersPage />,
          },
        ],
      },
      {
        path: 'contacts',
        element: <ContactsPage />,
      },
      {
        path: 'documents',
        element: <DocumentsPage />,
      },
      {
        path: 'analytics',
        element: <AnalyticsPage />,
      },
      {
        path: 'settings',
        element: <SettingsPage />,
      },
      {
        path: 'help',
        element: <HelpPage />,
      },
      {
        path: 'profile',
        element: (
          <RouteWrapper>
            <UserProfilePage />
          </RouteWrapper>
        ),
      },
    ],
  },
  {
    path: '*',
    element: <NotFoundPage />,
  },
]);

export default router;