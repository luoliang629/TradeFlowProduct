// 用户相关类型
export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  company?: string;
  verified: boolean;
  subscription?: Subscription;
  permissions?: string[]; // 用户权限列表
}

// 订阅相关类型
export interface Subscription {
  id: string;
  plan: 'free' | 'basic' | 'pro' | 'enterprise';
  status: 'active' | 'canceled' | 'expired';
  credits_used: number;
  credits_limit: number;
  expires_at: string;
}

// API响应类型
export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
  };
}

// 消息相关类型
export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: string;
  files?: FileInfo[];
  session_id: string;
}

// 会话类型
export interface Session {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
  last_message_preview?: string;
}

// 文件相关类型
export interface FileInfo {
  id: string;
  name: string;
  size: number;
  type: string;
  url: string;
  preview_url?: string;
  created_at: string;
}

// 文件附件类型
export interface FileAttachment {
  id?: string;
  name: string;
  size?: number;
  type?: string;
  url?: string;
  preview_url?: string;
  content?: string;
  created_at?: string;
}

// 业务相关类型
export interface Buyer {
  id: string;
  company_name: string;
  contact_person: string;
  position?: string;
  country: string;
  country_code?: string;
  city?: string;
  industry: string;
  company_size: string;
  annual_volume: string;
  credit_rating: number;
  certifications: string[];
  logo_url?: string;
  products_interested: string[];
  contact_info: {
    email?: string;
    phone?: string;
    website?: string;
  };
  priority: 'high' | 'medium' | 'low';
  match_score: number;
}

export interface Supplier {
  id: string;
  company_name: string;
  contact_person: string;
  position?: string;
  country: string;
  country_code?: string;
  city?: string;
  main_products: string[];
  established_year: number;
  employee_count: string;
  min_order: string;
  rating: number;
  review_count: number;
  level: 'gold' | 'silver' | 'bronze' | 'verified';
  certifications: string[];
  logo_url?: string;
  contact_info: {
    email?: string;
    phone?: string;
    website?: string;
  };
  trade_capacity: {
    export_percentage: number;
    main_markets: string[];
    annual_sales: string;
  };
  verified: boolean;
}

// 应用状态类型
export interface AppState {
  user: User | null;
  sessions: Session[];
  currentSession: Session | null;
  messages: Message[];
  loading: boolean;
  error: string | null;
}

// 主题类型
export type Theme = 'light' | 'dark';

// 语言类型
export type Language = 'zh' | 'en';