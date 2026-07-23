"""M5 TTS配音服务 - Pydantic 数据模型"""

from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


class VoiceInfo(BaseModel):
    """声线信息"""
    id: str
    name: str
    provider: str = "mock"  # mock / chattts / cosyvoice / azure
    gender: str = "neutral"  # male / female / neutral
    language: str = "zh-CN"
    style: str = "normal"  # normal / news / story / documentary
    preview_url: Optional[str] = None
    supported_emotions: list[str] = Field(default_factory=lambda: ["neutral", "happy", "sad", "angry", "calm"])
    is_active: bool = True


class EmotionParams(BaseModel):
    """情感参数"""
    speed: float = Field(default=1.0, ge=0.5, le=2.0, description="语速")
    pitch: float = Field(default=0.0, ge=-12.0, le=12.0, description="音调偏移(半音)")
    volume: float = Field(default=1.0, ge=0.1, le=1.5, description="音量")
    energy: float = Field(default=0.5, ge=0.0, le=1.0, description="激昂度")
    intonation: float = Field(default=0.5, ge=0.0, le=1.0, description="语调起伏")


class EmotionPreset(BaseModel):
    """情感预设"""
    id: str
    name: str
    emotion: str
    params: EmotionParams
    is_system: bool = True


class TTSJobRequest(BaseModel):
    """配音任务请求"""
    project_id: str
    segments: list[dict] = Field(..., description="段落列表 [{id, text, voice_id, emotion}]")
    voice_id: str = "default"
    global_emotion: Optional[EmotionParams] = None
    pause_between_segments: float = Field(default=0.8, ge=0, le=3.0)


class TTSJobResult(BaseModel):
    """配音任务结果"""
    job_id: str
    project_id: str
    segments_audio: list[dict] = Field(default_factory=list)
    total_duration_sec: float = 0.0
    status: str = "completed"
    error: Optional[str] = None


class TTSJob(BaseModel):
    """配音任务状态"""
    job_id: str
    project_id: str
    status: str = "pending"  # pending / processing / completed / failed
    progress: float = 0.0
    results: list[dict] = Field(default_factory=list)
    created_at: str = ""
