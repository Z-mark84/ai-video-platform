"""M2 AI绘图服务 - API 路由"""

from __future__ import annotations
import uuid

from fastapi import APIRouter, HTTPException, Query

from app.models.draw import (
    RenderTaskRequest, RenderTask, RenderTaskList,
    BatchRenderRequest, PipelineConfig, ModelInfo, WorkflowTemplate,
)
from app.services.draw.renderer import renderer

router = APIRouter()


@router.post("/render", response_model=RenderTask)
async def create_render_task(req: RenderTaskRequest):
    """F2.1 文生图 / F2.2 图生图 — 创建渲染任务"""
    task = renderer.create_task(req)
    return task


@router.post("/batch-render")
async def batch_render(req: BatchRenderRequest):
    """F2.3 批量生成 — 提交多个渲染任务"""
    task_ids = []
    for task_req in req.tasks:
        task = renderer.create_task(task_req)
        task_ids.append(task.task_id)
    return {"task_ids": task_ids, "count": len(task_ids)}


@router.get("/tasks", response_model=RenderTaskList)
async def list_tasks(
    project_id: str | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
):
    """获取渲染任务列表"""
    items = renderer.list_tasks(project_id, page, size)
    total = renderer.get_task_count(project_id)
    return RenderTaskList(items=items, total=total, page=page, size=size)


@router.get("/tasks/{task_id}", response_model=RenderTask)
async def get_task(task_id: str):
    """查询单个任务状态"""
    task = renderer.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task


@router.get("/pipelines", response_model=list[PipelineConfig])
async def list_pipelines():
    """获取支持的渲染管线"""
    return renderer.get_pipelines()


@router.get("/pipelines/{pipeline_id}", response_model=PipelineConfig)
async def get_pipeline(pipeline_id: str):
    pipe = renderer.get_pipeline(pipeline_id)
    if not pipe:
        raise HTTPException(status_code=404, detail="管线不存在")
    return pipe


@router.get("/models", response_model=list[ModelInfo])
async def list_models(model_type: str | None = Query(None)):
    """获取模型列表"""
    return renderer.get_models(model_type)


@router.get("/workflows", response_model=list[WorkflowTemplate])
async def list_workflows(workflow_type: str | None = Query(None)):
    """获取工作流模板"""
    return renderer.get_workflows(workflow_type)
