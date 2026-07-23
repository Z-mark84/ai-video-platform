/** M5 TTS配音 - API类型定义 */

export interface VoiceInfo {
  id: string; name: string; gender: string; style: string
  provider: string; language: string; supported_emotions: string[]
  is_active: boolean
}

export interface EmotionPreset {
  id: string; name: string; emotion: string
  is_system: boolean
}

export interface TTSJobRequest {
  project_id: string
  segments: Array<{ id: string; text: string; voice_id?: string; emotion?: string }>
  voice_id: string
  pause_between_segments: number
}

export interface TTSJobResult {
  job_id: string; project_id: string
  segments_audio: Array<{ segment_index: number; text: string; voice_id: string; emotion: string; duration_sec: number; audio_url: string }>
  total_duration_sec: number; status: string
}
