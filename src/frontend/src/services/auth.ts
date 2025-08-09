import { apiService } from './index';

/**
 * OAuth认证服务
 * 处理OAuth登录流程、Token管理和状态同步
 */
export class AuthService {
  private static instance: AuthService;
  
  // 单例模式
  public static getInstance(): AuthService {
    if (!AuthService.instance) {
      AuthService.instance = new AuthService();
    }
    return AuthService.instance;
  }

  /**
   * 启动OAuth登录流程
   * 对于真实环境，这会重定向到OAuth提供商
   * 对于Mock环境，这会模拟登录流程
   */
  public async initiateOAuthLogin(provider: 'google' | 'github'): Promise<{
    user: any;
    token: string;
    refreshToken: string;
  }> {
    try {
      // 如果是生产环境，需要处理OAuth重定向
      if (import.meta.env.PROD && import.meta.env.VITE_USE_MOCK_API === 'false') {
        // 生成state参数用于安全验证
        const state = this.generateState();
        sessionStorage.setItem('oauth_state', state);
        
        // 构建OAuth授权URL
        const authUrl = this.buildAuthUrl(provider, state);
        
        // 重定向到OAuth提供商
        window.location.href = authUrl;
        
        // 这里不会返回，因为已经重定向了
        throw new Error('Redirecting to OAuth provider');
      }
      
      // 开发环境使用Mock API
      const response = await apiService.auth.loginWithOAuth(provider);
      if (response.success) {
        return response.data;
      } else {
        throw new Error(response.error?.message || '登录失败');
      }
    } catch (error) {
      console.error('OAuth登录失败:', error);
      throw error;
    }
  }

  /**
   * 处理OAuth回调
   * 在OAuth提供商重定向回来时调用
   */
  public async handleOAuthCallback(code: string, state: string): Promise<{
    user: any;
    token: string;
    refreshToken: string;
  }> {
    try {
      // 验证state参数
      const savedState = sessionStorage.getItem('oauth_state');
      if (savedState !== state) {
        throw new Error('Invalid state parameter');
      }
      
      // 清理state
      sessionStorage.removeItem('oauth_state');
      
      // 交换授权码获取token
      const response = await apiService.auth.loginWithOAuth('google'); // 这里需要修改API来处理回调
      
      if (response.success) {
        return response.data;
      } else {
        throw new Error(response.error?.message || '登录失败');
      }
    } catch (error) {
      console.error('OAuth回调处理失败:', error);
      throw error;
    }
  }

  /**
   * 检查并恢复认证状态
   * 应用启动时调用，检查本地存储的token是否有效
   */
  public async restoreAuthState(): Promise<{
    user: any;
    token: string;
    refreshToken: string;
  } | null> {
    try {
      const token = localStorage.getItem('access_token');
      const refreshToken = localStorage.getItem('refresh_token');
      
      if (!token) {
        return null;
      }
      
      // 验证token是否有效
      try {
        const response = await apiService.auth.getCurrentUser();
        if (response.success) {
          return {
            user: response.data,
            token,
            refreshToken: refreshToken || '',
          };
        }
      } catch (error) {
        // token可能过期，尝试刷新
        if (refreshToken) {
          try {
            const refreshResponse = await apiService.auth.refreshToken(refreshToken);
            if (refreshResponse.success) {
              // 更新存储的token
              localStorage.setItem('access_token', refreshResponse.data.token);
              localStorage.setItem('refresh_token', refreshResponse.data.refreshToken);
              
              // 获取用户信息
              const userResponse = await apiService.auth.getCurrentUser();
              if (userResponse.success) {
                return {
                  user: userResponse.data,
                  token: refreshResponse.data.token,
                  refreshToken: refreshResponse.data.refreshToken,
                };
              }
            }
          } catch (refreshError) {
            console.warn('刷新token失败:', refreshError);
          }
        }
        
        // 清理无效的token
        this.clearAuthTokens();
        return null;
      }
    } catch (error) {
      console.error('恢复认证状态失败:', error);
      this.clearAuthTokens();
      return null;
    }
    
    return null;
  }

  /**
   * 登出
   */
  public async logout(): Promise<void> {
    try {
      // 调用服务器登出API
      await apiService.auth.logout();
    } catch (error) {
      console.warn('服务器登出失败:', error);
    } finally {
      // 无论服务器登出是否成功，都清理本地存储
      this.clearAuthTokens();
    }
  }

  /**
   * 清理认证token
   */
  private clearAuthTokens(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  /**
   * 生成随机state参数
   */
  private generateState(): string {
    const array = new Uint32Array(8);
    crypto.getRandomValues(array);
    return Array.from(array, dec => ('0' + dec.toString(16)).substr(-2)).join('');
  }

  /**
   * 构建OAuth授权URL
   */
  private buildAuthUrl(provider: 'google' | 'github', state: string): string {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
    const redirectUri = `${window.location.origin}/auth/callback`;
    
    // OAuth配置
    const oauthConfigs = {
      google: {
        authUrl: 'https://accounts.google.com/o/oauth2/v2/auth',
        clientId: import.meta.env.VITE_GOOGLE_CLIENT_ID,
        scope: 'openid profile email',
      },
      github: {
        authUrl: 'https://github.com/login/oauth/authorize',
        clientId: import.meta.env.VITE_GITHUB_CLIENT_ID,
        scope: 'user:email',
      },
    };
    
    const config = oauthConfigs[provider];
    if (!config.clientId) {
      throw new Error(`${provider} OAuth客户端ID未配置`);
    }
    
    const params = new URLSearchParams({
      client_id: config.clientId,
      redirect_uri: redirectUri,
      scope: config.scope,
      response_type: 'code',
      state,
    });
    
    return `${config.authUrl}?${params.toString()}`;
  }
}

export const authService = AuthService.getInstance();