<template>
  <div class="asset-panel">
    <div class="panel-header">
      <h2>📦 素材管理</h2>
      <p class="subtitle">M3 · AI生成 & 上传素材统一管理</p>
    </div>

    <!-- 概览统计 -->
    <div class="stats-row">
      <n-statistic
        v-for="stat in store.categoryStats"
        :key="stat.name"
        :label="`${stat.icon} ${stat.name}`"
        :value="stat.count"
        class="stat-card"
      >
      </n-statistic>
      <n-statistic label="📊 总计" :value="store.totalCount" class="stat-card highlight" />
    </div>

    <!-- 操作栏 -->
    <div class="toolbar">
      <n-input
        v-model:value="searchText"
        placeholder="搜索素材名称..."
        clearable
        style="width: 280px"
        @input="onSearch"
      >
        <template #prefix>🔍</template>
      </n-input>

      <n-select
        v-model:value="filterCategory"
        :options="categoryOptions"
        placeholder="全部分类"
        style="width: 140px"
        @update:value="onFilterChange"
      />

      <n-button type="primary" :loading="store.loading" @click="mockGenerate">
        <template #icon>🎲</template>
        Mock生成素材
      </n-button>
    </div>

    <!-- 素材网格 -->
    <div v-if="store.loading && store.assets.length === 0" class="loading-area">
      <n-spin size="large" />
    </div>

    <div v-else-if="store.assets.length === 0" class="empty-area">
      <n-empty description="暂无素材，点击 Mock生成素材 添加">
        <template #extra>
          <n-button size="small" @click="mockGenerate">生成示例素材</n-button>
        </template>
      </n-empty>
    </div>

    <n-grid v-else :cols="4" :x-gap="12" :y-gap="12" class="asset-grid">
      <n-gi v-for="asset in store.assets" :key="asset.id">
        <n-card :title="asset.original_name" size="small" hoverable class="asset-card">
          <template #cover>
            <div class="card-cover">
              <n-icon size="32" color="#6366f1" v-if="asset.mime_type.startsWith('image/')">🖼️</n-icon>
              <n-icon size="32" color="#10b981" v-else-if="asset.mime_type.startsWith('audio/')">🎵</n-icon>
              <n-icon size="32" color="#f59e0b" v-else>📄</n-icon>
            </div>
          </template>
          <div class="asset-meta">
            <n-tag size="tiny" :bordered="false">{{ categoryLabel(asset.category) }}</n-tag>
            <span class="file-size">{{ formatSize(asset.file_size) }}</span>
          </div>
          <div class="asset-tags" v-if="asset.tags.length">
            <n-tag v-for="tag in asset.tags.slice(0, 3)" :key="tag" size="tiny" :bordered="false" round>
              {{ tag }}
            </n-tag>
            <span v-if="asset.tags.length > 3" class="more-tags">+{{ asset.tags.length - 3 }}</span>
          </div>
          <template #action>
            <n-button size="tiny" quaternary @click="store.removeAsset(asset.id)">
              <template #icon>🗑️</template>
            </n-button>
          </template>
        </n-card>
      </n-gi>
    </n-grid>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { useAssetStore } from '../../stores/assetStore'

const store = useAssetStore()
const message = useMessage()

const searchText = ref('')
const filterCategory = ref<string | null>(null)

const categoryOptions = computed(() => [
  { label: '全部分类', value: null },
  ...store.categories.map(c => ({ label: `${c.icon} ${c.name}`, value: c.id })),
])

const categoryMap = computed(() => {
  const m: Record<string, string> = {}
  store.categories.forEach(c => { m[c.id] = c.name })
  return m
})

function categoryLabel(id: string) { return categoryMap.value[id] || id }

function formatSize(bytes: number) {
  if (bytes < 1024) return `${bytes}B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)}MB`
}

async function mockGenerate() {
  const asset = await store.mockUpload('proj-demo')
  if (asset) message.success(`✅ 生成素材: ${asset.original_name}`)
}

let searchTimer: ReturnType<typeof setTimeout> | null = null
function onSearch() {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => store.fetchAssets({ search: searchText.value || undefined }), 300)
}

function onFilterChange(val: string | null) {
  store.fetchAssets({ category: val || undefined })
}

onMounted(() => {
  store.fetchCategories()
  store.fetchAssets()
})
</script>

<style scoped>
.asset-panel { display: flex; flex-direction: column; gap: 16px; }
.panel-header { text-align: center; }
.panel-header h2 { font-size: 1.4rem; font-weight: 700; }

.stats-row { display: flex; gap: 12px; flex-wrap: wrap; }
.stat-card { flex: 1; min-width: 100px; background: rgba(99,102,241,0.06); border-radius: 8px; padding: 12px 16px; border: 1px solid rgba(99,102,241,0.1); }
.stat-card.highlight { border-color: #6366f1; }

.toolbar { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }

.loading-area, .empty-area { display: flex; justify-content: center; align-items: center; min-height: 300px; }

.asset-grid { overflow-y: auto; max-height: calc(100vh - 360px); }

.asset-card { cursor: default; }
.asset-card:hover { border-color: #6366f1; }

.card-cover { display: flex; justify-content: center; align-items: center; height: 100px; background: rgba(99,102,241,0.05); }
.card-cover .n-icon { filter: none; }

.asset-meta { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.file-size { font-size: 0.75rem; opacity: 0.6; font-family: monospace; }

.asset-tags { display: flex; gap: 4px; flex-wrap: wrap; margin-top: 6px; }
.more-tags { font-size: 0.7rem; opacity: 0.5; align-self: center; }
</style>
