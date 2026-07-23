<template>
  <div class="quality-panel">
    <div class="panel-header">
      <h2>📊 质量评估</h2>
      <p class="subtitle">M8 · AI素材自动化质量检测引擎</p>
    </div>

    <n-tabs type="line" animated>
      <!-- Tab1: 评估 -->
      <n-tab-pane name="eval" tab="🔬 质量检测">
        <div class="eval-form">
          <n-input v-model:value="taskId" placeholder="任务ID（可选，自动生成）" clearable />
          <n-select v-model:value="taskType" :options="typeOpts" style="width:160px" />
          <n-button type="primary" block :loading="loading" @click="runEval">
            🔍 运行质量评估
          </n-button>
        </div>

        <div v-if="lastReport" class="report">
          <n-divider />
          <div class="scores-row">
            <div class="score-item" :class="{ pass: lastReport.scores.passed }">
              <div class="score-label">LPIPS</div>
              <div class="score-val">{{ lastReport.scores.lpips_avg }}</div>
              <div class="score-threshold">阈值 ≤0.15</div>
            </div>
            <div class="score-item" :class="{ pass: lastReport.scores.passed }">
              <div class="score-label">CLIP Score</div>
              <div class="score-val">{{ lastReport.scores.clip_score_avg }}</div>
              <div class="score-threshold">阈值 ≥0.75</div>
            </div>
            <div class="score-item">
              <div class="score-label">光流平滑</div>
              <div class="score-val">{{ lastReport.scores.optical_flow_smoothness }}</div>
            </div>
          </div>

          <n-alert :type="lastReport.scores.passed ? 'success' : 'warning'">
            {{ lastReport.summary }}
          </n-alert>

          <n-list v-if="lastReport.suggestions.length">
            <n-list-item v-for="(s, i) in lastReport.suggestions" :key="i">
              {{ s }}
            </n-list-item>
          </n-list>
        </div>
      </n-tab-pane>

      <!-- Tab2: 反馈 -->
      <n-tab-pane name="feedback" tab="⭐ 用户反馈">
        <div v-if="feedbackStats">
          <div class="stats-row">
            <n-statistic label="总反馈数" :value="feedbackStats.total" />
            <n-statistic label="平均评分" :value="feedbackStats.avg_rating" precision="2" />
          </div>
        </div>
        <n-divider />
        <div class="feedback-form">
          <n-input v-model:value="fbTaskId" placeholder="任务ID" />
          <n-rate v-model:value="fbRating" count="5" />
          <n-input v-model:value="fbComment" type="textarea" :autosize="{ minRows: 2, maxRows: 4 }" placeholder="评价（可选）" />
          <n-button type="primary" @click="submitFb" :disabled="!fbTaskId">提交评分</n-button>
        </div>
      </n-tab-pane>
    </n-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import type { QualityReport, FeedbackStats } from '../../api/qualityTypes'
import * as api from '../../api/quality'

const message = useMessage()
const loading = ref(false)
const taskId = ref('')
const taskType = ref('text2img')
const lastReport = ref<QualityReport | null>(null)
const feedbackStats = ref<FeedbackStats | null>(null)
const fbTaskId = ref('')
const fbRating = ref(5)
const fbComment = ref('')

const typeOpts = [
  { label: '文生图', value: 'text2img' },
  { label: '图生图', value: 'img2img' },
  { label: '视频', value: 'video' },
]

async function runEval() {
  loading.value = true
  try {
    lastReport.value = await api.evaluate({
      task_id: taskId.value || `task-${Date.now().toString(36)}`,
      project_id: 'demo',
      image_urls: [],
      prompt_text: null,
      task_type: taskType.value,
    })
    message.success(lastReport.value.scores.passed ? '✅ 质量达标' : '⚠️ 需优化')
  } catch (e: unknown) {
    message.error(e instanceof Error ? e.message : '评估失败')
  } finally {
    loading.value = false
  }
}

async function submitFb() {
  try {
    await api.submitFeedback(fbTaskId.value, fbRating.value, fbComment.value)
    message.success('✅ 评分已提交')
    feedbackStats.value = await api.getFeedbackStats()
  } catch (e: unknown) {
    message.error(e instanceof Error ? e.message : '提交失败')
  }
}

onMounted(async () => {
  try { feedbackStats.value = await api.getFeedbackStats() } catch {}
})
</script>

<style scoped>
.quality-panel { display: flex; flex-direction: column; gap: 16px; }
.panel-header { text-align: center; }
.panel-header h2 { font-size: 1.4rem; font-weight: 700; }
.eval-form { display: flex; flex-direction: column; gap: 12px; }
.report { display: flex; flex-direction: column; gap: 12px; }
.scores-row { display: flex; gap: 16px; justify-content: center; }
.score-item { text-align: center; padding: 16px; background: rgba(99,102,241,0.05); border-radius: 8px; min-width: 120px; border: 1px solid rgba(99,102,241,0.1); }
.score-item.pass { border-color: #10b981; }
.score-label { font-size: 0.75rem; opacity: 0.7; text-transform: uppercase; }
.score-val { font-size: 1.5rem; font-weight: 700; font-family: monospace; margin: 4px 0; }
.score-threshold { font-size: 0.65rem; opacity: 0.5; }
.stats-row { display: flex; gap: 24px; }
.feedback-form { display: flex; flex-direction: column; gap: 12px; }
</style>
