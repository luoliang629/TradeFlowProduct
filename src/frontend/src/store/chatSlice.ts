import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';
import type { Message, Session } from '../types';

interface ChatState {
  sessions: Session[];
  currentSession: Session | null;
  messages: Message[];
  isSSEConnected: boolean;
  isTyping: boolean;
  loading: boolean;
  error: string | null;
}

const initialState: ChatState = {
  sessions: [],
  currentSession: null,
  messages: [],
  isSSEConnected: false,
  isTyping: false,
  loading: false,
  error: null,
};

// 异步thunks
export const fetchSessions = createAsyncThunk(
  'chat/fetchSessions',
  async (_, { rejectWithValue }) => {
    try {
      // API调用获取会话列表
      return [];
    } catch (error) {
      return rejectWithValue('获取会话列表失败');
    }
  }
);

export const createNewSession = createAsyncThunk(
  'chat/createNewSession',
  async (title: string | undefined, { rejectWithValue }) => {
    try {
      const newSession: Session = {
        id: `session_${Date.now()}`,
        title: title || '新对话',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        message_count: 0,
      };
      return newSession;
    } catch (error) {
      return rejectWithValue('创建会话失败');
    }
  }
);

export const sendMessage = createAsyncThunk(
  'chat/sendMessage',
  async (
    { content, sessionId }: { content: string; sessionId: string },
    { rejectWithValue }
  ) => {
    try {
      const userMessage: Message = {
        id: `msg_${Date.now()}`,
        content,
        role: 'user',
        timestamp: new Date().toISOString(),
        session_id: sessionId,
      };
      return userMessage;
    } catch (error) {
      return rejectWithValue('发送消息失败');
    }
  }
);

const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    setCurrentSession: (state, action: PayloadAction<Session | null>) => {
      state.currentSession = action.payload;
      if (action.payload) {
        // 加载该会话的消息
        state.messages = [];
      }
    },
    addMessage: (state, action: PayloadAction<Message>) => {
      state.messages.push(action.payload);
    },
    updateLastMessage: (state, action: PayloadAction<string>) => {
      const lastMessage = state.messages[state.messages.length - 1];
      if (lastMessage && lastMessage.role === 'assistant') {
        lastMessage.content = action.payload;
      }
    },
    setSSEConnectionStatus: (state, action: PayloadAction<boolean>) => {
      state.isSSEConnected = action.payload;
    },
    setTypingStatus: (state, action: PayloadAction<boolean>) => {
      state.isTyping = action.payload;
    },
    clearMessages: state => {
      state.messages = [];
    },
    clearError: state => {
      state.error = null;
    },
    deleteSession: (state, action: PayloadAction<string>) => {
      state.sessions = state.sessions.filter(s => s.id !== action.payload);
      if (state.currentSession?.id === action.payload) {
        state.currentSession = null;
        state.messages = [];
      }
    },
  },
  extraReducers: builder => {
    builder
      // 获取会话列表
      .addCase(fetchSessions.pending, state => {
        state.loading = true;
      })
      .addCase(fetchSessions.fulfilled, (state, action) => {
        state.loading = false;
        state.sessions = action.payload;
      })
      .addCase(fetchSessions.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // 创建新会话
      .addCase(createNewSession.fulfilled, (state, action) => {
        state.sessions.unshift(action.payload);
        state.currentSession = action.payload;
        state.messages = [];
      })
      // 发送消息
      .addCase(sendMessage.fulfilled, (state, action) => {
        state.messages.push(action.payload);
        // 更新会话的最后消息预览
        if (state.currentSession) {
          const sessionIndex = state.sessions.findIndex(
            s => s.id === state.currentSession!.id
          );
          if (sessionIndex >= 0) {
            state.sessions[sessionIndex].last_message_preview =
              action.payload.content;
            state.sessions[sessionIndex].updated_at = action.payload.timestamp;
            state.sessions[sessionIndex].message_count++;
          }
        }
      });
  },
});

export const {
  setCurrentSession,
  addMessage,
  updateLastMessage,
  setSSEConnectionStatus,
  setTypingStatus,
  clearMessages,
  clearError,
  deleteSession,
} = chatSlice.actions;

export default chatSlice.reducer;