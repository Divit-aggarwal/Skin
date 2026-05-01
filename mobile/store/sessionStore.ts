import { create } from 'zustand';

interface SessionState {
  currentSessionId: string | null;
  setCurrentSession: (id: string) => void;
  clearSession: () => void;
}

export const useSessionStore = create<SessionState>((set) => ({
  currentSessionId: null,
  setCurrentSession: (id) => set({ currentSessionId: id }),
  clearSession: () => set({ currentSessionId: null }),
}));
