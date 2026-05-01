import { create } from 'zustand';

interface SessionState {
  currentSessionId: string | null;
  capturedImageUri: string | null;
  setCurrentSession: (id: string) => void;
  setCapturedImageUri: (uri: string) => void;
  clearSession: () => void;
}

export const useSessionStore = create<SessionState>((set) => ({
  currentSessionId: null,
  capturedImageUri: null,
  setCurrentSession: (id) => set({ currentSessionId: id }),
  setCapturedImageUri: (uri) => set({ capturedImageUri: uri }),
  clearSession: () => set({ currentSessionId: null, capturedImageUri: null }),
}));
