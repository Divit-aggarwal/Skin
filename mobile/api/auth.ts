import { apiClient } from './client';

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  user: { id: string; email: string };
}

export const authApi = {
  register: (email: string, password: string, displayName?: string) =>
    apiClient.post<AuthResponse>('/auth/register', { email, password, display_name: displayName }),

  login: (email: string, password: string) =>
    apiClient.post<AuthResponse>('/auth/login', { email, password }),

  refresh: (refreshToken: string) =>
    apiClient.post<AuthResponse>('/auth/refresh', { refresh_token: refreshToken }),

  logout: (refreshToken: string) =>
    apiClient.post('/auth/logout', { refresh_token: refreshToken }),
};
