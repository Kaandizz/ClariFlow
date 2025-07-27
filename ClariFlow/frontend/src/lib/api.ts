import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Important for cookies
});

// Request interceptor - cookies are automatically sent
api.interceptors.request.use(
  (config) => {
    // Cookies are automatically sent with requests when withCredentials is true
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle 401 errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // Handle 401 errors (unauthorized)
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      // Redirect to login page
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

// Types
export interface SearchRequest {
  query: string;
  file_id?: string;
  top_k?: number;
}

export interface SearchResult {
  content: string;
  metadata: {
    source: string;
    chunk_index: number;
    document_id: string;
    filename: string;
  };
  score: number;
}

export interface SearchResponse {
  results: SearchResult[];
  total_results: number;
  query: string;
}

export interface DocumentsResponse {
  documents: Array<{
    id: string;
    filename: string;
    upload_date: string;
    status: string;
  }>;
}

export interface ChatRequest {
  query: string;
  session_id?: string;
  history?: string[];
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  document_id?: string;
  source?: 'document' | 'openai';
}

export interface ChatMessageResponse {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  document_id?: string;
  source?: 'document' | 'openai';
}

export interface ChatSession {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface CreateSessionRequest {
  title?: string;
}

export interface UpdateSessionRequest {
  title?: string;
}

export interface ChatResponse {
  response: string;
  source: 'document' | 'openai';
  sources?: string[] | null;
  document_id?: string | null;
  timestamp: string;
  session_id?: string;
  used_context?: boolean;
  matched_chunks?: string[] | null;
  relevance_score?: number | null;
}

export interface InsightQuery {
  question: string;
  data_source: string;
  data_source_type: 'csv' | 'excel';
}

export interface InsightResponse {
  insight: string;
  confidence_score: number;
  data_summary: string;
  recommendations: string[];
  visualization_data?: any;
  analysis_type: string;
  data_source: string;
  timestamp: string;
}

export interface TaskParseRequest {
  transcript: string;
  context?: string;
}

export interface ExtractedTask {
  id: string;
  title: string;
  assignee?: string;
  due_date?: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  category: 'meeting' | 'follow_up' | 'research' | 'presentation' | 'analysis' | 'communication';
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled';
  notes?: string;
  confidence_score: number;
  extracted_from: string;
  created_at: string;
}

export interface TaskParseResponse {
  tasks: ExtractedTask[];
  total_tasks: number;
  parsing_confidence: number;
  processing_time: number;
  summary?: string;
}

export interface TaskFilter {
  assignee?: string;
  status?: 'pending' | 'in_progress' | 'completed' | 'cancelled';
  priority?: 'low' | 'medium' | 'high' | 'urgent';
  category?: 'meeting' | 'follow_up' | 'research' | 'presentation' | 'analysis' | 'communication';
  due_date_from?: string;
  due_date_to?: string;
  search_term?: string;
}

export interface TaskListResponse {
  tasks: ExtractedTask[];
  total_count: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface AgentRequest {
  agent_name: string;
  input_data: any;
  parameters?: Record<string, any>;
  context?: Record<string, any>;
}

export interface AgentResponse {
  success: boolean;
  result: any;
  metadata: Record<string, any>;
  execution_time: number;
  error_message?: string;
}

// API Functions
export const createChatSession = async (request: CreateSessionRequest = {}): Promise<ChatSession> => {
  const response = await api.post<ChatSession>('/api/sessions', request);
  return response.data;
};

export const getChatSessions = async (): Promise<ChatSession[]> => {
  const response = await api.get<ChatSession[]>('/api/sessions');
  return response.data;
};

export const updateChatSession = async (sessionId: string, request: UpdateSessionRequest): Promise<ChatSession> => {
  const response = await api.put<ChatSession>(`/api/sessions/${sessionId}`, request);
  return response.data;
};

export const deleteChatSession = async (sessionId: string): Promise<void> => {
  await api.delete(`/api/sessions/${sessionId}`);
};

export const getChatMessages = async (sessionId: string): Promise<ChatMessageResponse[]> => {
  const response = await api.get<ChatMessageResponse[]>(`/api/sessions/${sessionId}/messages`);
  return response.data;
};

export const sendChatMessage = async (request: ChatRequest): Promise<ChatResponse> => {
  const response = await api.post<ChatResponse>('/api/chat', request);
  return response.data;
};

export const searchDocuments = async (request: SearchRequest): Promise<SearchResponse> => {
  const response = await api.post<SearchResponse>('/api/search', request);
  return response.data;
};

export const getAvailableDocuments = async (): Promise<DocumentsResponse> => {
  const response = await api.get<DocumentsResponse>('/api/documents');
  return response.data;
};

// Phase 8 - Business Insights API Functions
export const generateInsight = async (request: InsightQuery): Promise<InsightResponse> => {
  const response = await api.post('/insights/query', request);
  return response.data;
};

export const getDataSources = async (): Promise<any> => {
  const response = await api.get('/insights/data-sources');
  return response.data;
};

export const uploadDataSource = async (file: File): Promise<any> => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/insights/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const performAdvancedAnalysis = async (
  dataSource: string, 
  dataSourceType: 'csv' | 'excel',
  analysisType: 'regression' | 'clustering' | 'forecasting'
): Promise<any> => {
  const response = await api.post('/insights/advanced-analysis', {
    data_source: dataSource,
    data_source_type: dataSourceType,
    analysis_type: analysisType
  });
  return response.data;
};

// Task Management API Functions
export const parseTasks = async (request: TaskParseRequest): Promise<TaskParseResponse> => {
  const response = await api.post('/tasks/parse', request);
  return response.data;
};

export const getTasks = async (
  page: number = 1,
  per_page: number = 20,
  filters?: TaskFilter
): Promise<TaskListResponse> => {
  const params = new URLSearchParams({
    page: page.toString(),
    per_page: per_page.toString(),
    ...(filters && Object.fromEntries(
      Object.entries(filters).filter(([_, value]) => value !== undefined)
    ))
  });
  
  const response = await api.get<TaskListResponse>(`/api/tasks?${params}`);
  return response.data;
};

export const updateTask = async (taskId: string, updates: Partial<ExtractedTask>): Promise<ExtractedTask> => {
  const response = await api.put<ExtractedTask>(`/api/tasks/${taskId}`, updates);
  return response.data;
};

export const deleteTask = async (taskId: string): Promise<void> => {
  await api.delete(`/api/tasks/${taskId}`);
};

// Agent API Functions
export const callAgent = async (request: AgentRequest): Promise<AgentResponse> => {
  const response = await api.post('/agents/call', request);
  return response.data;
};

export const callAgentChain = async (requests: AgentRequest[]): Promise<AgentResponse[]> => {
  const response = await api.post('/agents/chain', requests);
  return response.data;
}; 