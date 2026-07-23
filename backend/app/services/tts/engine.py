"""M5 TTS配音 - 引擎服务（Mock模式）

模拟ChatTTS/CosyVoice的TTS生成过程。
支持：多声线选择、情感参数调节、批量分段配音。
"""

from __future__ import annotations
import uuid
import random
from datetime import datetime
from typing import Optional

from app.models.tts import (
    VoiceInfo, EmotionParams, EmotionPreset,
    TTSJobRequest, TTSJobResult, TTSJob,
)

# ============================================================
# 内置声线库
# ============================================================
_BUILTIN_VOICES: list[VoiceInfo] = [
    VoiceInfo(id="vo-male-calm-01", name="沉稳男声", provider="mock", gender="male",
              style="documentary", supported_emotions=["neutral", "calm", "serious", "warm"]),
    VoiceInfo(id="vo-female-warm-01", name="温暖女声", provider="mock", gender="female",
              style="story", supported_emotions=["neutral", "happy", "warm", "sad"]),
    VoiceInfo(id="vo-male-narrative-01", name="叙事男声", provider="mock", gender="male",
              style="normal", supported_emotions=["neutral", "calm", "serious", "inspiring"]),
    VoiceInfo(id="vo-female-news-01", name="新闻女声", provider="mock", gender="female",
              style="news", supported_emotions=["neutral", "serious"]),
    VoiceInfo(id="vo-male-enthu-01", name="激昂男声", provider="mock", gender="male",
              style="normal", supported_emotions=["happy", "excited", "angry", "inspiring"]),
    VoiceInfo(id="vo-kid-cute-01", name="可爱童声", provider="mock", gender="neutral",
              style="story", supported_emotions=["happy", "sad", "surprised"]),
]

# ============================================================
# 内置情感预设
# ============================================================
_BUILTIN_EMOTION_PRESETS: list[EmotionPreset] = [
    EmotionPreset(id="emo-neutral", name="平静", emotion="neutral",
                  params=EmotionParams(speed=1.0, pitch=0, volume=1.0, energy=0.3, intonation=0.3)),
    EmotionPreset(id="emo-happy", name="欢快", emotion="happy",
                  params=EmotionParams(speed=1.2, pitch=2, volume=1.1, energy=0.7, intonation=0.7)),
    EmotionPreset(id="emo-sad", name="悲伤", emotion="sad",
                  params=EmotionParams(speed=0.85, pitch=-2, volume=0.85, energy=0.2, intonation=0.2)),
    EmotionPreset(id="emo-angry", name="愤怒", emotion="angry",
                  params=EmotionParams(speed=1.3, pitch=-1, volume=1.3, energy=0.9, intonation=0.8)),
    EmotionPreset(id="emo-calm", name="沉稳", emotion="calm",
                  params=EmotionParams(speed=0.9, pitch=-1, volume=0.9, energy=0.2, intonation=0.2)),
    EmotionPreset(id="emo-inspiring", name="鼓舞", emotion="inspiring",
                  params=EmotionParams(speed=1.1, pitch=1, volume=1.2, energy=0.8, intonation=0.6)),
]


class MockTTSEngine:
    """Mock TTS引擎（模拟配音）"""

    def __init__(self):
        self._voices = list(_BUILTIN_VOICES)
        self._presets = list(_BUILTIN_EMOTION_PRESETS)
        self._jobs: dict[str, TTSJob] = {}

    # ---- 声线管理 ----

    def get_voices(self, gender: str | None = None, style: str | None = None) -> list[VoiceInfo]:
        items = self._voices
        if gender:
            items = [v for v in items if v.gender == gender]
        if style:
            items = [v for v in items if v.style == style]
        return items

    def get_voice(self, voice_id: str) -> VoiceInfo | None:
        for v in self._voices:
            if v.id == voice_id:
                return v
        return None

    # ---- 情感预设 ----

    def get_emotion_presets(self) -> list[EmotionPreset]:
        return self._presets

    def get_emotion_preset(self, preset_id: str) -> EmotionPreset | None:
        for p in self._presets:
            if p.id == preset_id:
                return p
        return None

    # ---- 配音任务 ----

    def synthesize(self, req: TTSJobRequest) -> TTSJobResult:
        """批量分段配音"""
        job_id = f"tts-{uuid.uuid4().hex[:12]}"
        segments_audio = []
        total_duration = 0.0

        for i, seg in enumerate(req.segments):
            text = seg.get("text", "")
            voice_id = seg.get("voice_id", req.voice_id)
            emotion = seg.get("emotion", "neutral")

            # 模拟配音时长：按字数估算，约3.5字/秒
            word_count = len(text)
            duration = word_count / 3.5
            # 添加情感和语速影响
            emotion_params = next((p.params for p in self._presets if p.emotion == emotion), None)
            if emotion_params:
                duration = duration / emotion_params.speed  # 语速越快，时长越短

            audio_info = {
                "segment_index": i,
                "segment_id": seg.get("id", f"seg-{i}"),
                "text": text,
                "voice_id": voice_id,
                "emotion": emotion,
                "duration_sec": round(duration, 2),
                "audio_url": f"/mock/tts/{job_id}/seg_{i}.wav",
                "word_count": word_count,
            }
            segments_audio.append(audio_info)
            total_duration += duration + req.pause_between_segments

        result = TTSJobResult(
            job_id=job_id,
            project_id=req.project_id,
            segments_audio=segments_audio,
            total_duration_sec=round(total_duration, 2),
            status="completed",
        )

        # 记录任务
        job = TTSJob(
            job_id=job_id,
            project_id=req.project_id,
            status="completed",
            progress=1.0,
            results=segments_audio,
            created_at=datetime.now().isoformat(),
        )
        self._jobs[job_id] = job

        return result

    def get_job(self, job_id: str) -> TTSJob | None:
        return self._jobs.get(job_id)


# 全局单例
tts_engine = MockTTSEngine()
