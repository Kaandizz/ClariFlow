import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import { jwtDecode } from 'jwt-decode';

// Types
export interface User {
  id: string;
  email: string;
  full_name?: string;
  is_active: boolean;
  is_superuser: boolean;
  is_email_verified: boolean;
  created_at: string;
  updated_at?: string;
}

export interface LoginRequest {
  username: string; // email
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  confirm_password: string;
  full_name?: string;
}

export interface LoginResponse {
  user: User;
  message?: string;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface DecodedToken {
  sub: string;
  user_id: number;
  is_superuser: boolean;
  exp: number;
  type: string;
}

// Constants
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create authenticated API instance
export const createAuthApi = (): AxiosInstance => {
  const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
      'Content-Type': 'application/json',
    },
    withCredentials: true, // Important for cookies
  });

  // Request interceptor to add auth token (for backward compatibility)
  api.interceptors.request.use(
    (config) => {
      // Cookies are automatically sent with requests when withCredentials is true
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  // Response interceptor to handle auth errors
  api.interceptors.response.use(
    (response: AxiosResponse) => response,
    async (error: AxiosError) => {
      const originalRequest = error.config as any;

      if (error.response?.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true;

        try {
          // Try to refresh token
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {}, {
            withCredentials: true
          });

          // Retry the original request
          return api(originalRequest);
        } catch (refreshError) {
          // Refresh failed, redirect to login
          if (typeof window !== 'undefined') {
            window.location.href = '/login';
          }
          return Promise.reject(refreshError);
        }
      }

      return Promise.reject(error);
    }
  );

  return api;
};

// Auth API functions
export const authApi = createAuthApi();

export const login = async (credentials: LoginRequest): Promise<LoginResponse> => {
  const formData = new FormData();
  formData.append('username', credentials.username);
  formData.append('password', credentials.password);
  
  const response = await authApi.post('/auth/login', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });
  
  return response.data;
};

export const register = async (userData: RegisterRequest): Promise<LoginResponse> => {
  const response = await authApi.post('/auth/register', {
    email: userData.email,
    password: userData.password,
    full_name: userData.full_name,
  });
  
  return response.data;
};

export const logout = async (): Promise<void> => {
  await authApi.post('/auth/logout');
};

export const refreshToken = async (): Promise<void> => {
  await authApi.post('/auth/refresh');
};

export const getCurrentUser = async (): Promise<User> => {
  const response = await authApi.get('/auth/me');
  return response.data;
};

export const updateProfile = async (updates: Partial<User>): Promise<User> => {
  const response = await authApi.put('/auth/me', updates);
  return response.data;
};

export const changePassword = async (currentPassword: string, newPassword: string): Promise<void> => {
  await authApi.post('/auth/change-password', {
    current_password: currentPassword,
    new_password: newPassword,
  });
};

export const verifyEmail = async (token: string): Promise<{ message: string }> => {
  const response = await authApi.post('/auth/verify-email', { token });
  return response.data;
};

export const resendVerificationEmail = async (email: string): Promise<{ message: string }> => {
  const response = await authApi.post('/auth/resend-verification', { email });
  return response.data;
};

export const requestPasswordReset = async (email: string): Promise<{ message: string }> => {
  const response = await authApi.post('/auth/request-password-reset', { email });
  return response.data;
};

export const resetPassword = async (token: string, newPassword: string): Promise<{ message: string }> => {
  const response = await authApi.post('/auth/reset-password', { token, new_password: newPassword });
  return response.data;
};

// Auth state management
export const getAuthState = (): AuthState => {
  return {
    user: null,
    isAuthenticated: false,
    isLoading: false,
    error: null,
  };
};

// Utility functions
export const hasPermission = (permission: string): boolean => {
  const user = null; // No user object in new auth, so no permission check
  return false;
};

export const isAdmin = (): boolean => {
  const user = null; // No user object in new auth, so no permission check
  return false;
}; 