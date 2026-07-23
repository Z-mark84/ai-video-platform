"""M2 AI绘图服务 - Pydantic 数据模型"""

from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class RenderTaskRequest(BaseModel):
    """渲染任务请求"""
    project_id: str = Field(..., description="项目UUID")
    prompt_id: str = Field(..., description="关联提示词ID")
    positive_prompt: str = Field(..., description="正向提示词")
    negative_prompt: str = Field(default="", description="反向提示词")
    params: dict = Field(default_factory=lambda: {
        "width": 1920, "height": 1080, "steps": 30,
        "cfg_scale": 7.0, "sampler": "DPM++ 2M Karras",
    })
    classification: str = Field(default="scene", description="scene/character/fusion")
    count: int = Field(default=1, ge=1, le=30, description="生成张数")
    reference_images: list[str] = Field(default_factory=list, description="参考图片URL（图生图）")
    denoising_strength: float = Field(default=0.75, ge=0.0, le=1.0, description="图生图重绘强度")
    webhook_url: Optional[str] = Field(default=None, description="回调通知URL")


class RenderTask(BaseModel):
    """渲染任务状态"""
    task_id: str
    project_id: str
    prompt_id: str
    status: str = Field(default="pending")  # pending/processing/completed/failed
    progress: float = Field(default=0.0, ge=0.0, le=1.0)
    results: list[str] = Field(default_factory=list)  # 生成图片URL列表
    params_snapshot: dict = Field(default_factory=dict)
    error: Optional[str] = None
    created_at: str = ""
    completed_at: Optional[str] = None
    total_count: int = 1


class RenderTaskList(BaseModel):
    """任务列表"""
    items: list[RenderTask]
    total: int
    page: int = 1
    size: int = 20


class BatchRenderRequest(BaseModel):
    """批量渲染请求"""
    project_id: str
    tasks: list[RenderTaskRequest]


class PipelineConfig(BaseModel):
    """管线配置"""
    id: str
    name: str
    pipeline_type: str  # sdxl / sd3 / flux / mock
    base_model: str
    vae: Optional[str] = None
    sampler: str = "DPM++ 2M Karras"
    scheduler: str = "normal"
    cfg_scale_default: float = 7.0
    steps_default: int = 30
    extra_params: dict = Field(default_factory=dict)
    is_active: bool = True


class ModelInfo(BaseModel):
    """模型信息"""
    model_config = {'protected_namespaces': ()}
    id: str
    name: str
    model_type: str  # checkpoint / vae / lora / controlnet / upscaler
    base_model: str  # SD15 / SDXL / SD3 / Flux
    path: str
    hash_sha256: Optional[str] = None
    trigger_words: list[str] = Field(default_factory=list)
    preview_url: Optional[str] = None
    is_active: bool = True


class WorkflowTemplate(BaseModel):
    """ComfyUI工作流模板"""
    id: str
    name: str
    description: str
    workflow_type: str  # text2img / img2img / inpainting / upscale
    input_schema: dict = Field(default_factory=dict)
    output_schema: dict = Field(default_factory=dict)
    is_active: bool = True
