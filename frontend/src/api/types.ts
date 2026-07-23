/** M1 提示词引擎 - API 类型定义 */

export interface TagItem {
  tag: string
  category: string
  weight: number
  tag_zh: string | null
}

export interface NLInputRequest {
  project_id: string
  text: string
  context_tags: string[]
  lang: string
}

export interface TagInputRequest {
  project_id: string
  tags: TagItem[]
}

export interface NLInputResponse {
  input_id: string
  parsed_tags: TagItem[]
  preview_zh: string
  preview_en: string
  confidence: number
}

export interface ConflictCheckResponse {
  has_conflict: boolean
  conflicts: Array<{
    group: string
    reason: string
    keeper: string
    removed: string[]
  }>
  cleaned_tags: TagItem[]
}

export interface PromptOutput {
  id: string
  version: string
  classification: string
  input_raw: string
  positive_prompt: string
  negative_prompt: string
  params: Record<string, unknown>
  weights: Record<string, number>
  mapping_log: Array<{
    source: string
    count: number
    weight: number
    items: string[]
  }>
}

export interface OptimizeRequest {
  tags: TagItem[]
  classification: string
  preserve_literary: boolean
}

export interface TemplateItem {
  id: string
  name: string
  genre: string
  tags: TagItem[]
  style_guide: string | null
}
