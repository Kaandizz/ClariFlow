import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
import { 
  User, 
  AuthState, 
  LoginRequest, 
  RegisterRequest,
  login as authLogin,
  register as authRegister,
  logout as authLogout,
  getCurrentUser,
  updateProfile,
  changePassword,
  getAuthState,
  verifyEmail,
  resendVerificationEmail
} from '@/lib/auth';

interface AuthStore extends AuthState {
  // Actions
  login: (credentials: LoginRequest) => Promise<void>;
  register: (userData: RegisterRequest) => Promise<void>;
  logout: () => void;
  fetchCurrentUser: () => Promise<void>;
  updateUserProfile: (updates: Partial<User>) => Promise<void>;
  changeUserPassword: (currentPassword: string, newPassword: string) => Promise<void>;
  verifyUserEmail: (token: string) => Promise<void>;
  resendUserVerificationEmail: (email: string) => Promise<void>;
  
  // State setters
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
  
  // Utility
  initialize: () => void;
  isAuthenticated: boolean;
}

const initialState: AuthState = {
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
};

export const useAuthStore = create<AuthStore>()(
  subscribeWithSelector((set, get) => ({
    ...initialState,

    login: async (credentials: LoginRequest) => {
      set({ isLoading: true, error: null });
      try {
        const response = await authLogin(credentials);
        set({
          user: response.user,
          isAuthenticated: true,
          isLoading: false,
          error: null,
        });
      } catch (error: any) {
        set({
          isLoading: false,
          error: error.response?.data?.detail || error.message || 'Login failed',
        });
        throw error;
      }
    },

    register: async (userData: RegisterRequest) => {
      set({ isLoading: true, error: null });
      try {
        const response = await authRegister(userData);
        set({
          user: response.user,
          isAuthenticated: true,
          isLoading: false,
          error: null,
        });
      } catch (error: any) {
        set({
          isLoading: false,
          error: error.response?.data?.detail || error.message || 'Registration failed',
        });
        throw error;
      }
    },

    logout: async () => {
      try {
        await authLogout();
      } catch (error) {
        console.error('Error during logout:', error);
      } finally {
        set(initialState);
      }
    },

    fetchCurrentUser: async () => {
      set({ isLoading: true, error: null });
      try {
        const user = await getCurrentUser();
        set({
          user,
          isAuthenticated: true,
          isLoading: false,
          error: null,
        });
      } catch (error: any) {
        set({
          user: null,
          isAuthenticated: false,
          isLoading: false,
          error: error.response?.data?.detail || error.message || 'Failed to fetch user',
        });
        // If token is invalid, logout
        if (error.response?.status === 401) {
          get().logout();
        }
      }
    },

    updateUserProfile: async (updates: Partial<User>) => {
      set({ isLoading: true, error: null });
      try {
        const user = await updateProfile(updates);
        set({
          user,
          isLoading: false,
          error: null,
        });
      } catch (error: any) {
        set({
          isLoading: false,
          error: error.response?.data?.detail || error.message || 'Failed to update profile',
        });
        throw error;
      }
    },

    changeUserPassword: async (currentPassword: string, newPassword: string) => {
      set({ isLoading: true, error: null });
      try {
        await changePassword(currentPassword, newPassword);
        set({
          isLoading: false,
          error: null,
        });
      } catch (error: any) {
        set({
          isLoading: false,
          error: error.response?.data?.detail || error.message || 'Failed to change password',
        });
        throw error;
      }
    },

    verifyUserEmail: async (token: string) => {
      set({ isLoading: true, error: null });
      try {
        await verifyEmail(token);
        set({
          isLoading: false,
          error: null,
        });
        // Refresh user data to get updated verification status
        await get().fetchCurrentUser();
      } catch (error: any) {
        set({
          isLoading: false,
          error: error.response?.data?.detail || error.message || 'Failed to verify email',
        });
        throw error;
      }
    },

    resendUserVerificationEmail: async (email: string) => {
      set({ isLoading: true, error: null });
      try {
        await resendVerificationEmail(email);
        set({
          isLoading: false,
          error: null,
        });
      } catch (error: any) {
        set({
          isLoading: false,
          error: error.response?.data?.detail || error.message || 'Failed to resend verification email',
        });
        throw error;
      }
    },

    setLoading: (loading: boolean) => set({ isLoading: loading }),
    setError: (error: string | null) => set({ error }),
    clearError: () => set({ error: null }),

    initialize: async () => {
      try {
        // Try to fetch current user to check if authenticated
        await get().fetchCurrentUser();
      } catch (error) {
        // User not authenticated, keep initial state
        set(initialState);
      }
    },
  }))
);

// Subscribe to auth state changes and persist to localStorage
if (typeof window !== 'undefined') {
  useAuthStore.subscribe(
    (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
    (state) => {
      if (state.user) {
        localStorage.setItem('clariflow_user', JSON.stringify(state.user));
      } else {
        localStorage.removeItem('clariflow_user');
      }
    }
  );
} 