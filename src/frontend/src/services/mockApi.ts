import type { User, Session, Message, Buyer, Supplier, FileInfo } from '../types';

// 模拟延迟
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// Mock用户数据
const mockUser: User = {
  id: 'user_12345',
  email: 'demo@tradeflow.com',
  name: 'Demo User',
  avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=demo',
  company: 'TradeFlow Demo Co.',
  verified: true,
  subscription: {
    id: 'sub_12345',
    plan: 'pro',
    status: 'active',
    credits_used: 150,
    credits_limit: 1000,
    expires_at: '2025-12-31T23:59:59Z',
  },
  permissions: [
    'trade:read',
    'trade:write',
    'contacts:read',
    'contacts:write',
    'documents:read',
    'reports:read',
    'analytics:read',
  ],
};

// Mock会话数据
const mockSessions: Session[] = [
  {
    id: 'session_1',
    title: '寻找电子产品买家',
    created_at: '2025-01-08T10:00:00Z',
    updated_at: '2025-01-08T15:30:00Z',
    message_count: 8,
    last_message_preview: '根据您的需求，我为您找到了5个潜在的电子产品买家...',
  },
  {
    id: 'session_2',
    title: '供应商质量评估',
    created_at: '2025-01-07T14:20:00Z',
    updated_at: '2025-01-07T16:45:00Z',
    message_count: 12,
    last_message_preview: '这家供应商的综合评分为8.5分，主要优势在于...',
  },
  {
    id: 'session_3',
    title: '市场价格分析',
    created_at: '2025-01-06T09:15:00Z',
    updated_at: '2025-01-06T11:20:00Z',
    message_count: 6,
    last_message_preview: '当前市场价格趋势显示...',
  },
];

// Mock消息数据
const mockMessages: Message[] = [
  {
    id: 'msg_1',
    content: '我想找一些电子产品的买家，主要是手机和平板电脑',
    role: 'user',
    timestamp: '2025-01-08T10:00:00Z',
    session_id: 'session_1',
  },
  {
    id: 'msg_2',
    content: '好的，我来为您分析电子产品买家市场。根据最新的贸易数据，我为您找到了几个高潜力的买家：\n\n## 推荐买家列表\n\n### 1. TechGlobal Solutions (美国)\n- **主营业务**: 消费电子产品分销\n- **年采购量**: 5000万美元\n- **重点产品**: 智能手机、平板电脑、可穿戴设备\n- **匹配度**: ⭐⭐⭐⭐⭐\n\n### 2. EuroElectronics Ltd (德国)\n- **主营业务**: 电子产品零售连锁\n- **年采购量**: 3200万欧元\n- **重点产品**: 手机配件、平板电脑\n- **匹配度**: ⭐⭐⭐⭐\n\n需要我为您生成具体的联系方案吗？',
    role: 'assistant',
    timestamp: '2025-01-08T10:01:30Z',
    session_id: 'session_1',
  },
];

// Mock买家数据
const mockBuyers: Buyer[] = [
  {
    id: 'buyer_1',
    company_name: 'TechGlobal Solutions',
    contact_person: 'John Smith',
    country: 'United States',
    industry: 'Consumer Electronics',
    products_interested: ['Smartphones', 'Tablets', 'Wearables'],
    contact_info: {
      email: 'john.smith@techglobal.com',
      phone: '+1-555-0123',
      website: 'https://techglobal.com',
    },
    priority: 'high',
    match_score: 95,
  },
  {
    id: 'buyer_2',
    company_name: 'EuroElectronics Ltd',
    contact_person: 'Marie Dubois',
    country: 'Germany',
    industry: 'Electronics Retail',
    products_interested: ['Mobile Accessories', 'Tablets'],
    contact_info: {
      email: 'marie@euroelectronics.de',
      website: 'https://euroelectronics.de',
    },
    priority: 'medium',
    match_score: 87,
  },
];

// Mock供应商数据
const mockSuppliers: Supplier[] = [
  {
    id: 'supplier_1',
    company_name: '深圳科技制造有限公司',
    country: 'China',
    products: ['Smartphones', 'Tablets', 'Electronics Components'],
    certifications: ['ISO9001', 'CE', 'FCC', 'RoHS'],
    contact_info: {
      email: 'sales@sztech.com',
      phone: '+86-755-8888-9999',
      website: 'https://sztech.com',
    },
    rating: 4.8,
    verified: true,
  },
];

// Mock文件数据
const mockFiles: FileInfo[] = [
  {
    id: 'file_1',
    name: 'product_catalog.pdf',
    size: 2048576, // 2MB
    type: 'application/pdf',
    url: '/api/files/file_1/download',
    preview_url: '/api/files/file_1/preview',
    created_at: '2025-01-08T10:00:00Z',
  },
  {
    id: 'file_2',
    name: 'market_analysis.xlsx',
    size: 1024000, // 1MB
    type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    url: '/api/files/file_2/download',
    created_at: '2025-01-07T14:30:00Z',
  },
];

// Mock API服务
export const mockApi = {
  // 认证相关
  auth: {
    login: async (_provider: string) => {
      await delay(1000);
      return {
        success: true,
        data: {
          user: mockUser,
          token: `mock_token_${Date.now()}`,
          refreshToken: `mock_refresh_${Date.now()}`,
        },
      };
    },
    
    refresh: async (_refreshToken: string) => {
      await delay(500);
      return {
        success: true,
        data: {
          token: `new_token_${Date.now()}`,
          refreshToken: `new_refresh_${Date.now()}`,
        },
      };
    },
    
    me: async () => {
      await delay(300);
      return {
        success: true,
        data: mockUser,
      };
    },
  },
  
  // 会话管理
  sessions: {
    list: async () => {
      await delay(500);
      return {
        success: true,
        data: mockSessions,
      };
    },
    
    create: async (title?: string) => {
      await delay(300);
      const newSession: Session = {
        id: `session_${Date.now()}`,
        title: title || '新对话',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        message_count: 0,
      };
      return {
        success: true,
        data: newSession,
      };
    },
    
    delete: async (id: string) => {
      await delay(200);
      return {
        success: true,
        data: { id },
      };
    },
  },
  
  // 消息管理
  messages: {
    list: async (sessionId: string) => {
      await delay(300);
      const sessionMessages = mockMessages.filter(msg => msg.session_id === sessionId);
      return {
        success: true,
        data: sessionMessages,
      };
    },
    
    send: async (content: string, sessionId: string) => {
      await delay(800);
      const userMessage: Message = {
        id: `msg_${Date.now()}`,
        content,
        role: 'user',
        timestamp: new Date().toISOString(),
        session_id: sessionId,
      };
      
      // 模拟AI回复
      const aiMessage: Message = {
        id: `msg_${Date.now() + 1}`,
        content: '这是一个模拟的AI回复。在实际环境中，这里会显示真实的AI分析结果。',
        role: 'assistant',
        timestamp: new Date().toISOString(),
        session_id: sessionId,
      };
      
      return {
        success: true,
        data: [userMessage, aiMessage],
      };
    },
  },
  
  // 买家推荐
  buyers: {
    recommend: async (_query: string) => {
      await delay(1500);
      return {
        success: true,
        data: mockBuyers,
      };
    },
    
    detail: async (id: string) => {
      await delay(300);
      const buyer = mockBuyers.find(b => b.id === id);
      return {
        success: true,
        data: buyer,
      };
    },
  },
  
  // 供应商搜索
  suppliers: {
    search: async (_query: string) => {
      await delay(1200);
      return {
        success: true,
        data: mockSuppliers,
      };
    },
    
    detail: async (id: string) => {
      await delay(300);
      const supplier = mockSuppliers.find(s => s.id === id);
      return {
        success: true,
        data: supplier,
      };
    },
  },
  
  // 文件管理
  files: {
    upload: async (file: File) => {
      await delay(2000);
      const mockFile: FileInfo = {
        id: `file_${Date.now()}`,
        name: file.name,
        size: file.size,
        type: file.type,
        url: `/api/files/file_${Date.now()}/download`,
        created_at: new Date().toISOString(),
      };
      return {
        success: true,
        data: mockFile,
      };
    },
    
    list: async () => {
      await delay(300);
      return {
        success: true,
        data: mockFiles,
      };
    },
    
    delete: async (id: string) => {
      await delay(200);
      return {
        success: true,
        data: { id },
      };
    },
  },
};