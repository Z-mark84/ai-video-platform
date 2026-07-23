<script setup lang="ts">
import { ref } from 'vue'
import { NConfigProvider, NMessageProvider, darkTheme, NMenu } from 'naive-ui'
import DualChannelInput from './components/prompt/DualChannelInput.vue'
import DrawPanel from './components/draw/DrawPanel.vue'
import AssetPanel from './components/asset/AssetPanel.vue'
import CopywritePanel from './components/copywrite/CopywritePanel.vue'
import TTSPanel from './components/tts/TTSPanel.vue'
import EditPanel from './components/edit/EditPanel.vue'
import CharacterPanel from './components/character/CharacterPanel.vue'
import QualityPanel from './components/quality/QualityPanel.vue'

const currentModule = ref<'m1' | 'm2' | 'm3' | 'm4' | 'm5' | 'm6' | 'm7' | 'm8'>('m8')

const menuOptions = [
  { label: () => 'M1 提示词引擎', key: 'm1', icon: () => '✏️' },
  { label: () => 'M2 AI绘图', key: 'm2', icon: () => '🎨' },
  { label: () => 'M3 素材管理', key: 'm3', icon: () => '📦' },
  { label: () => 'M4 文案生成', key: 'm4', icon: () => '📝' },
  { label: () => 'M5 TTS配音', key: 'm5', icon: () => '🎙️' },
  { label: () => 'M6 智能剪辑', key: 'm6', icon: () => '🎬' },
  { label: () => 'M7 角色一致性', key: 'm7', icon: () => '👤' },
  { label: () => 'M8 质量评估', key: 'm8', icon: () => '📊' },
]
</script>

<template>
  <NConfigProvider :theme="darkTheme">
    <NMessageProvider>
      <div class="app-container">
        <header class="app-header">
          <h1>AI 长视频生成平台</h1>
          <p class="subtitle">{{ currentModule === 'm1' ? 'M1 · 提示词优化引擎' : currentModule === 'm2' ? 'M2 · AI 绘图服务' : currentModule === 'm3' ? 'M3 · 素材管理' : currentModule === 'm4' ? 'M4 · 文案生成' : currentModule === 'm5' ? 'M5 · TTS配音' : currentModule === 'm6' ? 'M6 · 智能剪辑' : currentModule === 'm7' ? 'M7 · 角色一致性' : 'M8 · 质量评估' }}</p>
          <n-menu
            v-model:value="currentModule"
            mode="tabs"
            :options="menuOptions"
            class="module-nav"
          />
        </header>
        <main class="app-main">
          <DualChannelInput v-if="currentModule === 'm1'" />
          <DrawPanel v-else-if="currentModule === 'm2'" />
          <QualityPanel v-else-if="currentModule === 'm8'" />
          <CharacterPanel v-else-if="currentModule === 'm7'" />
          <EditPanel v-else-if="currentModule === 'm6'" />
          <TTSPanel v-else-if="currentModule === 'm5'" />
          <CopywritePanel v-else />
        </main>
        <footer class="app-footer">
          <span>v0.3.0</span>
          <span>M1 提示词引擎 · M2 AI绘图 · M3 素材管理 · M4 文案生成 · M5 TTS配音 · M6 智能剪辑 · M7 角色一致性 · M8 质量评估</span>
        </footer>
      </div>
    </NMessageProvider>
  </NConfigProvider>
</template>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body, #app { height: 100%; }

.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
}

.app-header {
  padding: 16px 0 0;
  text-align: center;
}
.app-header h1 {
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}
.app-header .subtitle {
  font-size: 0.85rem;
  opacity: 0.6;
  margin-top: 2px;
}
.module-nav {
  margin-top: 8px;
  justify-content: center;
}

.app-main {
  flex: 1;
  overflow: auto;
  padding: 12px 0;
}

.app-footer {
  display: flex;
  gap: 16px;
  justify-content: center;
  padding: 10px 0;
  font-size: 0.75rem;
  opacity: 0.5;
  border-top: 1px solid rgba(255,255,255,0.06);
}
</style>
