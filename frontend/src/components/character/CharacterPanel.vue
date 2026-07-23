<template>
  <div class="char-panel">
    <div class="panel-header">
      <h2>👤 角色一致性管理</h2>
      <p class="subtitle">M7 · 跨镜头角色外貌保持</p>
    </div>

    <n-tabs type="line" animated>
      <!-- Tab1: 角色创建 -->
      <n-tab-pane name="create" tab="➕ 创建角色">
        <div class="create-form">
          <n-input v-model:value="charName" placeholder="角色名称" size="large" />
          <div class="form-row">
            <n-select v-model:value="gender" :options="genderOpts" style="width:120px" />
            <n-select v-model:value="ageRange" :options="ageOpts" style="width:120px" />
            <n-select v-model:value="style" :options="styleOpts" style="width:120px" />
          </div>
          <n-input v-model:value="outfit" placeholder="默认服饰描述" clearable />
          <n-button type="primary" block :loading="loading" @click="createChar" :disabled="!charName.trim()">
            🎭 创建角色
          </n-button>
        </div>
      </n-tab-pane>

      <!-- Tab2: 角色库 -->
      <n-tab-pane name="library" tab="📚 角色库">
        <div v-if="chars.length === 0" class="empty">暂无角色</div>
        <n-grid :cols="2" :x-gap="12" :y-gap="12" v-else>
          <n-gi v-for="c in chars" :key="c.id">
            <n-card :title="c.name" size="small" hoverable>
              <div class="char-body">
                <div class="char-tags">
                  <n-tag size="tiny">{{ c.attributes.gender }}</n-tag>
                  <n-tag size="tiny">{{ c.attributes.age_range }}</n-tag>
                  <n-tag size="tiny">{{ c.attributes.style }}</n-tag>
                </div>
                <div class="char-meta">
                  <span>使用 {{ c.usage_count }} 次</span>
                  <n-tag v-if="c.face_similarity" size="tiny" :type="c.face_similarity >= 0.85 ? 'success' : 'warning'">
                    {{ (c.face_similarity * 100).toFixed(0) }}% 一致
                  </n-tag>
                </div>
                <div v-if="c.tags.length" class="char-tags-list">
                  <n-tag v-for="t in c.tags" :key="t" size="tiny" round :bordered="false">{{ t }}</n-tag>
                </div>
              </div>
              <template #action>
                <n-button size="tiny" @click="checkChar(c.id)">检测一致性</n-button>
              </template>
            </n-card>
          </n-gi>
        </n-grid>

        <n-modal v-model:show="showScore" title="一致性评分">
          <div class="score-modal" v-if="scoreResult">
            <n-progress type="circle" :percentage="Math.round(scoreResult.score * 100)" :status="scoreResult.passed ? 'success' : 'warning'" />
            <div class="score-detail">{{ scoreResult.details.recommendation as string }}</div>
          </div>
        </n-modal>
      </n-tab-pane>
    </n-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import type { CharacterInfo, ConsistencyScore } from '../../api/characterTypes'
import * as api from '../../api/character'

const message = useMessage()
const loading = ref(false)
const chars = ref<CharacterInfo[]>([])
const charName = ref('')
const gender = ref('male')
const ageRange = ref('25-30')
const style = ref('写实')
const outfit = ref('')

const showScore = ref(false)
const scoreResult = ref<ConsistencyScore | null>(null)

const genderOpts = [
  { label: '男性', value: 'male' }, { label: '女性', value: 'female' }, { label: '中性', value: 'neutral' },
]
const ageOpts = [
  { label: '少年(10-18)', value: '10-18' }, { label: '青年(20-30)', value: '20-30' },
  { label: '中年(35-50)', value: '35-50' }, { label: '老年(55-70)', value: '55-70' },
]
const styleOpts = [
  { label: '写实', value: '写实' }, { label: '二次元', value: '二次元' }, { label: '油画', value: '油画' },
]

async function createChar() {
  loading.value = true
  try {
    const c = await api.createCharacter({
      name: charName.value, gender: gender.value, age_range: ageRange.value,
      style: style.value, default_outfit: outfit.value, tags: ['自定义'],
    })
    chars.value.unshift(c)
    message.success(`✅ 角色已创建: ${c.name}`)
    charName.value = ''
  } catch (e: unknown) {
    message.error(e instanceof Error ? e.message : '创建失败')
  } finally {
    loading.value = false
  }
}

async function checkChar(id: string) {
  try {
    scoreResult.value = await api.checkConsistency(id)
    showScore.value = true
  } catch (e: unknown) {
    message.error(e instanceof Error ? e.message : '检测失败')
  }
}

onMounted(async () => {
  try { chars.value = await api.getCharacters() } catch {}
})
</script>

<style scoped>
.char-panel { display: flex; flex-direction: column; gap: 16px; }
.panel-header { text-align: center; }
.panel-header h2 { font-size: 1.4rem; font-weight: 700; }
.create-form { display: flex; flex-direction: column; gap: 12px; }
.form-row { display: flex; gap: 8px; }
.empty { color: #888; text-align: center; padding: 60px; }
.char-body { display: flex; flex-direction: column; gap: 8px; }
.char-tags { display: flex; gap: 4px; }
.char-meta { display: flex; justify-content: space-between; font-size: 0.8rem; opacity: 0.7; }
.char-tags-list { display: flex; gap: 4px; flex-wrap: wrap; }
.score-modal { display: flex; flex-direction: column; align-items: center; gap: 16px; padding: 24px; }
.score-detail { font-size: 1rem; }
</style>
