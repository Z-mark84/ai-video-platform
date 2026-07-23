"""Pipeline 视频生成流水线 - API 路由

一键生成：串联 M1→M4→M2→M5→M6→M8 的完整视频生成流程。
"""

from __future__ import annotations
from fastapi import APIRouter, HTTPException

from app.models.pipeline import (
    PipelineGenerateRequest, PipelineGenerateResponse,
    PipelineProject, PipelineStatusResponse,
)
from app.services.pipeline.engine import pipeline_engine

router = APIRouter()


@router.post("/generate", response_model=PipelineGenerateResponse)
async def generate_video(req: PipelineGenerateRequest):
    """一键生成视频 - 执行完整流水线

    流程:
    1. M1 提示词优化 → 生成标准化绘图关键词
    2. M4 文案生成 → 生成结构化视频文案
    3. M2 AI绘图 → 为每个段落生成配图
    4. M5 TTS配音 → 为每个段落合成语音
    5. M6 智能剪辑 → 图片+音频+字幕合成为视频
    6. M8 质量评估 → 综合评分和建议
    """
    if not req.topic.strip():
        raise HTTPException(status_code=400, detail="视频主题不能为空")
    return pipeline_engine.generate(req)


@router.get("/projects", response_model=list[PipelineProject])
async def list_projects():
    """获取所有 Pipeline 项目"""
    return pipeline_engine.list_projects()


@router.get("/projects/{project_id}", response_model=PipelineProject)
async def get_project(project_id: str):
    """查询单个 Pipeline 项目详情"""
    project = pipeline_engine.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    return project


@router.get("/projects/{project_id}/status", response_model=PipelineStatusResponse)
async def get_project_status(project_id: str):
    """查询 Pipeline 项目状态"""
    project = pipeline_engine.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    result_url = None
    for stage in project.stages:
        if stage.stage.value == "edit" and stage.status.value == "completed":
            result_url = stage.output.get("video_url")
            break

    return PipelineStatusResponse(
        project_id=project.id,
        status=project.status,
        stages=project.stages,
        overall_progress=project.overall_progress,
        result_video_url=result_url,
    )
