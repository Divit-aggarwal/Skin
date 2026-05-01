import { create } from 'zustand';
import { saveTokens, getTokens, clearTokens as clearStoredTokens } from '../utils/storage';

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  userId: string | null;
  setTokens: (accessToken: string, refreshToken: string, userId: string) => void;
  clearTokens: () => void;
  hydrate: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: null,
  refreshToken: null,
  isAuthenticated: false,
  userId: null,

  setTokens: (accessToken, refreshToken, userId) => {
    saveTokens(accessToken, refreshToken);
    set({ accessToken, refreshToken, userId, isAuthenticated: true });
  },

  clearTokens: () => {
    clearStoredTokens();
    set({ accessToken: null, refreshToken: null, userId: null, isAuthenticated: false });
  },

  hydrate: async () => {
    const { accessToken, refreshToken } = await getTokens();
    if (accessToken && refreshToken) {
      set({ accessToken, refreshToken, isAuthenticated: true });
    }
  },
}));
