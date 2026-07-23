/** M3 素材管理 - Pinia 状态管理 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { AssetInfo, AssetCategory, CategoryStats } from '../api/assetTypes'
import * as api from '../api/asset'

export const useAssetStore = defineStore('asset', () => {
  const assets = ref<AssetInfo[]>([])
  const categories = ref<AssetCategory[]>([])
  const categoryStats = ref<CategoryStats[]>([])
  const totalAssets = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const totalCount = computed(() => totalAssets.value)
  const imageAssets = computed(() => assets.value.filter(a => a.mime_type.startsWith('image/')))
  const audioAssets = computed(() => assets.value.filter(a => a.mime_type.startsWith('audio/')))

  async function fetchAssets(params?: { category?: string; search?: string; page?: number }) {
    loading.value = true
    try {
      const res = await api.getAssets({ ...params, size: 50 })
      assets.value = res.items
      totalAssets.value = res.total
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : '加载失败'
    } finally {
      loading.value = false
    }
  }

  async function fetchCategories() {
    categories.value = await api.getCategories()
    categoryStats.value = await api.getCategoryStats()
  }

  async function removeAsset(id: string) {
    await api.deleteAsset(id)
    assets.value = assets.value.filter(a => a.id !== id)
    totalAssets.value--
  }

  async function mockUpload(projectId = 'default') {
    const asset = await api.mockUploadAsset(projectId)
    assets.value.unshift(asset)
    totalAssets.value++
    return asset
  }

  return { assets, categories, categoryStats, totalAssets, loading, error, totalCount, imageAssets, audioAssets, fetchAssets, fetchCategories, removeAsset, mockUpload }
})
