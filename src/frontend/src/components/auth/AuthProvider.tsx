import React, { useEffect } from 'react';
import { useAppDispatch, useAppSelector } from '../../store/hooks';
import { setTokens, setAuthLoading } from '../../store/authSlice';
import { authService } from '../../services/auth';

interface AuthProviderProps {
  children: React.ReactNode;
}

/**
 * 认证提供者组件
 * 负责在应用启动时恢复用户的认证状态
 */
const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const dispatch = useAppDispatch();
  const { loading } = useAppSelector(state => state.auth);

  useEffect(() => {
    const initializeAuth = async () => {
      try {
        // 尝试从本地存储恢复认证状态
        const authState = await authService.restoreAuthState();
        
        if (authState) {
          // 恢复认证状态到Redux
          dispatch(setTokens({
            token: authState.token,
            refreshToken: authState.refreshToken,
          }));
          
          // 这里可以继续设置用户信息等
          console.log('认证状态已恢复');
        } else {
          console.log('无有效的认证状态');
        }
      } catch (error) {
        console.error('认证初始化失败:', error);
        // 清理可能损坏的认证数据
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
      }
    };

    initializeAuth();
  }, [dispatch]);

  // 在认证检查完成前，可以显示加载界面
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-center">
          <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg mx-auto mb-4">
            <span className="text-white text-2xl font-bold">TF</span>
          </div>
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <div className="text-gray-600">正在加载...</div>
        </div>
      </div>
    );
  }

  return <>{children}</>;
};

export default AuthProvider;