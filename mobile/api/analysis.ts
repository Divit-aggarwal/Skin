import { apiClient } from './client';

export type SeverityLevel = 'mild' | 'moderate' | 'severe';

export interface AnalysisReport {
  overall_score: number;
  acne_score: number;
  wrinkle_score: number;
  oiliness_score: number;
  severity_level: SeverityLevel;
}

export interface HistoryItem {
  id: string;
  image_id: string;
  status: string;
  created_at: string;
  report: AnalysisReport | null;
}

export interface HistoryResponse {
  items: HistoryItem[];
  total: number;
  page: number;
  page_size: number;
}

export const analysisApi = {
  getHistory: (page: number, pageSize: number) =>
    apiClient.get<HistoryResponse>(`/analysis/history?page=${page}&page_size=${pageSize}`),
  getSession: (sessionId: string) =>
    apiClient.get<HistoryItem>(`/analysis/sessions/${sessionId}`),
};
