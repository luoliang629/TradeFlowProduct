import axios from 'axios';
import type { AxiosResponse, AxiosError } from 'axios';
import { store } from '../store';
import { refreshAccessToken, logout } from '../store/authSlice';
import { addNotification } from '../store/uiSlice';
import type { ApiResponse } from '../types';

// 创建axios实例
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const state = store.getState();
    const token = state.auth.token;
    
    // 如果有token，添加到请求头
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // 添加请求ID用于追踪
    config.headers['X-Request-ID'] = `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    // 成功响应直接返回
    return response;
  },
  async (error: AxiosError<ApiResponse>) => {
    const originalRequest = error.config as any;
    
    // 处理401错误（token过期）
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      const state = store.getState();
      const refreshToken = state.auth.refreshToken;
      
      if (refreshToken) {
        try {
          // 尝试刷新token
          await store.dispatch(refreshAccessToken(refreshToken)).unwrap();
          
          // 重新发起原始请求
          return api(originalRequest);
        } catch (refreshError) {
          // 刷新失败，退出登录
          store.dispatch(logout());
          store.dispatch(addNotification({
            type: 'error',
            title: '登录已过期',
            message: '请重新登录',
          }));
          return Promise.reject(refreshError);
        }
      } else {
        // 没有refresh token，直接退出
        store.dispatch(logout());
        return Promise.reject(error);
      }
    }
    
    // 处理其他错误
    const errorMessage = error.response?.data?.error?.message || '网络请求失败';
    
    // 显示错误通知（排除某些不需要显示的错误）
    if (error.response?.status !== 401) {
      store.dispatch(addNotification({
        type: 'error',
        title: '请求失败',
        message: errorMessage,
      }));
    }
    
    return Promise.reject(error);
  }
);

// API方法封装
export const apiClient = {
  // GET请求
  get: <T = any>(url: string, params?: any) => 
    api.get<ApiResponse<T>>(url, { params }).then(res => res.data),
  
  // POST请求
  post: <T = any>(url: string, data?: any) => 
    api.post<ApiResponse<T>>(url, data).then(res => res.data),
  
  // PUT请求
  put: <T = any>(url: string, data?: any) => 
    api.put<ApiResponse<T>>(url, data).then(res => res.data),
  
  // DELETE请求
  delete: <T = any>(url: string) => 
    api.delete<ApiResponse<T>>(url).then(res => res.data),
  
  // PATCH请求
  patch: <T = any>(url: string, data?: any) => 
    api.patch<ApiResponse<T>>(url, data).then(res => res.data),
  
  // 文件上传
  upload: <T = any>(url: string, file: File, onProgress?: (progress: number) => void) => {
    const formData = new FormData();
    formData.append('file', file);
    
    return api.post<ApiResponse<T>>(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded / progressEvent.total) * 100);
          onProgress(progress);
        }
      },
    }).then(res => res.data);
  },
};

export default api;