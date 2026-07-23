/** M4 文案生成 - API服务层 */

import type { GenerateRequest, GenerateResponse, CopywriteSegment, CopywriteTemplate } from './copywriteTypes'

const BASE = 'http://localhost:8000/api/v1/copywrite'

async function req<T>(url: string, opts?: RequestInit): Promise<T> {
  const res = await fetch(url, { headers: { 'Content-Type': 'application/json' }, ...opts })
  if (!res.ok) throw new Error(((await res.json().catch(() => ({}))).detail) || res.statusText)
  return res.json()
}

export async function generateCopywrite(data: GenerateRequest): Promise<GenerateResponse> {
  return req(`${BASE}/generate`, { method: 'POST', body: JSON.stringify(data) })
}

export async function getProjects() {
  return req(`${BASE}/projects`)
}

export async function getSegments(projectId: string): Promise<CopywriteSegment[]> {
  return req(`${BASE}/projects/${projectId}/segments`)
}

export async function updateSegment(id: string, content: string, scene_description = '', emotion = 'neutral') {
  return req(`${BASE}/segments/${id}`, {
    method: 'PUT',
    body: JSON.stringify({ content, scene_description, emotion }),
  })
}

export async function getTemplates(genre?: string): Promise<CopywriteTemplate[]> {
  const p = genre ? `?genre=${genre}` : ''
  return req(`${BASE}/templates${p}`)
}

export async function checkStatus(): Promise<{ llm_available: boolean; mode: string }> {
  return req(`${BASE}/status`)
}
