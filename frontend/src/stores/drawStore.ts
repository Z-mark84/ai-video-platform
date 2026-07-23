/** M2 AI绘图服务 - Pinia 状态管理 */

import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { RenderTask, RenderTaskRequest, PipelineConfig } from '../api/drawTypes'
import * as api from '../api/draw'

export const useDrawStore = defineStore('draw', () => {
  // 状态
  const pendingTasks = ref<RenderTask[]>([])
  const completedTasks = ref<RenderTask[]>([])
  const pipelines = ref<PipelineConfig[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 操作
  async function submitRender(req: RenderTaskRequest) {
    loading.value = true
    error.value = null
    try {
      const task = await api.createRenderTask(req)
      completedTasks.value.unshift(task)
      return task
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : '渲染失败'
      return null
    } finally {
      loading.value = false
    }
  }

  async function fetchPipelines() {
    try {
      pipelines.value = await api.getPipelines()
    } catch {
      // 静默
    }
  }

  async function refreshTasks(projectId?: string) {
    try {
      const res = await api.getTasks(projectId, 1, 50)
      completedTasks.value = res.items.filter(t => t.status === 'completed')
      pendingTasks.value = res.items.filter(t => t.status !== 'completed')
    } catch {
      // 静默
    }
  }

  return { pendingTasks, completedTasks, pipelines, loading, error, submitRender, fetchPipelines, refreshTasks }
})
