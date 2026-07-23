/** M2 AI绘图服务 - API类型定义 */

export interface RenderTaskRequest {
  project_id: string
  prompt_id: string
  positive_prompt: string
  negative_prompt: string
  params: Record<string, unknown>
  classification: string
  count: number
  reference_images: string[]
  denoising_strength: number
}

export interface RenderTask {
  task_id: string
  project_id: string
  prompt_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number
  results: string[]
  params_snapshot: Record<string, unknown>
  error: string | null
  created_at: string
  completed_at: string | null
  total_count: number
}

export interface RenderTaskList {
  items: RenderTask[]
  total: number
  page: number
  size: number
}

export interface PipelineConfig {
  id: string
  name: string
  pipeline_type: string
  base_model: string
  vae: string | null
  sampler: string
  cfg_scale_default: number
  steps_default: number
  is_active: boolean
}

export interface ModelInfo {
  id: string
  name: string
  model_type: string
  base_model: string
  is_active: boolean
}

export interface WorkflowTemplate {
  id: string
  name: string
  description: string
  workflow_type: string
  input_schema: Record<string, unknown>
  is_active: boolean
}
