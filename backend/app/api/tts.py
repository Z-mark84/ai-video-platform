"""M5 TTS配音服务 - API 路由"""

from __future__ import annotations
from fastapi import APIRouter, HTTPException, Query

from app.models.tts import (
    VoiceInfo, EmotionPreset, EmotionParams,
    TTSJobRequest, TTSJobResult, TTSJob,
)
from app.services.tts.engine import tts_engine

router = APIRouter()


# ---- 声线管理 ----

@router.get("/voices", response_model=list[VoiceInfo])
async def list_voices(gender: str | None = Query(None), style: str | None = Query(None)):
    """F5.1 声线列表"""
    return tts_engine.get_voices(gender, style)


@router.get("/voices/{voice_id}", response_model=VoiceInfo)
async def get_voice(voice_id: str):
    voice = tts_engine.get_voice(voice_id)
    if not voice:
        raise HTTPException(status_code=404, detail="声线不存在")
    return voice


# ---- 情感预设 ----

@router.get("/emotion-presets", response_model=list[EmotionPreset])
async def list_emotion_presets():
    """F5.2 情感预设列表"""
    return tts_engine.get_emotion_presets()


# ---- 配音任务 ----

@router.post("/synthesize", response_model=TTSJobResult)
async def synthesize(req: TTSJobRequest):
    """F5.3 批量分段配音"""
    if not req.segments:
        raise HTTPException(status_code=400, detail="段落列表不能为空")
    result = tts_engine.synthesize(req)
    return result


@router.get("/jobs/{job_id}", response_model=TTSJob)
async def get_job(job_id: str):
    job = tts_engine.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="任务不存在")
    return job
