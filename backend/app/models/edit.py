"""M6 智能剪辑服务 - Pydantic 数据模型"""

from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


class TimelineSegment(BaseModel):
    """时间线段落"""
    seq: int
    image_url: str = ""
    audio_url: str = ""
    subtitle_text: str = ""
    duration_sec: float = 5.0
    transition: str = "fade"  # fade / cut / dissolve
    highlight_words: list[str] = Field(default_factory=list)
    scene_description: str = ""


class VideoProject(BaseModel):
    """视频项目"""
    id: str
    name: str
    timeline: list[TimelineSegment] = Field(default_factory=list)
    global_settings: GlobalSettings = Field(default_factory=lambda: GlobalSettings())
    status: str = "draft"  # draft / rendering / completed / failed
    output_path: Optional[str] = None
    created_at: str = ""


class GlobalSettings(BaseModel):
    """全局设置"""
    brightness_delta: int = -15
    saturation_delta: int = -10
    bgm_id: str = "bgm_calm_01"
    bgm_volume_db: float = -15.0
    voice_volume_db: float = -3.0
    subtitle_style: str = "typewriter_center"
    resolution: str = "1920x1080"
    fps: int = 30


class EditingRequest(BaseModel):
    """智能剪辑请求"""
    project_name: str = "未命名视频"
    segments: list[EditingSegment] = Field(default_factory=list)


class EditingSegment(BaseModel):
    """剪辑段落输入"""
    image_url: str = ""
    audio_url: str = ""
    subtitle_text: str = ""
    duration_sec: float = 5.0
    transition: str = "fade"
    scene_description: str = ""


class RenderProgress(BaseModel):
    """渲染进度"""
    project_id: str
    progress: float = 0.0
    status: str = "pending"
    output_url: Optional[str] = None
    error: Optional[str] = None
