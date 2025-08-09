import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Card, Spin, Result, Button } from 'antd';
import { LoadingOutlined, CheckCircleOutlined, ExclamationCircleOutlined } from '@ant-design/icons';
import { useAppDispatch } from '../../store/hooks';
import { setTokens } from '../../store/authSlice';
import { authService } from '../../services/auth';

type CallbackStatus = 'loading' | 'success' | 'error';

const OAuthCallbackPage: React.FC = () => {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const [searchParams] = useSearchParams();
  const [status, setStatus] = useState<CallbackStatus>('loading');
  const [error, setError] = useState<string>('');

  useEffect(() => {
    const handleCallback = async () => {
      try {
        const code = searchParams.get('code');
        const state = searchParams.get('state');
        const errorParam = searchParams.get('error');

        // 检查是否有错误参数
        if (errorParam) {
          const errorDescription = searchParams.get('error_description') || '用户取消了授权';
          throw new Error(errorDescription);
        }

        // 检查必需参数
        if (!code || !state) {
          throw new Error('缺少必需的授权参数');
        }

        // 处理OAuth回调
        const authResult = await authService.handleOAuthCallback(code, state);

        // 更新Redux状态
        dispatch(setTokens({
          token: authResult.token,
          refreshToken: authResult.refreshToken,
        }));

        setStatus('success');

        // 延迟跳转，让用户看到成功状态
        setTimeout(() => {
          const redirectTo = sessionStorage.getItem('auth_redirect') || '/dashboard';
          sessionStorage.removeItem('auth_redirect');
          navigate(redirectTo, { replace: true });
        }, 2000);

      } catch (error) {
        console.error('OAuth回调处理失败:', error);
        setError(error instanceof Error ? error.message : '登录失败');
        setStatus('error');
      }
    };

    handleCallback();
  }, [searchParams, dispatch, navigate]);

  const handleRetry = () => {
    navigate('/auth/login', { replace: true });
  };

  const renderContent = () => {
    switch (status) {
      case 'loading':
        return (
          <div className="text-center py-8">
            <Spin 
              indicator={<LoadingOutlined style={{ fontSize: 48 }} spin />} 
              size="large" 
            />
            <div className="mt-4 text-lg text-gray-600">
              正在处理登录...
            </div>
            <div className="mt-2 text-sm text-gray-400">
              请稍等，我们正在验证您的身份
            </div>
          </div>
        );

      case 'success':
        return (
          <Result
            icon={<CheckCircleOutlined style={{ color: '#52c41a' }} />}
            title="登录成功！"
            subTitle="正在跳转到应用..."
            extra={
              <div className="text-sm text-gray-500">
                如果页面没有自动跳转，请手动刷新页面
              </div>
            }
          />
        );

      case 'error':
        return (
          <Result
            icon={<ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />}
            title="登录失败"
            subTitle={error || '发生了未知错误，请重试'}
            extra={
              <Button type="primary" onClick={handleRetry}>
                返回登录
              </Button>
            }
          />
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg">
              <span className="text-white text-2xl font-bold">TF</span>
            </div>
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            TradeFlow
          </h1>
        </div>

        {/* 内容卡片 */}
        <Card className="shadow-xl border-0">
          {renderContent()}
        </Card>

        {/* 底部信息 */}
        {status === 'error' && (
          <div className="text-center mt-6 text-sm text-gray-500">
            如果问题持续存在，请联系 
            <a href="mailto:support@tradeflow.ai" className="text-blue-500 hover:text-blue-600 ml-1">
              技术支持
            </a>
          </div>
        )}
      </div>
    </div>
  );
};

export default OAuthCallbackPage;