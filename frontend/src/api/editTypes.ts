/** M6 智能剪辑 - API类型定义 */

export interface TimelineSegment {
  seq: number; image_url: string; audio_url: string
  subtitle_text: string; duration_sec: number
  transition: string; scene_description: string
}

export interface VideoProject {
  id: string; name: string
  timeline: TimelineSegment[]
  global_settings: GlobalSettings
  status: string; created_at: string
}

export interface GlobalSettings {
  brightness_delta: number; saturation_delta: number
  bgm_id: string; bgm_volume_db: number; voice_volume_db: number
  subtitle_style: string; resolution: string; fps: number
}

export interface RenderProgress {
  project_id: string; progress: number
  status: string; output_url: string | null
}

export interface EditingRequest {
  project_name: string
  segments: Array<{
    image_url: string; audio_url: string; subtitle_text: string
    duration_sec: number; transition: string; scene_description: string
  }>
}
