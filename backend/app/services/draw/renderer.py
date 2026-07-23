"""M2 AI绘图 - Mock渲染服务

无GPU时模拟ComfyUI生成过程，返回占位图片和完整任务生命周期。
当真实ComfyUI可用时，替换此模块的实现即可。
"""

from __future__ import annotations
import uuid
import random
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.models.draw import RenderTask, RenderTaskRequest, PipelineConfig, ModelInfo, WorkflowTemplate

DATA_DIR = Path(__file__).parent.parent.parent / "data" / "draw"

# ============================================================
# 内置管线配置
# ============================================================
_BUILTIN_PIPELINES: list[PipelineConfig] = [
    PipelineConfig(
        id="sdxl-scene",
        name="SDXL 场景管线",
        pipeline_type="sdxl",
        base_model="RealVisXL v5.0",
        vae="sdxl_vae",
        sampler="DPM++ 2M Karras",
        scheduler="normal",
        steps_default=30,
        is_active=True,
    ),
    PipelineConfig(
        id="sdxl-character",
        name="SDXL 人物管线",
        pipeline_type="sdxl",
        base_model="DreamShaper XL",
        vae="sdxl_vae",
        sampler="DPM++ 2M Karras",
        steps_default=30,
        is_active=True,
    ),
    PipelineConfig(
        id="mock-dev",
        name="Mock 开发管线",
        pipeline_type="mock",
        base_model="mock",
        steps_default=1,
        is_active=True,
    ),
]

_BUILTIN_MODELS: list[ModelInfo] = [
    ModelInfo(id="realvisxl-v5", name="RealVisXL v5.0", model_type="checkpoint",
              base_model="SDXL", path="models/checkpoints/realvisxl50.safetensors",
              trigger_words=["photorealistic"], is_active=True),
    ModelInfo(id="dreamshaper-xl", name="DreamShaper XL", model_type="checkpoint",
              base_model="SDXL", path="models/checkpoints/dreamshaperXL.safetensors",
              trigger_words=["digital painting"], is_active=True),
    ModelInfo(id="sdxl-vae", name="SDXL VAE", model_type="vae",
              base_model="SDXL", path="models/vae/sdxl_vae.safetensors", is_active=True),
]

_BUILTIN_WORKFLOWS: list[WorkflowTemplate] = [
    WorkflowTemplate(
        id="wf-txt2img-scene", name="文生图-场景", description="标准场景文生图管线",
        workflow_type="text2img",
        input_schema={
            "positive_prompt": {"type": "string", "required": True},
            "negative_prompt": {"type": "string", "default": ""},
            "width": {"type": "int", "default": 1920},
            "height": {"type": "int", "default": 1080},
            "steps": {"type": "int", "default": 30},
            "cfg_scale": {"type": "float", "default": 7.0},
        },
        is_active=True,
    ),
    WorkflowTemplate(
        id="wf-img2img-refine", name="图生图-精修", description="参考图精修管线",
        workflow_type="img2img",
        input_schema={
            "reference_image": {"type": "string", "required": True},
            "positive_prompt": {"type": "string", "required": True},
            "denoising_strength": {"type": "float", "default": 0.75},
        },
        is_active=True,
    ),
]


class MockRenderer:
    """Mock 渲染器 - 模拟ComfyUI生成过程"""

    def __init__(self):
        self._tasks: dict[str, RenderTask] = {}
        self._pipelines = list(_BUILTIN_PIPELINES)
        self._models = list(_BUILTIN_MODELS)
        self._workflows = list(_BUILTIN_WORKFLOWS)
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    # ---- 任务管理 ----

    def create_task(self, req: RenderTaskRequest) -> RenderTask:
        """创建渲染任务（同步模拟）"""
        task_id = f"draw-{uuid.uuid4().hex[:12]}"

        task = RenderTask(
            task_id=task_id,
            project_id=req.project_id,
            prompt_id=req.prompt_id,
            status="processing",
            progress=0.0,
            results=[],
            params_snapshot=req.model_dump(),
            created_at=datetime.now().isoformat(),
            total_count=req.count,
        )
        self._tasks[task_id] = task

        # 模拟生成过程
        self._simulate_generation(task, req)
        return task

    def _simulate_generation(self, task: RenderTask, req: RenderTaskRequest):
        """模拟图片生成 - 返回随机占位图片信息"""
        results = []
        for i in range(req.count):
            fake_url = f"/mock/generated/{task.task_id}/{i+1}.png"
            results.append(fake_url)

        task.status = "completed"
        task.progress = 1.0
        task.results = results
        task.completed_at = datetime.now().isoformat()

    def get_task(self, task_id: str) -> Optional[RenderTask]:
        return self._tasks.get(task_id)

    def list_tasks(self, project_id: Optional[str] = None, page: int = 1, size: int = 20) -> list[RenderTask]:
        items = list(self._tasks.values())
        if project_id:
            items = [t for t in items if t.project_id == project_id]
        items.sort(key=lambda x: x.created_at, reverse=True)
        start = (page - 1) * size
        return items[start:start + size]

    def get_task_count(self, project_id: Optional[str] = None) -> int:
        items = list(self._tasks.values())
        if project_id:
            items = [t for t in items if t.project_id == project_id]
        return len(items)

    # ---- 管线管理 ----

    def get_pipelines(self) -> list[PipelineConfig]:
        return self._pipelines

    def get_pipeline(self, pipeline_id: str) -> Optional[PipelineConfig]:
        for p in self._pipelines:
            if p.id == pipeline_id:
                return p
        return None

    def get_models(self, model_type: Optional[str] = None) -> list[ModelInfo]:
        if model_type:
            return [m for m in self._models if m.model_type == model_type]
        return self._models

    def get_workflows(self, workflow_type: Optional[str] = None) -> list[WorkflowTemplate]:
        if workflow_type:
            return [w for w in self._workflows if w.workflow_type == workflow_type]
        return self._workflows


# 全局单例
renderer = MockRenderer()
