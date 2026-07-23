/** Pipeline 视频生成 - API 服务层 */

const BASE_URL = 'http://localhost:8000/api/v1/pipeline'

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

// ---- 类型定义 ----

export interface PipelineStageResult {
  stage: string
  status: 'pending' | 'running' | 'completed' | 'failed' | 'skipped'
  progress: number
  message: string
  output: Record<string, any>
  error?: string
}

export interface PipelineGenerateRequest {
  topic: string
  genre?: string
  target_length?: string
  style?: string
  lang?: string
  voice_style?: string
  mood_tags?: string[]
  auto_generate?: boolean
}

export interface PipelineGenerateResponse {
  project_id: string
  title: string
  status: string
  stages: PipelineStageResult[]
  current_stage: string
  overall_progress: number
  estimated_duration_sec: number
  created_at: string
}

export interface PipelineProject {
  id: string
  title: string
  topic: string
  genre: string
  status: string
  stages: PipelineStageResult[]
  overall_progress: number
  created_at: string
}

// ---- API 函数 ----

/** 一键生成视频 - 执行完整流水线 */
export async function generateVideo(req: PipelineGenerateRequest): Promise<PipelineGenerateResponse> {
  return request<PipelineGenerateResponse>(`${BASE_URL}/generate`, {
    method: 'POST',
    body: JSON.stringify(req),
  })
}

/** 获取所有项目 */
export async function listProjects(): Promise<PipelineProject[]> {
  return request<PipelineProject[]>(`${BASE_URL}/projects`)
}

/** 获取项目详情 */
export async function getProject(projectId: string): Promise<PipelineProject> {
  return request<PipelineProject>(`${BASE_URL}/projects/${projectId}`)
}

/** 查询项目状态 */
export async function getProjectStatus(projectId: string): Promise<{
  project_id: string
  status: string
  stages: PipelineStageResult[]
  overall_progress: number
  result_video_url?: string
}> {
  return request(`${BASE_URL}/projects/${projectId}/status`)
}
