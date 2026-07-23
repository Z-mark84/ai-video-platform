/** M7 角色一致性 - API类型定义 */

export interface CharacterInfo {
  id: string; name: string
  reference_images: string[]
  attributes: { gender: string; age_range: string; style: string; default_outfit: string }
  tags: string[]; usage_count: number; face_similarity: number | null
  created_at: string
}

export interface CharacterCreateRequest {
  name: string; gender: string; age_range: string; style: string
  default_outfit: string; tags: string[]
}

export interface ConsistencyScore {
  character_id: string; score: number; passed: boolean
  details: Record<string, unknown>
}
