"""M1 提示词优化引擎 - Pydantic 数据模型"""

from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


class TagItem(BaseModel):
    """单个提示词标签"""
    tag: str = Field(..., description="标签英文值")
    category: str = Field(..., description="标签分类: subject/scene/light/style/emotion/color/composition/custom")
    weight: float = Field(default=1.0, ge=0.1, le=2.0, description="权重 0.1-2.0")
    tag_zh: Optional[str] = Field(default=None, description="中文标签")


class NLInputRequest(BaseModel):
    """自然语言输入请求"""
    project_id: str = Field(..., description="项目UUID")
    text: str = Field(..., max_length=2000, description="用户口语化描述")
    context_tags: list[str] = Field(default_factory=list, description="上下文标签")
    lang: str = Field(default="zh", description="输入语言")


class TagInputRequest(BaseModel):
    """标签输入请求"""
    project_id: str = Field(..., description="项目UUID")
    tags: list[TagItem] = Field(..., description="标签列表")


class PromptOutput(BaseModel):
    """标准化提示词输出"""
    id: str = Field(..., description="提示词UUID")
    version: str = Field(default="1.0.0")
    classification: str = Field(..., description="scene/character/fusion")
    input_raw: str = Field(default="", description="用户原始输入")
    positive_prompt: str = Field(..., description="正向提示词")
    negative_prompt: str = Field(..., description="反向提示词")
    params: dict = Field(default_factory=lambda: {
        "width": 1920, "height": 1080, "steps": 30,
        "cfg_scale": 7.0, "sampler": "DPM++ 2M Karras"
    })
    weights: dict = Field(default_factory=lambda: {
        "user_keywords": 1.2, "system_quality": 1.0, "negative_global": 1.5
    })
    mapping_log: list[dict] = Field(default_factory=list)


class NLInputResponse(BaseModel):
    """自然语言输入响应"""
    input_id: str
    parsed_tags: list[TagItem]
    preview_zh: str
    preview_en: str
    confidence: float = Field(default=0.0, ge=0, le=1)


class ConflictCheckRequest(BaseModel):
    """冲突检查请求"""
    tags: list[TagItem]


class ConflictCheckResponse(BaseModel):
    """冲突检查响应"""
    has_conflict: bool
    conflicts: list[dict] = Field(default_factory=list)
    cleaned_tags: list[TagItem]


class OptimizeRequest(BaseModel):
    """完整优化请求"""
    tags: list[TagItem]
    classification: str = Field(default="scene", description="scene/character/fusion")
    preserve_literary: bool = Field(default=False, description="保留文学性修辞")
    model: str = Field(default="sdxl")


class TemplateItem(BaseModel):
    """模板项"""
    id: str
    name: str
    genre: str
    tags: list[TagItem]
    style_guide: Optional[str] = None
