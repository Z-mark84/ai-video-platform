/** M8 质量评估 - API服务层 */

import type { EvaluateRequest, QualityReport, FeedbackStats } from './qualityTypes'

const BASE = 'http://localhost:8000/api/v1/quality'

async function req<T>(url: string, opts?: RequestInit): Promise<T> {
  const res = await fetch(url, { headers: { 'Content-Type': 'application/json' }, ...opts })
  if (!res.ok) throw new Error(((await res.json().catch(() => ({}))).detail) || res.statusText)
  return res.json()
}

export async function evaluate(data: EvaluateRequest): Promise<QualityReport> {
  return req(`${BASE}/evaluate`, { method: 'POST', body: JSON.stringify(data) })
}

export async function getReports(): Promise<QualityReport[]> {
  return req(`${BASE}/reports`)
}

export async function submitFeedback(taskId: string, rating: number, comment = '') {
  return req(`${BASE}/feedback`, { method: 'POST', body: JSON.stringify({ task_id: taskId, rating, comment }) })
}

export async function getFeedbackStats(): Promise<FeedbackStats> {
  return req(`${BASE}/feedback/stats`)
}
