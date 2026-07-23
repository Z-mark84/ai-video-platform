/** M6 智能剪辑 - API服务层 */

import type { VideoProject, EditingRequest, TimelineSegment, RenderProgress } from './editTypes'

const BASE = 'http://localhost:8000/api/v1/edit'

async function req<T>(url: string, opts?: RequestInit): Promise<T> {
  const res = await fetch(url, { headers: { 'Content-Type': 'application/json' }, ...opts })
  if (!res.ok) throw new Error(((await res.json().catch(() => ({}))).detail) || res.statusText)
  return res.json()
}

export async function createProject(data: EditingRequest): Promise<VideoProject> {
  return req(`${BASE}/projects`, { method: 'POST', body: JSON.stringify(data) })
}

export async function getProjects(): Promise<VideoProject[]> {
  return req(`${BASE}/projects`)
}

export async function getProject(id: string): Promise<VideoProject> {
  return req(`${BASE}/projects/${id}`)
}

export async function updateTimeline(id: string, segments: TimelineSegment[]): Promise<VideoProject> {
  return req(`${BASE}/projects/${id}/timeline`, { method: 'PUT', body: JSON.stringify(segments) })
}

export async function renderProject(id: string): Promise<RenderProgress> {
  return req(`${BASE}/projects/${id}/render`, { method: 'POST' })
}

export async function getBGM(): Promise<Array<{ id: string; name: string }>> {
  return req(`${BASE}/bgm`)
}

export async function getTransitions(): Promise<Array<{ id: string; name: string }>> {
  return req(`${BASE}/transitions`)
}
