<template>
  <div class="copywrite-panel">
    <div class="panel-header">
      <h2>📝 文案生成</h2>
      <p class="subtitle">M4 · AI长视频文案生成引擎</p>
      <n-tag :type="llmAvailable ? 'success' : 'warning'" size="small" class="status-tag">
        {{ llmAvailable ? 'DeepSeek-R1 在线' : 'Mock模式（内置模板）' }}
      </n-tag>
    </div>

    <!-- 输入区域 -->
    <n-card title="生成文案" size="small" v-if="!currentProject">
      <div class="generate-form">
        <n-input
          v-model:value="topic"
          placeholder="输入文案主题，例如：为什么穷人越穷富人越富"
          :maxlength="500"
          size="large"
        />
        <div class="form-row">
          <n-select v-model:value="genre" :options="genreOptions" style="width:140px" />
          <n-select v-model:value="targetLength" :options="lengthOptions" style="width:120px" />
          <n-select v-model:value="style" :options="styleOptions" style="width:120px" />
        </div>
        <n-input
          v-model:value="reference"
          type="textarea"
          :autosize="{ minRows: 2, maxRows: 4 }"
          placeholder="参考内容（可选）：提供一些背景信息或参考文案"
          clearable
        />
        <n-checkbox v-model:checked="preserveLiterary">保留文学性修辞</n-checkbox>
        <n-button type="primary" block size="large" :loading="loading" @click="generate" :disabled="!topic.trim()">
          {{ llmAvailable ? '🤖 AI生成文案' : '📄 生成示例文案' }}
        </n-button>
      </div>
    </n-card>

    <!-- 文案展示 -->
    <template v-if="currentProject">
      <div class="project-info">
        <n-tag size="small" type="info">{{ genreLabel }}文案</n-tag>
        <span class="word-count">共 {{ totalWords }} 字 / 约 {{ totalDuration }} 秒</span>
        <n-button size="tiny" quaternary @click="backToList">← 返回</n-button>
      </div>

      <n-collapse :default-expanded-names="['segments']" class="segments-list">
        <n-collapse-item title="📄 文案段落" name="segments">
          <div v-for="(seg, idx) in segments" :key="seg.id" class="segment-card">
            <div class="segment-header">
              <span class="segment-index">第{{ idx + 1 }}段</span>
              <n-tag size="tiny" :bordered="false">{{ seg.emotion }}</n-tag>
              <span class="segment-duration">{{ seg.estimated_duration_sec }}秒</span>
            </div>
            <n-input
              v-model:value="seg.content"
              type="textarea"
              :autosize="{ minRows: 3, maxRows: 8 }"
            />
            <div class="segment-meta">
              <n-input
                v-model:value="seg.scene_description"
                placeholder="场景描述（推送到M1/M2）"
                size="small"
                clearable
              />
            </div>
          </div>
        </n-collapse-item>
      </n-collapse>

      <div class="actions">
        <n-button @click="sendToM1">
          <template #icon>✏️</template>
          推送至M1提示词引擎
        </n-button>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import type { CopywriteSegment } from '../../api/copywriteTypes'
import * as api from '../../api/copywrite'

const message = useMessage()

const topic = ref('')
const genre = ref('cognitive')
const targetLength = ref('medium')
const style = ref('normal')
const reference = ref('')
const preserveLiterary = ref(false)
const loading = ref(false)
const llmAvailable = ref(false)
const currentProject = ref<string | null>(null)
const segments = ref<CopywriteSegment[]>([])
const totalWords = ref(0)
const totalDuration = ref(0)

const genreOptions = [
  { label: '🧠 认知科普', value: 'cognitive' },
  { label: '📖 叙事故事', value: 'story' },
  { label: '🎓 知识分享', value: 'lecture' },
]
const lengthOptions = [
  { label: '短篇(500字)', value: 'short' },
  { label: '中篇(1500字)', value: 'medium' },
  { label: '长篇(3000字)', value: 'long' },
]
const styleOptions = [
  { label: '平实', value: 'normal' },
  { label: '情感', value: 'emotional' },
  { label: '幽默', value: 'humorous' },
]

const genreLabel = computed(() => genreOptions.find(g => g.value === genre.value)?.label || genre.value)

async function generate() {
  loading.value = true
  try {
    const res = await api.generateCopywrite({
      topic: topic.value,
      genre: genre.value,
      target_length: targetLength.value,
      style: style.value,
      reference: reference.value,
      preserve_literary: preserveLiterary.value,
    })
    currentProject.value = res.project_id
    segments.value = res.segments
    totalWords.value = res.total_word_count
    totalDuration.value = res.total_duration_sec
    message.success(`✅ 文案生成完成！共 ${res.total_word_count} 字，${res.segments.length} 段`)
  } catch (e: unknown) {
    message.error(e instanceof Error ? e.message : '生成失败')
  } finally {
    loading.value = false
  }
}

function backToList() {
  currentProject.value = null
  segments.value = []
}

function sendToM1() {
  message.success('文案已推送至M1提示词引擎（演示占位）')
}

onMounted(async () => {
  try {
    const status = await api.checkStatus()
    llmAvailable.value = status.llm_available
  } catch {
    llmAvailable.value = false
  }
})
</script>

<style scoped>
.copywrite-panel { display: flex; flex-direction: column; gap: 16px; }
.panel-header { text-align: center; position: relative; }
.panel-header h2 { font-size: 1.4rem; font-weight: 700; }
.status-tag { position: absolute; right: 0; top: 0; }
.generate-form { display: flex; flex-direction: column; gap: 12px; }
.form-row { display: flex; gap: 8px; flex-wrap: wrap; }
.project-info { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.word-count { font-size: 0.85rem; opacity: 0.7; }
.segments-list { overflow-y: auto; max-height: calc(100vh - 400px); }
.segment-card { margin-bottom: 12px; padding: 12px; background: rgba(99,102,241,0.04); border-radius: 8px; border: 1px solid rgba(99,102,241,0.1); }
.segment-header { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.segment-index { font-weight: 600; font-size: 0.85rem; }
.segment-duration { font-size: 0.75rem; opacity: 0.6; margin-left: auto; font-family: monospace; }
.segment-meta { margin-top: 8px; }
.actions { display: flex; gap: 8px; justify-content: center; }
</style>
