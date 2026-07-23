"""M4 文案生成服务 - API 路由"""

from __future__ import annotations
from fastapi import APIRouter, HTTPException, Query

from app.models.copywrite import (
    GenerateRequest, GenerateResponse, CopywriteProject, CopywriteSegment,
    CopywriteTemplate, SegmentUpdateRequest, EmotionCurve,
)
from app.services.copywrite.generator import copywrite_service

router = APIRouter()


@router.post("/generate", response_model=GenerateResponse)
async def generate_copywrite(req: GenerateRequest):
    """F4.1 文案生成 — 主题→结构化文案"""
    project, segments = copywrite_service.generate(req)

    return GenerateResponse(
        project_id=project.id,
        title=project.title,
        segments=segments,
        total_word_count=sum(s.word_count for s in segments),
        total_duration_sec=round(sum(s.estimated_duration_sec for s in segments), 1),
    )


@router.get("/projects", response_model=list[CopywriteProject])
async def list_projects():
    """获取文案项目列表"""
    return list(copywrite_service._projects.values())  # 简化实现


@router.get("/projects/{project_id}", response_model=CopywriteProject)
async def get_project(project_id: str):
    project = copywrite_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    return project


@router.get("/projects/{project_id}/segments", response_model=list[CopywriteSegment])
async def get_segments(project_id: str):
    """F4.2 获取文案段落列表"""
    segments = copywrite_service.get_segments(project_id)
    if not segments:
        raise HTTPException(status_code=404, detail="项目不存在或无段落")
    return segments


@router.put("/segments/{segment_id}", response_model=dict)
async def update_segment(segment_id: str, req: SegmentUpdateRequest):
    """F4.3 编辑段落"""
    ok = copywrite_service.update_segment(segment_id, req.content, req.scene_description, req.emotion)
    if not ok:
        raise HTTPException(status_code=404, detail="段落不存在")
    return {"success": True}


@router.get("/templates", response_model=list[CopywriteTemplate])
async def get_templates(genre: str | None = Query(None)):
    """F4.5 获取文案模板"""
    return copywrite_service.get_templates(genre)


@router.get("/status")
async def check_status():
    """检查LLM可用状态"""
    return {
        "llm_available": copywrite_service.has_llm,
        "mode": "llm" if copywrite_service.has_llm else "mock",
    }
