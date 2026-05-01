import { create } from 'zustand';
import { SkinType } from '../api/users';

interface UserData {
  id: string;
  email: string;
}

interface ProfileData {
  display_name: string | null;
  age: number | null;
  gender: string | null;
  skin_type: SkinType | null;
}

interface UserState {
  user: UserData | null;
  profile: ProfileData | null;
  profileSetupSeen: boolean;
  setUser: (user: UserData) => void;
  setProfile: (profile: ProfileData) => void;
  markProfileSetupSeen: () => void;
  clearUser: () => void;
}

export const useUserStore = create<UserState>((set) => ({
  user: null,
  profile: null,
  profileSetupSeen: false,
  setUser: (user) => set({ user }),
  setProfile: (profile) => set({ profile }),
  markProfileSetupSeen: () => set({ profileSetupSeen: true }),
  clearUser: () => set({ user: null, profile: null, profileSetupSeen: false }),
}));
