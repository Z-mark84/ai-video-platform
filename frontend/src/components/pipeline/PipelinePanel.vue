<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  NButton, NInput, NSelect, NTag, NProgress, NCard,
  NCollapse, NCollapseItem, NSpace, NDivider, NSpin,
  NAlert, useMessage
} from 'naive-ui'
import { generateVideo, type PipelineStageResult, type PipelineGenerateResponse } from '../../api/pipeline'
import { runDemoPipeline } from './demoPipeline'

const message = useMessage()

// 表单
const topic = ref('')
const genre = ref('cognitive')
const targetLength = ref('medium')
const style = ref('normal')
const voiceStyle = ref('documentary')
const generating = ref(false)

// 结果
const result = ref<PipelineGenerateResponse | null>(null)
const selectedStage = ref<string | null>(null)

const genreOptions = [
  { label: '🧠 认知科普', value: 'cognitive' },
  { label: '📖 叙事故事', value: 'story' },
  { label: '📚 知识分享', value: 'knowledge' },
  { label: '🎓 教程讲解', value: 'tutorial' },
]

const lengthOptions = [
  { label: '短视频 (1-3分钟)', value: 'short' },
  { label: '中视频 (3-8分钟)', value: 'medium' },
  { label: '长视频 (8-15分钟)', value: 'long' },
]

const styleOptions = [
  { label: '平实客观', value: 'normal' },
  { label: '情感充沛', value: 'emotional' },
  { label: '幽默风趣', value: 'humorous' },
  { label: '学术严谨', value: 'academic' },
]

const voiceOptions = [
  { label: '沉稳男声 (纪录片)', value: 'documentary' },
  { label: '温暖女声 (故事)', value: 'story' },
  { label: '新闻女声', value: 'news' },
  { label: '激昂男声', value: 'normal' },
]

// 预设话题
const presetTopics = [
  '为什么穷人越穷，富人越富？',
  '人工智能如何改变教育的未来',
  '一个普通人的不普通一年',
  '宇宙中最可怕的十个事实',
]

const stageLabels: Record<string, string> = {
  prompt: 'M1 提示词优化',
  copywrite: 'M4 文案生成',
  draw: 'M2 AI 绘图',
  tts: 'M5 TTS 配音',
  edit: 'M6 智能剪辑',
  quality: 'M8 质量评估',
}

const stageIcons: Record<string, string> = {
  prompt: '✏️',
  copywrite: '📝',
  draw: '🎨',
  tts: '🎙️',
  edit: '🎬',
  quality: '📊',
}

const stageColors: Record<string, string> = {
  completed: '#2dc653',
  running: '#4361ee',
  failed: '#ef4444',
  skipped: '#6b7280',
  pending: '#6b7280',
}

const overallProgress = computed(() => {
  if (!result.value) return 0
  return Math.round(result.value.overall_progress * 100)
})

function getStatusText(status: string): string {
  const map: Record<string, string> = {
    completed: '已完成',
    running: '执行中',
    pending: '等待中',
    failed: '失败',
    skipped: '已跳过',
  }
  return map[status] || status
}

function getStatusType(status: string): 'success' | 'info' | 'error' | 'warning' | 'default' {
  const map: Record<string, string> = {
    completed: 'success',
    running: 'info',
    pending: 'default',
    failed: 'error',
    skipped: 'warning',
  }
  return (map[status] as any) || 'default'
}

async function handleGenerate() {
  if (!topic.value.trim()) {
    message.warning('请输入视频主题')
    return
  }
  generating.value = true
  result.value = null

  // 先尝试调用后端 API
  try {
    const res = await generateVideo({
      topic: topic.value.trim(),
      genre: genre.value,
      target_length: targetLength.value,
      style: style.value,
      voice_style: voiceStyle.value,
      mood_tags: [],
      auto_generate: true,
    })
    result.value = res
    message.success('视频生成完成！(后端模式)')
  } catch (_e) {
    // 后端不可用，使用浏览器内置 Demo 模式
    message.info('后端未连接，使用 Demo 模式生成...')
    const demoResult = await runDemoPipeline({
      topic: topic.value.trim(),
      genre: genre.value,
      targetLength: targetLength.value,
      style: style.value,
      voiceStyle: voiceStyle.value,
    })
    result.value = demoResult
    message.success('视频生成完成！(Demo 模式)')
  } finally {
    generating.value = false
  }
}

function usePreset(preset: string) {
  topic.value = preset
}

function formatDuration(sec: number): string {
  const m = Math.floor(sec / 60)
  const s = Math.round(sec % 60)
  return m > 0 ? `${m}分${s}秒` : `${s}秒`
}
</script>

<template>
  <div class="pipeline-panel">
    <!-- 输入区 -->
    <n-card title="🎬 一键生成 AI 长视频" size="small" class="input-card">
      <n-space vertical :size="12">
        <n-input
          v-model:value="topic"
          type="textarea"
          :rows="2"
          placeholder="输入视频主题，如：为什么AI正在重塑教育行业、一个普通人如何实现财务自由..."
          :disabled="generating"
        />

        <!-- 预设话题 -->
        <n-space :size="6" wrap>
          <n-tag
            v-for="preset in presetTopics"
            :key="preset"
            type="info"
            :disabled="generating"
            style="cursor: pointer"
            @click="usePreset(preset)"
          >
            {{ preset.length > 20 ? preset.slice(0, 20) + '…' : preset }}
          </n-tag>
        </n-space>

        <n-space :size="16">
          <div class="param-group">
            <label class="param-label">视频类型</label>
            <n-select v-model:value="genre" :options="genreOptions" :disabled="generating" size="small" style="width: 140px" />
          </div>
          <div class="param-group">
            <label class="param-label">目标时长</label>
            <n-select v-model:value="targetLength" :options="lengthOptions" :disabled="generating" size="small" style="width: 150px" />
          </div>
          <div class="param-group">
            <label class="param-label">文案风格</label>
            <n-select v-model:value="style" :options="styleOptions" :disabled="generating" size="small" style="width: 120px" />
          </div>
          <div class="param-group">
            <label class="param-label">配音风格</label>
            <n-select v-model:value="voiceStyle" :options="voiceOptions" :disabled="generating" size="small" style="width: 160px" />
          </div>
        </n-space>

        <n-button
          type="primary"
          size="large"
          :loading="generating"
          :disabled="!topic.trim()"
          block
          @click="handleGenerate"
        >
          {{ generating ? '正在生成视频...' : '🚀 一键生成视频' }}
        </n-button>
      </n-space>
    </n-card>

    <!-- 结果区 -->
    <n-card v-if="result" title="📊 生成结果" size="small" class="result-card">
      <!-- 总进度 -->
      <div class="overall-bar">
        <n-progress
          type="line"
          :percentage="overallProgress"
          :status="result.status === 'completed' ? 'success' : 'default'"
          :height="24"
          :border-radius="12"
          :color="overallProgress >= 100 ? '#2dc653' : '#4361ee'"
        />
        <div class="result-meta">
          <n-tag type="success" v-if="result.status === 'completed'">✅ 生成完成</n-tag>
          <span class="meta-text">项目: {{ result.project_id }}</span>
          <span class="meta-text" v-if="result.estimated_duration_sec > 0">
            预估时长: {{ formatDuration(result.estimated_duration_sec) }}
          </span>
        </div>
      </div>

      <n-divider />

      <!-- 阶段流程 -->
      <div class="stage-flow">
        <div
          v-for="(stage, i) in result.stages"
          :key="stage.stage"
          class="stage-node"
          :class="[`status-${stage.status}`]"
        >
          <div class="stage-icon">{{ stageIcons[stage.stage] || '🔧' }}</div>
          <div class="stage-dot" :style="{ background: stageColors[stage.status] }"></div>
          <div class="stage-content">
            <div class="stage-name">{{ stageLabels[stage.stage] || stage.stage }}</div>
            <n-tag :type="getStatusType(stage.status)" size="tiny" :bordered="false">
              {{ getStatusText(stage.status) }}
            </n-tag>
            <div class="stage-msg" v-if="stage.message">{{ stage.message }}</div>
            <div class="stage-error" v-if="stage.error" style="color: #ef4444">
              ⚠️ {{ stage.error }}
            </div>
          </div>
          <!-- 连接线 -->
          <div v-if="i < result.stages.length - 1" class="stage-connector">
            <div
              class="connector-line"
              :style="{
                background: stage.status === 'completed' ? '#2dc653' : '#374151'
              }"
            ></div>
            <div class="connector-arrow">→</div>
          </div>
        </div>
      </div>

      <!-- 详细信息 -->
      <n-divider />
      <n-collapse>
        <n-collapse-item v-for="stage in result.stages" :key="stage.stage"
          :title="`${stageIcons[stage.stage]} ${stageLabels[stage.stage]} - ${stage.message || getStatusText(stage.status)}`"
          :name="stage.stage"
        >
          <div class="stage-detail" v-if="Object.keys(stage.output).length > 0">
            <div v-for="(value, key) in stage.output" :key="key" class="output-item">
              <span class="output-key">{{ key }}:</span>
              <span class="output-value" v-if="typeof value === 'string' || typeof value === 'number'">
                {{ typeof value === 'number' ? (Number.isInteger(value) ? value : value.toFixed(2)) : value }}
              </span>
              <pre v-else class="output-json">{{ JSON.stringify(value, null, 2) }}</pre>
            </div>
          </div>
          <div v-else class="output-empty">暂无详细输出</div>
        </n-collapse-item>
      </n-collapse>
    </n-card>

    <!-- 空状态 -->
    <n-card v-if="!result && !generating" size="small" class="empty-card">
      <n-space vertical align="center" :size="12">
        <div style="font-size: 3rem">🎬</div>
        <div style="font-size: 1.1rem; opacity: 0.6">
          输入视频主题，AI 将自动完成：
        </div>
        <n-space :size="8" wrap justify="center">
          <n-tag type="info">✏️ 优化提示词</n-tag>
          <n-tag type="info">📝 智能生成文案</n-tag>
          <n-tag type="info">🎨 AI生成配图</n-tag>
          <n-tag type="info">🎙️ TTS配音</n-tag>
          <n-tag type="info">🎬 自动剪辑合成</n-tag>
          <n-tag type="info">📊 质量评估</n-tag>
        </n-space>
        <div style="font-size: 0.85rem; opacity: 0.4">全程自动化，一键生成完整长视频</div>
      </n-space>
    </n-card>
  </div>
</template>

<style scoped>
.pipeline-panel {
  max-width: 900px;
  margin: 0 auto;
}

.input-card {
  margin-bottom: 16px;
}

.result-card {
  margin-bottom: 16px;
}

.overall-bar {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.result-meta {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.meta-text {
  font-size: 0.82rem;
  opacity: 0.6;
  font-family: monospace;
}

/* 阶段流程图 */
.stage-flow {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0;
  padding: 16px 0;
  align-items: flex-start;
}

.stage-node {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  width: 130px;
  text-align: center;
}

.stage-icon {
  font-size: 1.5rem;
  margin-bottom: 4px;
}

.stage-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  margin: 4px 0;
  border: 2px solid rgba(255,255,255,0.15);
}

.stage-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;
}

.stage-name {
  font-size: 0.78rem;
  font-weight: 600;
  white-space: nowrap;
}

.stage-msg {
  font-size: 0.7rem;
  opacity: 0.65;
  max-width: 120px;
  word-break: break-all;
}

.stage-error {
  font-size: 0.7rem;
  max-width: 120px;
  word-break: break-all;
}

.stage-connector {
  position: absolute;
  top: 30px;
  right: -8px;
  display: flex;
  align-items: center;
  gap: 0;
}

.connector-line {
  width: 24px;
  height: 2px;
  border-radius: 2px;
}

.connector-arrow {
  font-size: 0.7rem;
  opacity: 0.4;
}

/* 暗淡状态 */
.stage-node.status-pending .stage-dot {
  opacity: 0.3;
}
.stage-node.status-pending .stage-name,
.stage-node.status-pending .stage-icon {
  opacity: 0.4;
}

/* 跳过状态 */
.stage-node.status-skipped .stage-dot {
  opacity: 0.5;
}
.stage-node.status-skipped .stage-name {
  text-decoration: line-through;
  opacity: 0.5;
}

/* 失败状态 */
.stage-node.status-failed .stage-icon {
  filter: grayscale(1);
}

/* 详情区 */
.stage-detail {
  padding: 8px 0;
}

.output-item {
  margin-bottom: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: baseline;
}

.output-key {
  font-weight: 600;
  font-size: 0.82rem;
  opacity: 0.7;
  min-width: 120px;
}

.output-value {
  font-size: 0.85rem;
  font-family: monospace;
}

.output-json {
  width: 100%;
  background: rgba(0,0,0,0.2);
  padding: 8px;
  border-radius: 6px;
  font-size: 0.78rem;
  font-family: monospace;
  overflow-x: auto;
  white-space: pre-wrap;
  max-height: 200px;
  overflow-y: auto;
}

.output-empty {
  opacity: 0.4;
  font-size: 0.85rem;
}

.param-group {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.param-label {
  font-size: 0.7rem;
  opacity: 0.6;
  font-weight: 500;
}

.empty-card {
  opacity: 0.85;
}
</style>
