import React, { useState, useEffect } from 'react';
import { Card, Button, Form, Input, Checkbox, Divider, Typography, Space, message, Alert } from 'antd';
import { GoogleOutlined, GithubOutlined, LockOutlined, UserOutlined, EyeInvisibleOutlined, EyeTwoTone } from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../../store/hooks';
import { loginWithOAuth, clearError } from '../../store/authSlice';
import { authService } from '../../services/auth';

const { Title, Text, Link } = Typography;

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const dispatch = useAppDispatch();
  const { loading, error, isAuthenticated } = useAppSelector(state => state.auth);
  const [rememberMe, setRememberMe] = useState(true);
  const [form] = Form.useForm();

  // 获取重定向路径
  const from = location.state?.from || '/dashboard';

  // 如果已经登录，直接跳转
  useEffect(() => {
    if (isAuthenticated) {
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, navigate, from]);

  // 清理错误
  useEffect(() => {
    return () => {
      dispatch(clearError());
    };
  }, [dispatch]);

  // OAuth登录
  const handleOAuthLogin = async (provider: 'google' | 'github') => {
    try {
      dispatch(clearError()); // 清理之前的错误
      
      // 保存重定向路径
      if (from !== '/dashboard') {
        sessionStorage.setItem('auth_redirect', from);
      }
      
      // 使用新的认证服务
      await authService.initiateOAuthLogin(provider);
      
      // 注意：如果是生产环境，上面的调用会重定向到OAuth提供商
      // 如果是开发环境(Mock)，会返回结果并继续执行下面的代码
      message.success('登录成功！');
      navigate(from, { replace: true });
    } catch (error) {
      console.error('登录失败:', error);
      // 如果不是重定向错误，显示错误信息
      if (!(error instanceof Error && error.message === 'Redirecting to OAuth provider')) {
        // 错误信息会在Redux状态中显示，这里不显示message
      }
    }
  };

  // 表单登录（预留）
  const handleFormLogin = async (values: any) => {
    message.info('邮箱登录功能即将推出');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        {/* Logo和标题 */}
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center shadow-lg">
              <Text className="text-white text-3xl font-bold">TF</Text>
            </div>
          </div>
          <Title level={2} className="mb-2">
            欢迎使用 TradeFlow
          </Title>
          <Text className="text-gray-600">
            AI驱动的全球B2B贸易智能助手
          </Text>
        </div>

        {/* 登录卡片 */}
        <Card className="shadow-xl border-0">
          {/* 错误提示 */}
          {error && (
            <Alert
              message="登录失败"
              description={error}
              type="error"
              showIcon
              closable
              onClose={() => dispatch(clearError())}
              className="mb-4"
            />
          )}
          {/* OAuth登录 */}
          <div className="space-y-3">
            <Button
              block
              size="large"
              icon={<GoogleOutlined />}
              onClick={() => handleOAuthLogin('google')}
              loading={loading}
              className="h-12 font-medium"
              style={{
                backgroundColor: '#4285f4',
                color: 'white',
                border: 'none',
              }}
            >
              使用 Google 账号登录
            </Button>
            
            <Button
              block
              size="large"
              icon={<GithubOutlined />}
              onClick={() => handleOAuthLogin('github')}
              loading={loading}
              className="h-12 font-medium bg-gray-900 text-white border-0 hover:bg-gray-800"
            >
              使用 GitHub 账号登录
            </Button>
          </div>

          <Divider>
            <Text className="text-gray-500">或使用邮箱登录</Text>
          </Divider>

          {/* 邮箱登录表单 */}
          <Form
            name="login"
            onFinish={handleFormLogin}
            autoComplete="off"
            layout="vertical"
          >
            <Form.Item
              name="email"
              rules={[
                { required: true, message: '请输入邮箱' },
                { type: 'email', message: '请输入有效的邮箱地址' }
              ]}
            >
              <Input
                size="large"
                prefix={<UserOutlined />}
                placeholder="邮箱地址"
                className="h-12"
              />
            </Form.Item>

            <Form.Item
              name="password"
              rules={[{ required: true, message: '请输入密码' }]}
            >
              <Input.Password
                size="large"
                prefix={<LockOutlined />}
                placeholder="密码"
                className="h-12"
                iconRender={(visible) => (visible ? <EyeTwoTone /> : <EyeInvisibleOutlined />)}
              />
            </Form.Item>

            <Form.Item>
              <div className="flex justify-between items-center">
                <Checkbox
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                >
                  记住我
                </Checkbox>
                <Link href="#" className="text-blue-500">
                  忘记密码？
                </Link>
              </div>
            </Form.Item>

            <Form.Item>
              <Button
                type="primary"
                htmlType="submit"
                block
                size="large"
                loading={loading}
                className="h-12 font-medium"
              >
                登录
              </Button>
            </Form.Item>
          </Form>

          {/* 注册链接 */}
          <div className="text-center">
            <Text className="text-gray-600">
              还没有账号？{' '}
              <Link href="#" className="text-blue-500 font-medium">
                立即注册
              </Link>
            </Text>
          </div>
        </Card>

        {/* 底部信息 */}
        <div className="text-center mt-8">
          <Space split={<span className="text-gray-400">·</span>}>
            <Link href="#" className="text-gray-600 hover:text-gray-800">
              服务条款
            </Link>
            <Link href="#" className="text-gray-600 hover:text-gray-800">
              隐私政策
            </Link>
            <Link href="#" className="text-gray-600 hover:text-gray-800">
              帮助中心
            </Link>
          </Space>
          <div className="mt-4 text-gray-500 text-sm">
            © 2025 TradeFlow. All rights reserved.
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;