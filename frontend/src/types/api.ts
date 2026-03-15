// Aligns with backend standard envelope and analysis response

export interface ApiEnvelope<T = unknown> {
  success: boolean;
  code: string;
  message: string;
  data?: T;
}

export interface AnalyseRequest {
  image_b64: string;
  session_id: string;
  timestamp: string; // ISO
}

export interface ConditionPrediction {
  condition?: string;
  condition_name?: string;
  confidence: number;
  class_id: number;
}

export interface Recommendation {
  category: string;
  content: string;
  priority_rank: number;
}

export interface AnalysisResult {
  analysis_id?: string;
  skin_health_score: number;
  severity_tier: string;
  top_condition: string;
  top_confidence: number;
  /** Backend may return either "predictions" or "conditions" */
  predictions?: ConditionPrediction[];
  conditions?: ConditionPrediction[];
  recommendations: Recommendation[];
  processing_time_ms?: number;
  history?: SessionHistoryItem[];
}

export interface SessionHistoryItem {
  id: string;
  created_at: string;
  skin_health_score: number;
  severity_tier: string;
  top_condition: string;
}

export interface HistoryResponse {
  sessions: SessionHistoryItem[];
  total: number;
}

export type ErrorCode =
  | "NO_FACE_DETECTED"
  | "LOW_QUALITY_IMAGE"
  | "INVALID_IMAGE"
  | "MODEL_UNAVAILABLE"
  | "SESSION_EXPIRED"
  | "RATE_LIMIT_EXCEEDED";
