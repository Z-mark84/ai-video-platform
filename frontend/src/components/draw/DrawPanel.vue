<template>
  <div class="draw-panel">
    <div class="panel-header">
      <h2>🎨 AI 绘图服务</h2>
      <p class="subtitle">M2 · 文生图 / 图生图双管线</p>
    </div>

    <n-tabs type="line" animated :default-value="'txt2img'">
      <!-- Tab 1: 文生图 -->
      <n-tab-pane name="txt2img" tab="📝 文生图">
        <div class="render-form">
          <div class="form-row">
            <div class="form-group flex-1">
              <label>正向提示词</label>
              <n-input
                v-model:value="positivePrompt"
                type="textarea"
                :autosize="{ minRows: 4, maxRows: 8 }"
                placeholder="从M1复制优化后的正向提示词，或手动输入"
                clearable
              />
            </div>
            <div class="form-group flex-1">
              <label>反向提示词</label>
              <n-input
                v-model:value="negativePrompt"
                type="textarea"
                :autosize="{ minRows: 4, maxRows: 8 }"
                placeholder="从M1复制反向提示词"
                clearable
              />
            </div>
          </div>

          <div class="form-row params-row">
            <n-input-number v-model:value="width" :min="512" :max="3840" :step="64">
              <template #prefix>宽</template>
            </n-input-number>
            <n-input-number v-model:value="height" :min="512" :max="3840" :step="64">
              <template #prefix>高</template>
            </n-input-number>
            <n-input-number v-model:value="steps" :min="1" :max="150" :step="5">
              <template #prefix>步数</template>
            </n-input-number>
            <n-input-number v-model:value="cfgScale" :min="1" :max="30" :step="0.5">
              <template #prefix>CFG</template>
            </n-input-number>
            <n-input-number v-model:value="batchCount" :min="1" :max="30">
              <template #prefix>张数</template>
            </n-input-number>
          </div>

          <div class="form-row">
            <n-select
              v-model:value="selectedPipeline"
              :options="pipelineOptions"
              placeholder="选择管线"
              style="width: 240px"
            />
            <n-select
              v-model:value="selectedClassification"
              :options="classificationOptions"
              placeholder="画面分类"
              style="width: 160px"
            />
            <!-- 从M1加载按钮 -->
            <n-button @click="loadFromM1" :disabled="!hasM1Output">
              <template #icon><n-icon><svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 4V1L8 5l4 4V6c3.31 0 6 2.69 6 6 0 1.01-.25 1.97-.7 2.8l1.46 1.46C19.54 15.03 20 13.57 20 12c0-4.42-3.58-8-8-8zm0 14c-3.31 0-6-2.69-6-6 0-1.01.25-1.97.7-2.8L5.24 7.74C4.46 8.97 4 10.43 4 12c0 4.42 3.58 8 8 8v3l4-4-4-4v3z"/></svg></n-icon></template>
              从M1加载
            </n-button>
          </div>

          <n-button
            type="primary"
            size="large"
            block
            :loading="loading"
            :disabled="!positivePrompt.trim()"
            @click="submitRender"
          >
            🚀 生成图片
          </n-button>
        </div>
      </n-tab-pane>

      <!-- Tab 2: 图生图 -->
      <n-tab-pane name="img2img" tab="🖼️ 图生图">
        <div class="img2img-form">
          <div class="upload-area">
            <n-upload
              multiple
              :default-upload="false"
              list-type="image-card"
              @change="handleUploadChange"
            >
              <n-upload-dragger>
                <div class="upload-hint">
                  <n-icon size="48"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/></svg></n-icon>
                  <p>拖拽或点击上传参考图片</p>
                  <p class="upload-note">支持 JPG/PNG，单张≤20MB</p>
                </div>
              </n-upload-dragger>
            </n-upload>
          </div>

          <div class="form-row">
            <n-input-number v-model:value="denoisingStrength" :min="0.1" :max="0.95" :step="0.05" style="width: 220px">
              <template #prefix>重绘强度</template>
            </n-input-number>
            <n-slider v-model:value="denoisingStrength" :min="0.1" :max="0.95" :step="0.05" style="width: 200px" />
            <span class="param-value">{{ denoisingStrength.toFixed(2) }}</span>
          </div>

          <n-input
            v-model:value="img2imgPrompt"
            type="textarea"
            :autosize="{ minRows: 3, maxRows: 6 }"
            placeholder="输入图生图的提示词（可选，为空则自动提取原图特征）"
            clearable
          />

          <n-button
            type="primary"
            size="large"
            block
            :loading="loading"
            @click="submitImg2Img"
          >
            🎨 图生图生成
          </n-button>
        </div>
      </n-tab-pane>

      <!-- Tab 3: 任务历史 -->
      <n-tab-pane name="history" tab="📋 生成历史">
        <div v-if="completedTasks.length === 0 && pendingTasks.length === 0" class="history-empty">
          暂无生成记录。先提交一个文生图任务吧。
        </div>

        <n-list v-else>
          <n-list-item v-for="task in allTasks" :key="task.task_id">
            <template #prefix>
              <n-tag :type="task.status === 'completed' ? 'success' : 'warning'" size="small">
                {{ task.status }}
              </n-tag>
            </template>
            <div class="task-item">
              <div class="task-id">ID: {{ task.task_id }}</div>
              <div class="task-meta">
                {{ task.total_count }}张 | {{ task.created_at.slice(0, 19).replace('T', ' ') }}
              </div>
              <div v-if="task.results.length" class="task-results">
                <n-image-group>
                  <n-image
                    v-for="(url, idx) in task.results"
                    :key="idx"
                    :src="url"
                    :alt="`生成图${idx+1}`"
                    width="120"
                    :preview-disabled="!url.startsWith('http')"
                    class="result-thumb"
                  />
                </n-image-group>
              </div>
              <div v-if="task.error" class="task-error">{{ task.error }}</div>
            </div>
          </n-list-item>
        </n-list>
      </n-tab-pane>
    </n-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { useDrawStore } from '../../stores/drawStore'
import { usePromptStore } from '../../stores/promptStore'

const drawStore = useDrawStore()
const promptStore = usePromptStore()
const message = useMessage()

// 文生图参数
const positivePrompt = ref('')
const negativePrompt = ref('')
const width = ref(1920)
const height = ref(1080)
const steps = ref(30)
const cfgScale = ref(7.0)
const batchCount = ref(4)
const selectedPipeline = ref('mock-dev')
const selectedClassification = ref('scene')

// 图生图参数
const img2imgPrompt = ref('')
const denoisingStrength = ref(0.75)

// 管线选择
const pipelineOptions = computed(() =>
  drawStore.pipelines.map(p => ({ label: p.name, value: p.id }))
)
const classificationOptions = [
  { label: '🎬 场景', value: 'scene' },
  { label: '👤 人物', value: 'character' },
  { label: '🌌 融合', value: 'fusion' },
]

const loading = computed(() => drawStore.loading)
const allTasks = computed(() => [...drawStore.pendingTasks, ...drawStore.completedTasks])
const completedTasks = computed(() => drawStore.completedTasks)
const pendingTasks = computed(() => drawStore.pendingTasks)
const hasM1Output = computed(() => !!promptStore.lastOutput)

function loadFromM1() {
  const out = promptStore.lastOutput
  if (!out) {
    message.warning('M1 还没有优化结果，先去 M1 生成提示词')
    return
  }
  positivePrompt.value = out.positive_prompt
  negativePrompt.value = out.negative_prompt
  steps.value = out.params.steps as number || 30
  cfgScale.value = out.params.cfg_scale as number || 7.0
  selectedClassification.value = out.classification
  message.success('已从M1加载提示词')
}

async function submitRender() {
  const task = await drawStore.submitRender({
    project_id: `proj-${Date.now().toString(36)}`,
    prompt_id: '',
    positive_prompt: positivePrompt.value,
    negative_prompt: negativePrompt.value,
    params: { width: width.value, height: height.value, steps: steps.value, cfg_scale: cfgScale.value },
    classification: selectedClassification.value,
    count: batchCount.value,
    reference_images: [],
    denoising_strength: 0.75,
  })
  if (task) {
    message.success(`✅ 生成完成！共 ${task.total_count} 张`)
  }
}

async function submitImg2Img() {
  message.info('图生图模式需要上传参考图片后调用 (当前Mock模式)')
}

function handleUploadChange() {
  message.success('图片已上传')
}

onMounted(() => {
  drawStore.fetchPipelines()
})
</script>

<style scoped>
.draw-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.panel-header {
  text-align: center;
  padding-bottom: 8px;
}
.panel-header h2 {
  font-size: 1.4rem;
  font-weight: 700;
}

.render-form, .img2img-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-row {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.form-group label {
  font-size: 0.8rem;
  opacity: 0.7;
}
.flex-1 { flex: 1; min-width: 200px; }

.params-row {
  gap: 8px;
}
.params-row > * {
  width: 120px;
}

.upload-area {
  border: 2px dashed #444;
  border-radius: 8px;
  padding: 24px;
  text-align: center;
}
.upload-hint p {
  margin-top: 8px;
  opacity: 0.7;
}
.upload-note {
  font-size: 0.75rem;
  opacity: 0.5;
}

.param-value {
  font-family: monospace;
  font-size: 1.1rem;
  min-width: 40px;
  text-align: center;
}

.history-empty {
  color: #888;
  text-align: center;
  padding: 60px 20px;
}

.task-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.task-id {
  font-family: monospace;
  font-size: 0.75rem;
  opacity: 0.6;
}
.task-meta {
  font-size: 0.8rem;
  opacity: 0.7;
}
.task-results {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 4px;
}
.result-thumb {
  border-radius: 4px;
  border: 1px solid #333;
}
.task-error {
  color: #ef4444;
  font-size: 0.8rem;
}
</style>
