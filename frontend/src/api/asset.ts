/** M3 素材管理 - API服务层 */

import type { AssetInfo, AssetListResponse, AssetCategory, AssetTagCount, CategoryStats } from './assetTypes'

const BASE_URL = 'http://localhost:8000/api/v1/asset'

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, { headers: { 'Content-Type': 'application/json' }, ...options })
  if (!res.ok) throw new Error((await res.json().catch(() => ({ detail: res.statusText }))).detail || `HTTP ${res.status}`)
  return res.json()
}

/** 上传素材 */
export async function uploadAsset(projectId: string, file: File, category = 'uncategorized', tags = ''): Promise<AssetInfo> {
  const form = new FormData()
  form.append('project_id', projectId)
  form.append('file', file)
  form.append('category', category)
  form.append('tags', tags)
  const res = await fetch(`${BASE_URL}/upload`, { method: 'POST', body: form })
  if (!res.ok) throw new Error((await res.json().catch(() => ({ detail: res.statusText }))).detail || '上传失败')
  return res.json()
}

/** Mock上传（模拟M2生成结果入库） */
export async function mockUploadAsset(projectId = 'default'): Promise<AssetInfo> {
  return request(`${BASE_URL}/upload-from-mock?project_id=${projectId}`, { method: 'POST' })
}

/** 素材列表 */
export async function getAssets(params?: {
  project_id?: string; category?: string; mime_type?: string; tag?: string; search?: string; page?: number; size?: number
}): Promise<AssetListResponse> {
  const p = new URLSearchParams()
  if (params) Object.entries(params).forEach(([k, v]) => { if (v !== undefined) p.set(k, String(v)) })
  return request(`${BASE_URL}/list?${p}`)
}

/** 素材详情 */
export async function getAsset(id: string): Promise<AssetInfo> {
  return request(`${BASE_URL}/${id}`)
}

/** 更新素材 */
export async function updateAsset(id: string, data: { category?: string; tags?: string[]; original_name?: string }): Promise<AssetInfo> {
  return request(`${BASE_URL}/${id}`, { method: 'PUT', body: JSON.stringify(data) })
}

/** 删除素材 */
export async function deleteAsset(id: string): Promise<{ success: boolean }> {
  return request(`${BASE_URL}/${id}`, { method: 'DELETE' })
}

/** 分类列表 */
export async function getCategories(): Promise<AssetCategory[]> {
  return request(`${BASE_URL}/categories`)
}

/** 分类统计 */
export async function getCategoryStats(projectId?: string): Promise<CategoryStats[]> {
  const p = projectId ? `?project_id=${projectId}` : ''
  return request(`${BASE_URL}/categories/stats${p}`)
}

/** 标签统计 */
export async function getTags(projectId?: string): Promise<AssetTagCount[]> {
  const p = projectId ? `?project_id=${projectId}` : ''
  return request(`${BASE_URL}/tags${p}`)
}

/** 概览统计 */
export async function getStatsSummary(): Promise<{ total_assets: number; total_size_bytes: number; categories: CategoryStats[] }> {
  return request(`${BASE_URL}/stats/summary`)
}
