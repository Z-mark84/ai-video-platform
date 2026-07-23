"""M7 角色一致性管理 - Pydantic 数据模型"""

from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


class CharacterInfo(BaseModel):
    """角色信息"""
    id: str
    name: str
    reference_images: list[str] = Field(default_factory=list)
    embedding_path: Optional[str] = None
    attributes: CharacterAttributes = Field(default_factory=lambda: CharacterAttributes())
    tags: list[str] = Field(default_factory=list)
    usage_count: int = 0
    face_similarity: Optional[float] = None
    created_at: str = ""


class CharacterAttributes(BaseModel):
    """角色属性"""
    gender: str = "neutral"  # male / female / neutral
    age_range: str = "20-30"
    style: str = "写实"
    default_outfit: str = ""
    appearance_notes: str = ""


class CharacterCreateRequest(BaseModel):
    """角色创建请求"""
    name: str = Field(..., min_length=1, max_length=100)
    reference_images: list[str] = Field(default_factory=list)
    gender: str = "neutral"
    age_range: str = "20-30"
    style: str = "写实"
    default_outfit: str = ""
    tags: list[str] = Field(default_factory=list)


class CharacterConsistencyScore(BaseModel):
    """角色一致性评分"""
    character_id: str
    score: float  # 0-1
    passed: bool
    details: dict = Field(default_factory=dict)
