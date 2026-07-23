<template>
  <div class="edit-panel">
    <div class="panel-header">
      <h2>🎬 智能剪辑</h2>
      <p class="subtitle">M6 · 自动视频合成引擎</p>
    </div>

    <n-tabs type="line" animated>
      <!-- Tab1: 创建项目 -->
      <n-tab-pane name="create" tab="🎞️ 新建项目">
        <div class="create-form">
          <n-input v-model:value="projectName" placeholder="视频项目名称" size="large" />
          <n-divider />

          <div class="segment-list">
            <div v-for="(seg, idx) in segments" :key="idx" class="segment-item">
              <div class="seg-header">
                <n-tag size="tiny">片段{{ idx + 1 }}</n-tag>
                <n-button size="tiny" quaternary @click="removeSeg(idx)" v-if="segments.length > 1">✕</n-button>
              </div>
              <n-input v-model:value="seg.subtitle_text" type="textarea" :autosize="{ minRows: 2, maxRows: 4 }" placeholder="字幕文本" />
              <div class="seg-params">
                <n-input-number v-model:value="seg.duration_sec" :min="1" :max="60" size="small" style="width:100px">
                  <template #prefix>时长</template>
                </n-input-number>
                <n-select v-model:value="seg.transition" :options="transitionOpts" size="small" style="width:120px" />
              </div>
            </div>
          </div>

          <n-button dashed block @click="addSegment">+ 添加片段</n-button>
          <n-divider />
          <div class="total-info">共 {{ segments.length }} 片段 · 约 {{ totalDuration }} 秒</div>
          <n-button type="primary" block size="large" :loading="loading" @click="createProj" :disabled="!projectName.trim()">
            🚀 创建项目
          </n-button>
        </div>
      </n-tab-pane>

      <!-- Tab2: 项目列表 -->
      <n-tab-pane name="list" tab="📋 项目列表">
        <div v-if="projects.length === 0" class="empty">暂无项目</div>
        <n-list v-else>
          <n-list-item v-for="p in projects" :key="p.id">
            <div class="proj-item">
              <strong>{{ p.name }}</strong>
              <div class="proj-meta">{{ p.timeline.length }}片段 · {{ p.status }}</div>
              <n-button size="tiny" @click="selectProject(p)">渲染</n-button>
            </div>
          </n-list-item>
        </n-list>
      </n-tab-pane>

      <!-- Tab3: 渲染 -->
      <n-tab-pane name="render" tab="⚙️ 渲染">
        <div v-if="!selectedProj" class="empty">请先在项目列表中选择项目</div>
        <div v-else>
          <div class="render-info">
            <n-statistic label="项目" :value="selectedProj.name" />
            <n-statistic label="片段" :value="selectedProj.timeline.length" />
          </div>
          <n-button type="primary" block :loading="rendering" @click="startRender">🎬 开始渲染</n-button>
          <div v-if="renderResult" class="render-result">
            <n-alert :type="renderResult.status === 'completed' ? 'success' : 'warning'">
              {{ renderResult.status === 'completed' ? '渲染完成！' : renderResult.status }}
            </n-alert>
            <div class="output-info" v-if="renderResult.output_url">
              输出路径: {{ renderResult.output_url }}
              <n-tag>1080p MP4</n-tag>
            </div>
          </div>
        </div>
      </n-tab-pane>
    </n-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import type { TimelineSegment, VideoProject, RenderProgress } from '../../api/editTypes'
import * as api from '../../api/edit'

const message = useMessage()
const loading = ref(false)
const rendering = ref(false)
const projectName = ref('认知科普视频')
const projects = ref<VideoProject[]>([])
const selectedProj = ref<VideoProject | null>(null)
const renderResult = ref<RenderProgress | null>(null)

const segments = ref<Array<{ subtitle_text: string; duration_sec: number; transition: string }>>([
  { subtitle_text: '你有没有想过，为什么有些人赚钱那么容易？', duration_sec: 8, transition: 'fade' },
  { subtitle_text: '这背后有一个叫做「复利效应」的底层逻辑。', duration_sec: 10, transition: 'fade' },
  { subtitle_text: '爱因斯坦曾说过，复利是世界第八大奇迹。', duration_sec: 12, transition: 'dissolve' },
])

const transitionOpts = [
  { label: '淡入淡出', value: 'fade' },
  { label: '硬切', value: 'cut' },
  { label: '交叉溶解', value: 'dissolve' },
]

const totalDuration = computed(() => segments.value.reduce((s, seg) => s + seg.duration_sec, 0).toFixed(1))

function addSegment() {
  segments.value.push({ subtitle_text: '', duration_sec: 6, transition: 'fade' })
}
function removeSeg(idx: number) {
  segments.value.splice(idx, 1)
}

async function createProj() {
  loading.value = true
  try {
    const p = await api.createProject({
      project_name: projectName.value,
      segments: segments.value.map((s, i) => ({
        image_url: `/mock/assets/scene_${(i % 5) + 1}.png`,
        audio_url: `/mock/tts/seg_${i}.wav`,
        subtitle_text: s.subtitle_text,
        duration_sec: s.duration_sec,
        transition: s.transition,
        scene_description: '',
      })),
    })
    projects.value.unshift(p)
    message.success(`✅ 项目已创建: ${p.name}`)
  } catch (e: unknown) {
    message.error(e instanceof Error ? e.message : '创建失败')
  } finally {
    loading.value = false
  }
}

function selectProject(p: VideoProject) {
  selectedProj.value = p
  renderResult.value = null
}

async function startRender() {
  if (!selectedProj.value) return
  rendering.value = true
  try {
    renderResult.value = await api.renderProject(selectedProj.value.id)
    message.success('✅ 渲染完成！')
  } catch (e: unknown) {
    message.error(e instanceof Error ? e.message : '渲染失败')
  } finally {
    rendering.value = false
  }
}

onMounted(async () => {
  try { projects.value = await api.getProjects() } catch {}
})
</script>

<style scoped>
.edit-panel { display: flex; flex-direction: column; gap: 16px; }
.panel-header { text-align: center; }
.panel-header h2 { font-size: 1.4rem; font-weight: 700; }
.create-form { display: flex; flex-direction: column; gap: 8px; }
.segment-list { display: flex; flex-direction: column; gap: 8px; max-height: 400px; overflow-y: auto; }
.segment-item { background: rgba(99,102,241,0.04); border-radius: 8px; padding: 8px; border: 1px solid rgba(99,102,241,0.1); }
.seg-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
.seg-params { display: flex; gap: 8px; margin-top: 4px; }
.total-info { text-align: center; font-size: 0.85rem; opacity: 0.7; }
.empty { color: #888; text-align: center; padding: 60px; }
.proj-item { display: flex; align-items: center; gap: 12px; }
.proj-meta { font-size: 0.8rem; opacity: 0.6; flex: 1; }
.render-info { display: flex; gap: 24px; margin-bottom: 16px; }
.render-result { margin-top: 16px; }
.output-info { margin-top: 8px; font-size: 0.85rem; display: flex; align-items: center; gap: 8px; }
</style>
