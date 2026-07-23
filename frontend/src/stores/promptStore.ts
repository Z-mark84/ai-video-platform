/** M1 提示词引擎 - Pinia 状态管理 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { TagItem, TemplateItem, PromptOutput } from '../api/types'
import * as api from '../api/prompt'

export const usePromptStore = defineStore('prompt', () => {
  // === 状态 ===
  const inputText = ref('')
  const inputChannel = ref<'nl' | 'tag' | 'mixed'>('nl')
  const selectedTags = ref<TagItem[]>([])
  const tags = ref<Map<string, TagItem[]>>(new Map())
  const previewZh = ref('')
  const previewEn = ref('')
  const confidence = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const lastOutput = ref<PromptOutput | null>(null)
  const templates = ref<TemplateItem[]>([])
  const currentTemplate = ref<TemplateItem | null>(null)
  const history = ref<Array<{ text: string; time: string }>>([])
  const preserveLiterary = ref(false)

  // === 计算属性 ===
  const hasConflicts = computed(() => selectedTags.value.length === 0 && tags.value.size > 0)
  const inputLength = computed(() => inputText.value.length)

  // === 操作 ===
  async function submitNL() {
    if (!inputText.value.trim()) return
    loading.value = true
    error.value = null
    try {
      const res = await api.nlInput({
        project_id: 'project-' + Date.now().toString(36),
        text: inputText.value,
        context_tags: [],
        lang: 'zh',
      })
      selectedTags.value = res.parsed_tags
      previewZh.value = res.preview_zh
      previewEn.value = res.preview_en
      confidence.value = res.confidence

      // 加入历史
      history.value.unshift({
        text: inputText.value,
        time: new Date().toLocaleTimeString(),
      })
      if (history.value.length > 50) history.value.pop()
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : '请求失败'
    } finally {
      loading.value = false
    }
  }

  async function submitTags() {
    const tagList = Array.from(tags.value.values()).flat()
    if (tagList.length === 0) return
    loading.value = true
    error.value = null
    try {
      const res = await api.tagInput({
        project_id: 'project-' + Date.now().toString(36),
        tags: tagList,
      })
      selectedTags.value = res.parsed_tags
      previewZh.value = res.preview_zh
      previewEn.value = res.preview_en
      confidence.value = res.confidence
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : '请求失败'
    } finally {
      loading.value = false
    }
  }

  async function optimize() {
    if (selectedTags.value.length === 0) return
    loading.value = true
    error.value = null
    try {
      const res = await api.optimizePrompt({
        tags: selectedTags.value,
        classification: currentTemplate.value?.genre || 'scene',
        preserve_literary: preserveLiterary.value,
      })
      lastOutput.value = res
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : '优化失败'
    } finally {
      loading.value = false
    }
  }

  async function fetchTemplates() {
    try {
      templates.value = await api.getTemplates()
    } catch {
      // 静默失败
    }
  }

  function applyTemplate(tpl: TemplateItem) {
    currentTemplate.value = tpl
    inputText.value = tpl.name
    tags.value.set('template', tpl.tags)
    submitTags()
  }

  function addTag(tag: TagItem) {
    const existing = tags.value.get(tag.category) || []
    existing.push(tag)
    tags.value.set(tag.category, existing)
  }

  function removeTag(category: string, index: number) {
    const existing = tags.value.get(category)
    if (existing) {
      existing.splice(index, 1)
      if (existing.length === 0) tags.value.delete(category)
    }
  }

  function clearAll() {
    inputText.value = ''
    selectedTags.value = []
    tags.value.clear()
    previewZh.value = ''
    previewEn.value = ''
    confidence.value = 0
    lastOutput.value = null
    error.value = null
    currentTemplate.value = null
  }

  return {
    inputText, inputChannel, selectedTags, tags,
    previewZh, previewEn, confidence,
    loading, error, lastOutput, templates, currentTemplate,
    history, preserveLiterary,
    hasConflicts, inputLength,
    submitNL, submitTags, optimize, fetchTemplates,
    applyTemplate, addTag, removeTag, clearAll,
  }
})
