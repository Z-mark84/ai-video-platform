"""Pipeline 视频生成流水线 - 数据模型"""

from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class PipelineStage(str, Enum):
    """流水线阶段"""
    PROMPT = "prompt"         # M1: 提示词优化
    COPYWRITE = "copywrite"   # M4: 文案生成
    DRAW = "draw"             # M2: AI绘图
    TTS = "tts"               # M5: TTS配音
    EDIT = "edit"             # M6: 智能剪辑
    QUALITY = "quality"       # M8: 质量评估


class StageStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class PipelineStageResult(BaseModel):
    """单个阶段的执行结果"""
    stage: PipelineStage
    status: StageStatus = StageStatus.PENDING
    progress: float = 0.0
    message: str = ""
    output: dict = Field(default_factory=dict)
    error: Optional[str] = None


class PipelineGenerateRequest(BaseModel):
    """视频生成请求"""
    topic: str = Field(..., description="视频主题/核心概念", min_length=1, max_length=500)
    genre: str = Field(default="cognitive", description="视频类型: cognitive|story|knowledge|tutorial")
    target_length: str = Field(default="medium", description="目标时长: short|medium|long")
    style: str = Field(default="normal", description="文案风格: normal|emotional|humorous|academic")
    lang: str = Field(default="zh", description="语言: zh|en")
    voice_style: str = Field(default="documentary", description="配音风格: documentary|story|news|normal")
    mood_tags: list[str] = Field(default_factory=list, description="氛围标签")
    auto_generate: bool = Field(default=True, description="是否全自动生成所有阶段")


class PipelineGenerateResponse(BaseModel):
    """视频生成响应"""
    project_id: str
    title: str
    status: str = "running"
    stages: list[PipelineStageResult]
    current_stage: str = ""
    overall_progress: float = 0.0
    estimated_duration_sec: float = 0.0
    created_at: str = ""


class PipelineProject(BaseModel):
    """Pipeline 项目"""
    id: str
    title: str
    topic: str
    genre: str
    target_length: str
    status: str = "running"
    stages: list[PipelineStageResult]
    overall_progress: float = 0.0
    created_at: str = ""


class PipelineStatusResponse(BaseModel):
    """Pipeline 状态查询响应"""
    project_id: str
    status: str
    stages: list[PipelineStageResult]
    overall_progress: float
    result_video_url: Optional[str] = None
