<template>
  <div class="dual-channel-panel">
    <!-- 顶部：通道模式切换 + 操作栏 -->
    <div class="toolbar">
      <n-radio-group v-model:value="store.inputChannel" size="small">
        <n-radio-button value="nl">自然语言</n-radio-button>
        <n-radio-button value="tag">标签通道</n-radio-button>
        <n-radio-button value="mixed">混合模式</n-radio-button>
      </n-radio-group>
      <div class="toolbar-actions">
        <n-button quaternary circle size="small" @click="showHistory = !showHistory">
          <template #icon><n-icon><svg viewBox="0 0 24 24" fill="currentColor"><path d="M13 3a9 9 0 0 0-9 9H1l3.89 3.89.07.14L9 12H6c0-3.87 3.13-7 7-7s7 3.13 7 7-3.13 7-7 7c-1.93 0-3.68-.79-4.94-2.06l-1.42 1.42A8.954 8.954 0 0 0 13 21a9 9 0 0 0 0-18zm-1 5v5l4.28 2.54.72-1.21-3.5-2.08V8H12z"/></svg></n-icon></template>
        </n-button>
        <n-button quaternary circle size="small" @click="store.clearAll()">
          <template #icon><n-icon><svg viewBox="0 0 24 24" fill="currentColor"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg></n-icon></template>
        </n-button>
      </div>
    </div>

    <!-- 主区域：双栏布局 -->
    <div class="channel-area">
      <!-- 左栏：自然语言通道 -->
      <div class="channel-left" v-show="store.inputChannel !== 'tag'">
        <div class="channel-header">
          <span class="channel-title">自然语言描述</span>
          <span class="char-count" :class="{ warn: store.inputLength > 1800 }">
            {{ store.inputLength }} / 2000
          </span>
        </div>
        <n-input
          v-model:value="store.inputText"
          type="textarea"
          :autosize="{ minRows: 8, maxRows: 14 }"
          placeholder="输入你的画面描述，例如：一个夕阳下的少女在海边奔跑，氛围压抑而孤独…"
          :maxlength="2000"
          :disabled="store.loading"
          clearable
          class="nl-textarea"
        />
        <div class="channel-footer">
          <n-button
            type="primary"
            :loading="store.loading"
            :disabled="!store.inputText.trim()"
            @click="store.submitNL()"
          >
            解析
          </n-button>
          <n-checkbox v-model:checked="store.preserveLiterary" size="small">
            保留文学性修辞
          </n-checkbox>
        </div>
      </div>

      <!-- 拖拽分割条 -->
      <div class="divider" v-if="store.inputChannel === 'mixed'" />

      <!-- 右栏：标签通道 -->
      <div class="channel-right" v-show="store.inputChannel !== 'nl'">
        <div class="channel-header">
          <span class="channel-title">参数化标签</span>
        </div>

        <!-- 模板快速填充 -->
        <n-collapse :default-expanded-names="['templates']" class="tag-accordion">
          <n-collapse-item title="📋 预设模板" name="templates">
            <div class="template-grid">
              <n-button
                v-for="tpl in store.templates"
                :key="tpl.id"
                size="tiny"
                :type="store.currentTemplate?.id === tpl.id ? 'primary' : 'default'"
                @click="store.applyTemplate(tpl)"
              >
                {{ tpl.name }}
              </n-button>
            </div>
          </n-collapse-item>
        </n-collapse>

        <!-- 标签展示区 -->
        <div class="tags-area">
          <div v-for="[category, tagList] in tagEntries" :key="category" class="tag-group">
            <div class="tag-group-label">{{ categoryLabels[category] || category }}</div>
            <div class="tag-chips">
              <n-tag
                v-for="(tag, idx) in tagList"
                :key="idx"
                closable
                :type="tag.weight >= 1.2 ? 'primary' : tag.weight >= 1.0 ? 'info' : 'default'"
                size="small"
                @close="store.removeTag(category, idx)"
              >
                {{ tag.tag_zh || tag.tag }}
                <span class="tag-weight">×{{ tag.weight }}</span>
              </n-tag>
            </div>
          </div>
          <div v-if="store.tags.size === 0" class="tags-empty">
            在自然语言输入后自动生成标签，或从预设模板选择
          </div>
        </div>
      </div>
    </div>

    <!-- 预览条 -->
    <div class="preview-bar" v-if="store.previewZh || store.lastOutput">
      <n-tabs type="line" animated>
        <n-tab-pane name="zh" tab="中文预览">
          <div class="preview-content">{{ store.previewZh || '暂无预览' }}</div>
        </n-tab-pane>
        <n-tab-pane name="en" tab="英文提示词">
          <div class="preview-content mono">{{ store.lastOutput?.positive_prompt || store.previewEn || '暂无' }}</div>
        </n-tab-pane>
        <n-tab-pane name="negative" tab="反向提示词">
          <div class="preview-content mono">{{ store.lastOutput?.negative_prompt || '标准反向提示词' }}</div>
        </n-tab-pane>
        <n-tab-pane name="params" tab="参数">
          <div class="preview-content mono">
            {{ store.lastOutput ? JSON.stringify(store.lastOutput.params, null, 2) : '—' }}
          </div>
        </n-tab-pane>
      </n-tabs>

      <div class="preview-actions">
        <n-tag v-if="store.confidence > 0" size="small" :type="store.confidence > 0.7 ? 'success' : 'warning'">
          置信度 {{ (store.confidence * 100).toFixed(0) }}%
        </n-tag>
        <n-button
          v-if="store.selectedTags.length > 0"
          size="small"
          type="primary"
          :loading="store.loading"
          @click="store.optimize()"
        >
          完整优化
        </n-button>
        <n-button
          v-if="store.lastOutput"
          size="small"
          @click="copyPrompt()"
        >
          复制提示词
        </n-button>
      </div>
    </div>

    <!-- 历史抽屉 -->
    <n-drawer v-model:show="showHistory" :width="320" placement="right">
      <n-drawer-content title="输入历史">
        <div v-if="store.history.length === 0" class="history-empty">暂无历史记录</div>
        <n-list v-else>
          <n-list-item v-for="(item, idx) in store.history" :key="idx">
            <div class="history-item" @click="restoreHistory(item)">
              <div class="history-text">{{ item.text }}</div>
              <div class="history-time">{{ item.time }}</div>
            </div>
          </n-list-item>
        </n-list>
      </n-drawer-content>
    </n-drawer>

    <!-- 错误提示 -->
    <n-alert v-if="store.error" type="error" closable class="error-alert" @close="store.error = null">
      {{ store.error }}
    </n-alert>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { usePromptStore } from '../../stores/promptStore'

const store = usePromptStore()
const message = useMessage()
const showHistory = ref(false)

const categoryLabels: Record<string, string> = {
  subject: '主体', scene: '场景', light: '光线',
  style: '风格', emotion: '情感', color: '色彩',
  composition: '构图', custom: '自定义',
}

const tagEntries = computed(() => Array.from(store.tags.entries()))

function copyPrompt() {
  if (!store.lastOutput) return
  const text = `Positive: ${store.lastOutput.positive_prompt}\n\nNegative: ${store.lastOutput.negative_prompt}`
  navigator.clipboard.writeText(text).then(() => {
    message.success('已复制到剪贴板')
  }).catch(() => {
    message.warning('复制失败，请手动复制')
  })
}

function restoreHistory(item: { text: string }) {
  store.inputText = item.text
  showHistory.value = false
  store.submitNL()
}

onMounted(() => {
  store.fetchTemplates()
})
</script>

<style scoped>
.dual-channel-panel {
  display: flex;
  flex-direction: column;
  gap: 12px;
  height: 100%;
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 0;
}

.toolbar-actions {
  display: flex;
  gap: 4px;
}

.channel-area {
  display: flex;
  gap: 12px;
  flex: 1;
  min-height: 0;
}

.channel-left, .channel-right {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
}

.divider {
  width: 4px;
  background: rgba(99, 102, 241, 0.15);
  border-radius: 2px;
  cursor: col-resize;
}

.channel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.channel-title {
  font-weight: 600;
  font-size: 0.9rem;
}

.char-count {
  font-size: 0.75rem;
  color: #888;
}
.char-count.warn {
  color: #f59e0b;
}

.nl-textarea :deep(textarea) {
  line-height: 1.7;
  font-size: 0.95rem;
}

.channel-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tag-accordion {
  margin-bottom: 8px;
}

.template-grid {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.tags-area {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tag-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.tag-group-label {
  font-size: 0.78rem;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.tag-chips {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.tag-weight {
  font-size: 0.7rem;
  opacity: 0.7;
  margin-left: 2px;
}

.tags-empty {
  color: #888;
  font-size: 0.85rem;
  padding: 20px;
  text-align: center;
}

.preview-bar {
  border-top: 1px solid #eee;
  padding-top: 8px;
  margin-top: 4px;
}

.preview-content {
  font-size: 0.85rem;
  line-height: 1.6;
  max-height: 120px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-all;
}
.preview-content.mono {
  font-family: 'GeistMono', 'SF Mono', monospace;
  font-size: 0.8rem;
}

.preview-actions {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-top: 8px;
}

.history-item {
  cursor: pointer;
  padding: 4px 0;
}
.history-item:hover {
  opacity: 0.8;
}
.history-text {
  font-size: 0.85rem;
  margin-bottom: 2px;
}
.history-time {
  font-size: 0.7rem;
  color: #888;
}
.history-empty {
  color: #888;
  text-align: center;
  padding: 40px;
}

.error-alert {
  position: fixed;
  bottom: 20px;
  right: 20px;
  max-width: 400px;
}
</style>
