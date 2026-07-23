<template>
  <div class="tts-panel">
    <div class="panel-header">
      <h2>🎙️ TTS 智能配音</h2>
      <p class="subtitle">M5 · 多声线情感配音引擎</p>
    </div>

    <n-tabs type="line" animated>
      <!-- Tab1: 配音 -->
      <n-tab-pane name="tts" tab="🎤 配音">
        <div class="tts-form">
          <div class="form-row">
            <n-select v-model:value="selectedVoice" :options="voiceOptions" placeholder="选择声线" style="width: 200px" />
            <n-select v-model:value="selectedEmotion" :options="emotionOptions" placeholder="情感" style="width: 140px" />
          </div>

          <n-input
            v-model:value="inputText"
            type="textarea"
            :autosize="{ minRows: 4, maxRows: 10 }"
            placeholder="输入要配音的文本，支持多段落（用空行分隔）"
            clearable
          />

          <div class="params-row">
            <div class="param-item">
              <label>语速</label>
              <n-slider v-model:value="speed" :min="0.5" :max="2.0" :step="0.1" />
              <span class="pv">{{ speed.toFixed(1) }}x</span>
            </div>
            <div class="param-item">
              <label>音调</label>
              <n-slider v-model:value="pitch" :min="-12" :max="12" :step="1" />
              <span class="pv">{{ pitch > 0 ? '+' : '' }}{{ pitch }}</span>
            </div>
          </div>
          <div class="params-row">
            <div class="param-item">
              <label>激昂度</label>
              <n-slider v-model:value="energy" :min="0" :max="1" :step="0.05" />
              <span class="pv">{{ energy.toFixed(2) }}</span>
            </div>
            <div class="param-item">
              <label>语调起伏</label>
              <n-slider v-model:value="intonation" :min="0" :max="1" :step="0.05" />
              <span class="pv">{{ intonation.toFixed(2) }}</span>
            </div>
          </div>

          <n-button type="primary" block size="large" :loading="loading" @click="synthesize" :disabled="!inputText.trim()">
            🔊 生成配音
          </n-button>
        </div>
      </n-tab-pane>

      <!-- Tab2: 结果 -->
      <n-tab-pane name="results" tab="📋 配音结果">
        <div v-if="!lastResult" class="empty">暂无配音结果</div>
        <div v-else class="result-list">
          <div class="result-summary">
            <n-statistic label="总时长" :value="lastResult.total_duration_sec" precision="1" suffix="秒" />
            <n-statistic label="段落" :value="lastResult.segments_audio.length" />
          </div>
          <n-list>
            <n-list-item v-for="seg in lastResult.segments_audio" :key="seg.segment_index">
              <div class="seg-item">
                <div class="seg-header">
                  <n-tag size="tiny">{{ seg.emotion }}</n-tag>
                  <span class="seg-dur">{{ seg.duration_sec }}秒</span>
                  <span class="seg-voice">{{ seg.voice_id }}</span>
                </div>
                <div class="seg-text">{{ seg.text.slice(0, 80) }}{{ seg.text.length > 80 ? '...' : '' }}</div>
                <div class="seg-audio">{{ seg.audio_url }}</div>
              </div>
            </n-list-item>
          </n-list>
        </div>
      </n-tab-pane>

      <!-- Tab3: 声线库 -->
      <n-tab-pane name="voices" tab="🗣️ 声线库">
        <n-grid :cols="2" :x-gap="12" :y-gap="12">
          <n-gi v-for="v in voices" :key="v.id">
            <n-card :title="v.name" size="small" hoverable>
              <div class="voice-meta">
                <n-tag size="tiny">{{ v.gender }}</n-tag>
                <n-tag size="tiny">{{ v.style }}</n-tag>
              </div>
              <div class="voice-emotions">
                <n-tag v-for="e in v.supported_emotions" :key="e" size="tiny" :bordered="false" round>{{ e }}</n-tag>
              </div>
            </n-card>
          </n-gi>
        </n-grid>
      </n-tab-pane>
    </n-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import type { VoiceInfo, TTSJobResult } from '../../api/ttsTypes'
import * as api from '../../api/tts'

const message = useMessage()
const loading = ref(false)
const voices = ref<VoiceInfo[]>([])
const emotionPresets = ref<EmotionPreset[]>([])
const selectedVoice = ref('vo-male-calm-01')
const selectedEmotion = ref('neutral')
const inputText = ref('你有没有想过这样一个问题：为什么有些人轻松赚到百万，而另一些人拼尽全力只能勉强糊口？这不是运气问题，而是系统问题。\n\n今天我们就来揭开这个被称为马太效应的现象背后的底层逻辑。')
const speed = ref(1.0)
const pitch = ref(0)
const energy = ref(0.5)
const intonation = ref(0.5)
const lastResult = ref<TTSJobResult | null>(null)

const voiceOptions = computed(() => voices.value.map(v => ({ label: `${v.name} (${v.gender}/${v.style})`, value: v.id })))
const emotionOptions = computed(() =>
  emotionPresets.value.map(e => ({ label: `${e.name} (${e.emotion})`, value: e.emotion }))
)

async function synthesize() {
  const segments = inputText.value.split('\n\n').filter(Boolean).map((text, i) => ({
    id: `seg-${i}`, text: text.trim(), voice_id: selectedVoice.value, emotion: selectedEmotion.value,
  }))
  loading.value = true
  try {
    lastResult.value = await api.synthesize({
      project_id: 'proj-' + Date.now().toString(36),
      segments, voice_id: selectedVoice.value, pause_between_segments: 0.8,
    })
    message.success(`✅ 配音完成！${lastResult.value.total_duration_sec}秒，${segments.length}段`)
  } catch (e: unknown) {
    message.error(e instanceof Error ? e.message : '配音失败')
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  voices.value = await api.getVoices()
  emotionPresets.value = await api.getEmotionPresets()
})
</script>

<style scoped>
.tts-panel { display: flex; flex-direction: column; gap: 16px; }
.panel-header { text-align: center; }
.panel-header h2 { font-size: 1.4rem; font-weight: 700; }
.tts-form { display: flex; flex-direction: column; gap: 16px; }
.form-row { display: flex; gap: 8px; align-items: center; }
.params-row { display: flex; gap: 24px; }
.param-item { flex: 1; display: flex; align-items: center; gap: 8px; }
.param-item label { font-size: 0.8rem; min-width: 48px; opacity: 0.7; }
.pv { font-family: monospace; min-width: 40px; text-align: right; font-size: 0.85rem; }
.empty { color: #888; text-align: center; padding: 60px; }
.result-summary { display: flex; gap: 24px; margin-bottom: 16px; }
.seg-item { display: flex; flex-direction: column; gap: 4px; padding: 4px 0; }
.seg-header { display: flex; gap: 8px; align-items: center; }
.seg-dur { font-size: 0.75rem; font-family: monospace; opacity: 0.6; }
.seg-voice { font-size: 0.7rem; opacity: 0.5; margin-left: auto; }
.seg-text { font-size: 0.85rem; }
.seg-audio { font-size: 0.7rem; opacity: 0.4; font-family: monospace; }
.voice-meta { display: flex; gap: 6px; margin-bottom: 6px; }
.voice-emotions { display: flex; gap: 4px; flex-wrap: wrap; }
</style>
