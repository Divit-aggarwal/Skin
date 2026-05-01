import { apiClient } from './client';

export type SkinType = 'normal' | 'oily' | 'dry' | 'combination' | 'sensitive';

export interface UserMe {
  id: string;
  email: string;
  created_at: string;
}

export interface UserProfile {
  id: string;
  user_id: string;
  display_name: string | null;
  age: number | null;
  gender: string | null;
  skin_type: SkinType | null;
  created_at: string;
  updated_at: string;
}

export interface UpdateProfileData {
  display_name?: string;
  age?: number;
  gender?: string;
  skin_type?: SkinType;
}

export const usersApi = {
  getMe: () => apiClient.get<UserMe>('/users/me'),
  getProfile: () => apiClient.get<UserProfile>('/users/me/profile'),
  updateProfile: (data: UpdateProfileData) =>
    apiClient.put<UserProfile>('/users/me/profile', data),
  deleteAccount: (password: string) =>
    apiClient.delete('/users/me', { data: { password } }),
};
