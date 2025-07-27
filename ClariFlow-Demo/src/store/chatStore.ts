import { create } from 'zustand';
import { ChatSession, ChatMessage, ChatMessageResponse } from '@/lib/api';

interface ChatState {
  // Sessions
  sessions: ChatSession[];
  activeSessionId: string | null;
  isLoadingSessions: boolean;
  
  // Messages
  messages: ChatMessage[];
  isLoadingMessages: boolean;
  
  // UI State
  isCreatingSession: boolean;
  isDeletingSession: boolean;
  isUpdatingTitle: boolean;
  
  // Actions
  setSessions: (sessions: ChatSession[]) => void;
  setActiveSession: (sessionId: string | null) => void;
  setMessages: (messages: ChatMessage[]) => void;
  addMessage: (message: ChatMessage) => void;
  clearMessages: () => void;
  
  // Loading states
  setLoadingSessions: (loading: boolean) => void;
  setLoadingMessages: (loading: boolean) => void;
  setCreatingSession: (loading: boolean) => void;
  setDeletingSession: (loading: boolean) => void;
  setUpdatingTitle: (loading: boolean) => void;
  
  // Session management
  addSession: (session: ChatSession) => void;
  updateSession: (sessionId: string, updates: Partial<ChatSession>) => void;
  removeSession: (sessionId: string) => void;
  
  // Reset
  reset: () => void;
}

const initialState = {
  sessions: [],
  activeSessionId: null,
  isLoadingSessions: false,
  messages: [],
  isLoadingMessages: false,
  isCreatingSession: false,
  isDeletingSession: false,
  isUpdatingTitle: false,
};

export const useChatStore = create<ChatState>((set, get) => ({
  ...initialState,
  
  setSessions: (sessions) => set({ sessions }),
  setActiveSession: (sessionId) => set({ activeSessionId: sessionId }),
  setMessages: (messages) => set({ messages }),
  addMessage: (message) => set((state) => ({ 
    messages: [...state.messages, message] 
  })),
  clearMessages: () => set({ messages: [] }),
  
  setLoadingSessions: (loading) => set({ isLoadingSessions: loading }),
  setLoadingMessages: (loading) => set({ isLoadingMessages: loading }),
  setCreatingSession: (loading) => set({ isCreatingSession: loading }),
  setDeletingSession: (loading) => set({ isDeletingSession: loading }),
  setUpdatingTitle: (loading) => set({ isUpdatingTitle: loading }),
  
  addSession: (session) => set((state) => ({ 
    sessions: [session, ...state.sessions] 
  })),
  
  updateSession: (sessionId, updates) => set((state) => ({
    sessions: state.sessions.map(session => 
      session.id === sessionId ? { ...session, ...updates } : session
    )
  })),
  
  removeSession: (sessionId) => set((state) => ({
    sessions: state.sessions.filter(session => session.id !== sessionId),
    activeSessionId: state.activeSessionId === sessionId ? null : state.activeSessionId
  })),
  
  reset: () => set(initialState),
}));

// Helper function to convert ChatMessageResponse to ChatMessage
export const convertMessageResponse = (message: ChatMessageResponse): ChatMessage => ({
  role: message.role,
  content: message.content,
  timestamp: message.timestamp,
  document_id: message.document_id,
  source: message.source,
}); 