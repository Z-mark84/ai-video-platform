/** M8 质量评估 - API类型定义 */

export interface QualityReport {
  id: string; project_id: string; task_type: string
  scores: {
    lpips_avg: number | null; clip_score_avg: number | null
    optical_flow_smoothness: number | null; face_similarity: number | null
    passed: boolean; regenerate_count: number; user_rating: number | null
    evaluated_at: string
  }
  suggestions: string[]; summary: string
}

export interface EvaluateRequest {
  task_id: string; project_id: string
  image_urls: string[]; prompt_text: string | null; task_type: string
}

export interface FeedbackStats {
  total: number; avg_rating: number; counts: Record<string, number>
}
