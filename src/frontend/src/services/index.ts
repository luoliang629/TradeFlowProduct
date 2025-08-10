import { apiClient } from './api';
import { mockApi } from './mockApi';
import type { User, Session, Message, Buyer, Supplier, FileInfo } from '../types';

// 根据环境变量决定使用真实API还是Mock API
const USE_MOCK = import.meta.env.VITE_USE_MOCK_API !== 'false';

// 统一的API服务接口
export const apiService = {
  // 认证相关API
  auth: {
    loginWithOAuth: async (provider: 'google' | 'github') => {
      if (USE_MOCK) {
        return mockApi.auth.login(provider);
      }
      return apiClient.post('/auth/oauth/' + provider);
    },
    
    refreshToken: async (refreshToken: string) => {
      if (USE_MOCK) {
        return mockApi.auth.refresh(refreshToken);
      }
      return apiClient.post('/auth/refresh', { refresh_token: refreshToken });
    },
    
    getCurrentUser: async () => {
      if (USE_MOCK) {
        return mockApi.auth.me();
      }
      return apiClient.get<User>('/auth/me');
    },
    
    logout: async () => {
      if (USE_MOCK) {
        return { success: true };
      }
      return apiClient.post('/auth/logout');
    },
  },
  
  // 会话管理API
  sessions: {
    getList: async () => {
      if (USE_MOCK) {
        return mockApi.sessions.list();
      }
      return apiClient.get<Session[]>('/chat/sessions');
    },
    
    create: async (title?: string) => {
      if (USE_MOCK) {
        return mockApi.sessions.create(title);
      }
      return apiClient.post<Session>('/chat/sessions', { title });
    },
    
    delete: async (id: string) => {
      if (USE_MOCK) {
        return mockApi.sessions.delete(id);
      }
      return apiClient.delete(`/chat/sessions/${id}`);
    },
    
    update: async (id: string, data: Partial<Session>) => {
      if (USE_MOCK) {
        return { success: true, data: { ...data, id } };
      }
      return apiClient.patch<Session>(`/chat/sessions/${id}`, data);
    },
  },
  
  // 消息管理API
  messages: {
    getHistory: async (sessionId: string) => {
      if (USE_MOCK) {
        return mockApi.messages.list(sessionId);
      }
      return apiClient.get<Message[]>(`/chat/sessions/${sessionId}/messages`);
    },
    
    send: async (content: string, sessionId: string, files?: File[]) => {
      if (USE_MOCK) {
        return mockApi.messages.send(content, sessionId);
      }
      
      const formData = new FormData();
      formData.append('message', content);
      formData.append('session_id', sessionId);
      
      if (files) {
        files.forEach(file => {
          formData.append('files', file);
        });
      }
      
      return apiClient.post<Message>('/chat', formData);
    },
  },
  
  // SSE连接（实时通信）
  sse: {
    connect: (sessionId: string, token: string) => {
      if (USE_MOCK) {
        // Mock SSE连接，返回一个简单的EventSource模拟
        return {
          addEventListener: (event: string, handler: (e: any) => void) => {
            if (event === 'message') {
              // 模拟周期性消息
              setTimeout(() => {
                handler({
                  data: JSON.stringify({
                    type: 'message_chunk',
                    content: '这是模拟的流式消息内容...',
                    message_id: `msg_${Date.now()}`,
                  })
                });
              }, 1000);
            }
          },
          close: () => {},
        };
      }
      
      const url = `${import.meta.env.VITE_API_BASE_URL}/chat/stream?session_id=${sessionId}&token=${token}`;
      return new EventSource(url);
    },
  },
  
  // 买家推荐API
  buyers: {
    search: async (params?: any) => {
      if (USE_MOCK) {
        return mockApi.buyers.recommend(params?.keyword || '');
      }
      return apiClient.post<Buyer[]>('/buyers/search', params);
    },
    
    getStatistics: async () => {
      if (USE_MOCK) {
        return {
          success: true,
          data: {
            total_buyers: 45230,
            verified_buyers: 32150,
            premium_buyers: 12480,
            countries: 189,
            average_volume: '2.5M USD',
          }
        };
      }
      return apiClient.get('/buyers/statistics');
    },
    
    getRecommendations: async (query: string, filters?: any) => {
      if (USE_MOCK) {
        return mockApi.buyers.recommend(query);
      }
      return apiClient.post<Buyer[]>('/buyers/recommend', { query, ...filters });
    },
    
    getDetail: async (id: string) => {
      if (USE_MOCK) {
        return mockApi.buyers.detail(id);
      }
      return apiClient.get<Buyer>(`/buyers/${id}`);
    },
    
    generateContactTemplate: async (buyerId: string, productInfo: any) => {
      if (USE_MOCK) {
        return {
          success: true,
          data: {
            subject: 'Partnership Opportunity - Premium Electronics',
            content: 'Dear John Smith,\n\nI hope this email finds you well...',
          }
        };
      }
      return apiClient.post(`/buyers/${buyerId}/contact`, productInfo);
    },
  },
  
  // 供应商搜索API
  suppliers: {
    search: async (params?: any) => {
      if (USE_MOCK) {
        return mockApi.suppliers.search(params?.keyword || '');
      }
      return apiClient.post<Supplier[]>('/suppliers/search', params);
    },
    
    getStatistics: async () => {
      if (USE_MOCK) {
        return {
          success: true,
          data: {
            total_suppliers: 25680,
            verified_suppliers: 18234,
            gold_suppliers: 5432,
            countries: 156,
            average_rating: 4.3,
          }
        };
      }
      return apiClient.get('/suppliers/statistics');
    },
    
    getDetail: async (id: string) => {
      if (USE_MOCK) {
        return mockApi.suppliers.detail(id);
      }
      return apiClient.get<Supplier>(`/suppliers/${id}`);
    },
    
    compare: async (supplierIds: string[]) => {
      if (USE_MOCK) {
        return { success: true, data: { comparison: 'mock comparison data' } };
      }
      return apiClient.post('/suppliers/compare', { supplier_ids: supplierIds });
    },
  },
  
  // 文件管理API
  files: {
    upload: async (file: File, sessionId?: string, onProgress?: (progress: number) => void) => {
      if (USE_MOCK) {
        // 模拟上传进度
        if (onProgress) {
          const steps = [10, 30, 50, 70, 90, 100];
          steps.forEach((progress, index) => {
            setTimeout(() => onProgress(progress), index * 300);
          });
        }
        return mockApi.files.upload(file);
      }
      
      const formData = new FormData();
      formData.append('file', file);
      if (sessionId) {
        formData.append('session_id', sessionId);
      }
      
      return apiClient.upload<FileInfo>('/files', file, onProgress);
    },
    
    getList: async (sessionId?: string) => {
      if (USE_MOCK) {
        return mockApi.files.list();
      }
      const params = sessionId ? { session_id: sessionId } : {};
      return apiClient.get<FileInfo[]>('/files', params);
    },
    
    delete: async (id: string) => {
      if (USE_MOCK) {
        return mockApi.files.delete(id);
      }
      return apiClient.delete(`/files/${id}`);
    },
    
    getPreview: async (id: string) => {
      if (USE_MOCK) {
        return { success: true, data: { content: 'Mock file preview content' } };
      }
      return apiClient.get(`/files/${id}/preview`);
    },
  },
  
  // 用户管理API
  user: {
    updateProfile: async (data: Partial<User>) => {
      if (USE_MOCK) {
        return { success: true, data: { ...mockApi.auth.me(), ...data } };
      }
      return apiClient.put<User>('/users/profile', data);
    },
    
    getUsageStats: async () => {
      if (USE_MOCK) {
        return {
          success: true,
          data: {
            messages_sent: 45,
            files_uploaded: 12,
            credits_used: 150,
            credits_remaining: 850,
          }
        };
      }
      return apiClient.get('/users/usage');
    },
  },
  
  // 订阅管理API
  subscription: {
    getPlans: async () => {
      if (USE_MOCK) {
        return {
          success: true,
          data: [
            { id: 'free', name: 'Free', price: 0, credits: 100 },
            { id: 'pro', name: 'Pro', price: 29, credits: 1000 },
            { id: 'enterprise', name: 'Enterprise', price: 99, credits: 5000 },
          ]
        };
      }
      return apiClient.get('/subscription/plans');
    },
    
    create: async (planId: string) => {
      if (USE_MOCK) {
        return { success: true, data: { subscription_id: `sub_${Date.now()}` } };
      }
      return apiClient.post('/subscription/create', { plan_id: planId });
    },
    
    cancel: async () => {
      if (USE_MOCK) {
        return { success: true };
      }
      return apiClient.post('/subscription/cancel');
    },
  },
};

export default apiService;