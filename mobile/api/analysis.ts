import { apiClient } from './client';
import type { SessionOut, HistoryResponse } from './types';

export const analysisApi = {
  createSession: (imageId: string, imageData: string) =>
    apiClient.post<SessionOut>('/analysis/sessions', {
      image_id: imageId,
      image_data: imageData,
    }),

  getSession: (sessionId: string) =>
    apiClient.get<SessionOut>(`/analysis/sessions/${sessionId}`),

  getHistory: (page: number, pageSize: number) =>
    apiClient.get<HistoryResponse>(`/analysis/history?page=${page}&page_size=${pageSize}`),
};
