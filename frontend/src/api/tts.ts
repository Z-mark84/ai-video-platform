/** M5 TTS配音 - API服务层 */

import type { VoiceInfo, EmotionPreset, TTSJobRequest, TTSJobResult } from './ttsTypes'

const BASE = 'http://localhost:8000/api/v1/tts'

async function req<T>(url: string, opts?: RequestInit): Promise<T> {
  const res = await fetch(url, { headers: { 'Content-Type': 'application/json' }, ...opts })
  if (!res.ok) throw new Error(((await res.json().catch(() => ({}))).detail) || res.statusText)
  return res.json()
}

export async function getVoices(gender?: string, style?: string): Promise<VoiceInfo[]> {
  const p = new URLSearchParams()
  if (gender) p.set('gender', gender); if (style) p.set('style', style)
  return req(`${BASE}/voices?${p}`)
}

export async function getEmotionPresets(): Promise<EmotionPreset[]> {
  return req(`${BASE}/emotion-presets`)
}

export async function synthesize(req: TTSJobRequest): Promise<TTSJobResult> {
  return req(`${BASE}/synthesize`, { method: 'POST', body: JSON.stringify(req) })
}
