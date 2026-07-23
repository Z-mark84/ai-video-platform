"""M8 质量评估服务 - Pydantic 数据模型"""

from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


class QualityScore(BaseModel):
    """质量评估分数"""
    task_id: str
    lpips_avg: Optional[float] = None          # 帧间一致性(越低越好,阈值0.15)
    clip_score_avg: Optional[float] = None     # 语义对齐(越高越好,阈值0.75)
    optical_flow_smoothness: Optional[float] = None  # 光流平滑度(二期)
    face_similarity: Optional[float] = None    # 面部一致性(仅人物管线)
    passed: bool = False
    regenerate_count: int = 0
    user_rating: Optional[int] = None
    evaluated_at: str = ""


class QualityReport(BaseModel):
    """质量报告"""
    id: str
    project_id: str
    task_type: str = "text2img"  # text2img / img2img / video
    scores: QualityScore = Field(default_factory=lambda: QualityScore(task_id=""))
    suggestions: list[str] = Field(default_factory=list)
    summary: str = ""


class EvaluateRequest(BaseModel):
    """评估请求"""
    task_id: str
    project_id: str
    image_urls: list[str] = Field(default_factory=list)
    prompt_text: Optional[str] = None
    task_type: str = "text2img"


class UserFeedbackRequest(BaseModel):
    """用户反馈"""
    task_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: str = ""
