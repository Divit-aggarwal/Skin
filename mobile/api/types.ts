export type SeverityLevel = 'mild' | 'moderate' | 'severe';

export interface ImageOut {
  id: string;
  user_id: string;
  mime_type: string;
  size_bytes: number;
  blur_score: number;
  face_count: number;
  quality_passed: boolean;
  quality_reason: string | null;
  created_at: string;
}

export interface ZoneScore {
  zone: string;
  score: number;
}

export interface RecommendationOut {
  id: string;
  category: string;
  text: string;
  priority: number;
}

export interface Detection {
  bbox: [number, number, number, number]; // [cx, cy, w, h] in original image pixel space
  confidence: number;
  zone: string;
}

export interface ReportOut {
  id: string;
  session_id: string;
  acne_score: number;
  wrinkle_score: number;
  oiliness_score: number;
  overall_score: number;
  severity_level: SeverityLevel;
  blur_score: number;
  face_count: number;
  zone_breakdown: ZoneScore[];
  detections: Detection[];
  model_version: string;
  created_at: string;
}

export interface SessionOut {
  id: string;
  user_id: string;
  image_id: string;
  status: string;
  created_at: string;
  report: ReportOut | null;
  recommendations: RecommendationOut[];
}

export interface SessionListItem {
  id: string;
  image_id: string;
  status: string;
  overall_score: number | null;
  severity_level: SeverityLevel | null;
  created_at: string;
}

export interface HistoryResponse {
  items: SessionListItem[];
  total: number;
  page: number;
  page_size: number;
}
