/** M2 AI绘图服务 - API服务层 */

import type { RenderTaskRequest, RenderTask, RenderTaskList, PipelineConfig, ModelInfo, WorkflowTemplate } from './drawTypes'

const BASE_URL = 'http://localhost:8000/api/v1/draw'

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

/** 创建渲染任务 */
export async function createRenderTask(req: RenderTaskRequest): Promise<RenderTask> {
  return request<RenderTask>(`${BASE_URL}/render`, {
    method: 'POST',
    body: JSON.stringify(req),
  })
}

/** 批量渲染 */
export async function batchRender(tasks: RenderTaskRequest[]): Promise<{ task_ids: string[]; count: number }> {
  return request(`${BASE_URL}/batch-render`, {
    method: 'POST',
    body: JSON.stringify({ project_id: tasks[0]?.project_id || 'default', tasks }),
  })
}

/** 获取任务列表 */
export async function getTasks(projectId?: string, page = 1, size = 20): Promise<RenderTaskList> {
  const params = new URLSearchParams()
  if (projectId) params.set('project_id', projectId)
  params.set('page', String(page))
  params.set('size', String(size))
  return request(`${BASE_URL}/tasks?${params}`)
}

/** 查询任务状态 */
export async function getTask(taskId: string): Promise<RenderTask> {
  return request(`${BASE_URL}/tasks/${taskId}`)
}

/** 获取管线列表 */
export async function getPipelines(): Promise<PipelineConfig[]> {
  return request(`${BASE_URL}/pipelines`)
}

/** 获取模型列表 */
export async function getModels(modelType?: string): Promise<ModelInfo[]> {
  const params = modelType ? `?model_type=${modelType}` : ''
  return request(`${BASE_URL}/models${params}`)
}

/** 获取工作流模板 */
export async function getWorkflows(workflowType?: string): Promise<WorkflowTemplate[]> {
  const params = workflowType ? `?workflow_type=${workflowType}` : ''
  return request(`${BASE_URL}/workflows${params}`)
}
