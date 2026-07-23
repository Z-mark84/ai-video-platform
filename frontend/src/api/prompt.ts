/** M1 提示词引擎 - API 服务层 */

import type {
  NLInputRequest,
  NLInputResponse,
  TagInputRequest,
  ConflictCheckResponse,
  OptimizeRequest,
  PromptOutput,
  TagItem,
  TemplateItem,
} from './types'

const BASE_URL = 'http://localhost:8000/api/v1/prompt'

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || `HTTP ${res.status}`)
  }
  return res.json()
}

/** 自然语言输入 → 解析为结构化标签 */
export async function nlInput(req: NLInputRequest): Promise<NLInputResponse> {
  return request<NLInputResponse>(`${BASE_URL}/nl-input`, {
    method: 'POST',
    body: JSON.stringify(req),
  })
}

/** 标签输入 → 预览 */
export async function tagInput(req: TagInputRequest): Promise<NLInputResponse> {
  return request<NLInputResponse>(`${BASE_URL}/tag-input`, {
    method: 'POST',
    body: JSON.stringify(req),
  })
}

/** 冲突检测 */
export async function checkConflicts(tags: TagItem[]): Promise<ConflictCheckResponse> {
  return request<ConflictCheckResponse>(`${BASE_URL}/conflict-check`, {
    method: 'POST',
    body: JSON.stringify({ tags }),
  })
}

/** 完整优化 → 标准输出JSON */
export async function optimizePrompt(req: OptimizeRequest): Promise<PromptOutput> {
  return request<PromptOutput>(`${BASE_URL}/optimize`, {
    method: 'POST',
    body: JSON.stringify(req),
  })
}

/** 获取感性词库 */
export async function getMoods(category?: string): Promise<{ moods: string[]; categories: Record<string, string[]> }> {
  const params = category ? `?category=${category}` : ''
  return request(`${BASE_URL}/moods${params}`)
}

/** 获取模板列表 */
export async function getTemplates(genre?: string): Promise<TemplateItem[]> {
  const params = genre ? `?genre=${genre}` : ''
  return request<TemplateItem[]>(`${BASE_URL}/templates${params}`)
}
