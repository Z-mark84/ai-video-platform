/** M4 文案生成 - API类型定义 */

export interface GenerateRequest {
  topic: string
  genre: string
  target_length: string
  style: string
  reference: string
  preserve_literary: boolean
}

export interface CopywriteSegment {
  id: string
  project_id: string
  segment_index: number
  title: string
  content: string
  word_count: number
  estimated_duration_sec: number
  scene_description: string
  transition_hint: string
  key_visuals: string[]
  emotion: string
  status: string
}

export interface GenerateResponse {
  project_id: string
  title: string
  segments: CopywriteSegment[]
  total_word_count: number
  total_duration_sec: number
}

export interface CopywriteTemplate {
  id: string
  name: string
  genre: string
  structure: Array<{ title: string; description: string; word_count: number }>
  style_guide: string
  is_system: boolean
}
