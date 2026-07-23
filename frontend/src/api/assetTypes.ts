/** M3 素材管理 - API类型定义 */

export interface AssetInfo {
  id: string
  project_id: string
  filename: string
  original_name: string
  file_size: number
  mime_type: string
  category: string
  tags: string[]
  width: number | null
  height: number | null
  duration_sec: number | null
  source: string
  storage_path: string
  thumbnail_path: string | null
  is_deleted: boolean
  created_at: string
}

export interface AssetListResponse {
  items: AssetInfo[]
  total: number
  page: number
  size: number
}

export interface AssetCategory {
  id: string
  name: string
  description: string
  color: string
  icon: string
  sort_order: number
}

export interface AssetTagCount {
  tag: string
  count: number
}

export interface CategoryStats {
  name: string
  icon: string
  count: number
  color: string
}
