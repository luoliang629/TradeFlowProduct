import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';
import type { User } from '../types';

interface AuthState {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
}

const initialState: AuthState = {
  user: null,
  token: null,
  refreshToken: null,
  isAuthenticated: false,
  loading: false,
  error: null,
};

// 异步thunks
export const loginWithOAuth = createAsyncThunk(
  'auth/loginWithOAuth',
  async (provider: 'google' | 'github', { rejectWithValue }) => {
    try {
      // 动态导入API服务以避免循环依赖
      const { apiService } = await import('../services');
      const response = await apiService.auth.loginWithOAuth(provider);
      
      if (response.success) {
        // 存储token到localStorage
        localStorage.setItem('access_token', response.data.token);
        localStorage.setItem('refresh_token', response.data.refreshToken);
        
        return response.data;
      } else {
        throw new Error('登录失败');
      }
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : '登录失败');
    }
  }
);

export const refreshAccessToken = createAsyncThunk(
  'auth/refreshToken',
  async (refreshToken: string, { rejectWithValue }) => {
    try {
      const { apiService } = await import('../services');
      const response = await apiService.auth.refreshToken(refreshToken);
      
      if (response.success) {
        // 更新localStorage中的token
        localStorage.setItem('access_token', response.data.token);
        localStorage.setItem('refresh_token', response.data.refreshToken);
        
        return response.data;
      } else {
        throw new Error('Token刷新失败');
      }
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Token刷新失败');
    }
  }
);

export const logout = createAsyncThunk('auth/logout', async () => {
  // 清理本地存储等
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
});

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearError: state => {
      state.error = null;
    },
    setTokens: (
      state,
      action: PayloadAction<{ token: string; refreshToken?: string; user?: User }>
    ) => {
      state.token = action.payload.token;
      if (action.payload.refreshToken) {
        state.refreshToken = action.payload.refreshToken;
      }
      if (action.payload.user) {
        state.user = action.payload.user;
      }
      state.isAuthenticated = true;
      state.loading = false;
      state.error = null;
    },
    setAuthLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
  },
  extraReducers: builder => {
    builder
      // OAuth登录
      .addCase(loginWithOAuth.pending, state => {
        state.loading = true;
        state.error = null;
      })
      .addCase(loginWithOAuth.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload.user;
        state.token = action.payload.token;
        state.refreshToken = action.payload.refreshToken;
        state.isAuthenticated = true;
        state.error = null;
      })
      .addCase(loginWithOAuth.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // Token刷新
      .addCase(refreshAccessToken.fulfilled, (state, action) => {
        state.token = action.payload.token;
        state.refreshToken = action.payload.refreshToken;
      })
      .addCase(refreshAccessToken.rejected, state => {
        // Token刷新失败，退出登录
        state.user = null;
        state.token = null;
        state.refreshToken = null;
        state.isAuthenticated = false;
      })
      // 登出
      .addCase(logout.fulfilled, state => {
        state.user = null;
        state.token = null;
        state.refreshToken = null;
        state.isAuthenticated = false;
        state.error = null;
      });
  },
});

export const { clearError, setTokens, setAuthLoading } = authSlice.actions;
export default authSlice.reducer;