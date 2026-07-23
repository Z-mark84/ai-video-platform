"""M6 智能剪辑服务 - API 路由"""

from __future__ import annotations
from fastapi import APIRouter, HTTPException, Query
from app.models.edit import (
    EditingRequest, EditingSegment, VideoProject,
    TimelineSegment, GlobalSettings, RenderProgress,
)
from app.services.edit.engine import engine

router = APIRouter()


@router.post("/projects", response_model=VideoProject)
async def create_project(req: EditingRequest):
    """F6.7 创建视频项目"""
    return engine.create_project(req)


@router.get("/projects", response_model=list[VideoProject])
async def list_projects():
    return engine.list_projects()


@router.get("/projects/{project_id}", response_model=VideoProject)
async def get_project(project_id: str):
    p = engine.get_project(project_id)
    if not p:
        raise HTTPException(status_code=404, detail="项目不存在")
    return p


@router.put("/projects/{project_id}/timeline", response_model=VideoProject)
async def update_timeline(project_id: str, segments: list[TimelineSegment]):
    """更新时间线"""
    p = engine.update_timeline(project_id, segments)
    if not p:
        raise HTTPException(status_code=404, detail="项目不存在")
    return p


@router.post("/projects/{project_id}/auto-match", response_model=VideoProject)
async def auto_match(project_id: str, assets: list[str] = Query([]), audio_urls: list[str] = Query([])):
    """F6.1 分镜自动匹配"""
    p = engine.auto_match(project_id, assets, audio_urls)
    if not p:
        raise HTTPException(status_code=404, detail="项目不存在")
    return p


@router.post("/projects/{project_id}/render", response_model=RenderProgress)
async def render(project_id: str):
    """F6.6 渲染导出"""
    return engine.render(project_id)


@router.get("/projects/{project_id}/render", response_model=RenderProgress)
async def get_render(project_id: str):
    r = engine.get_render(project_id)
    if not r:
        raise HTTPException(status_code=404, detail="渲染任务不存在")
    return r


@router.get("/bgm")
async def list_bgm():
    """F6.4 BGM列表"""
    return engine.get_bgm_list()


@router.get("/transitions")
async def list_transitions():
    """F6.5 转场列表"""
    return engine.get_transitions()


@router.post("/estimate")
async def estimate(segments: list[TimelineSegment]):
    """预估视频总时长"""
    return {"total_duration_sec": engine.estimate_duration(segments)}
