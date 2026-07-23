"""M4 文案生成服务 - Pydantic 数据模型"""

from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


class CopywriteProject(BaseModel):
    """文案项目"""
    id: str
    title: str
    topic: str
    genre: str = "cognitive"  # cognitive / story / lecture / marketing
    target_length: str = "medium"  # short(500) / medium(1500) / long(3000)
    style: str = "normal"  # normal / emotional / humorous / academic
    status: str = "draft"  # draft / generating / completed / failed
    total_segments: int = 0
    created_at: str = ""


class CopywriteSegment(BaseModel):
    """文案段落"""
    id: str
    project_id: str
    segment_index: int
    title: str = ""
    content: str
    word_count: int = 0
    estimated_duration_sec: float = 0.0
    scene_description: str = ""
    transition_hint: str = "fade"
    key_visuals: list[str] = Field(default_factory=list)
    emotion: str = "neutral"
    status: str = "draft"  # draft / approved / revised


class VisualTag(BaseModel):
    """视觉标签"""
    id: str
    segment_id: str
    tag_type: str  # object / person / scene / action / color / lighting / emotion
    tag_value: str
    confidence: float = 0.0


class EmotionCurve(BaseModel):
    """情感曲线"""
    id: str
    project_id: str
    curve_name: str = "default"
    data_points: list[dict] = Field(default_factory=list)  # [{time, emotion, intensity}]
    total_duration: float = 0.0


class CopywriteTemplate(BaseModel):
    """文案模板"""
    id: str
    name: str
    genre: str
    structure: list[dict] = Field(default_factory=list)  # [{title, description, word_count}]
    style_guide: str = ""
    is_system: bool = True


class GenerateRequest(BaseModel):
    """文案生成请求"""
    topic: str = Field(..., min_length=2, max_length=500, description="文案主题")
    genre: str = "cognitive"
    target_length: str = "medium"
    style: str = "normal"
    reference: str = ""
    preserve_literary: bool = False


class GenerateResponse(BaseModel):
    """文案生成响应"""
    project_id: str
    title: str
    segments: list[CopywriteSegment]
    total_word_count: int
    total_duration_sec: float


class SegmentUpdateRequest(BaseModel):
    """段落更新请求"""
    content: str
    scene_description: str = ""
    emotion: str = "neutral"
