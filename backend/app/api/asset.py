"""M3 素材管理服务 - API 路由"""

from __future__ import annotations
import uuid
from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import FileResponse
from app.models.asset import (
    AssetInfo, AssetUploadRequest, AssetListResponse,
    AssetUpdateRequest, AssetCategory, AssetTagCount,
)
from app.services.asset.store import asset_store

router = APIRouter()

_ALLOWED_MIME = {
    "image/jpeg", "image/png", "image/webp", "image/gif", "image/svg+xml",
    "audio/mpeg", "audio/wav", "audio/ogg", "audio/flac",
    "video/mp4", "video/webm", "video/quicktime",
    "application/json", "text/plain",
}
_MAX_FILE_SIZE = 100 * 1024 * 1024

# ---- 静态路径（必须在 /{asset_id} 之前） ----

@router.get("/categories", response_model=list[AssetCategory])
async def get_categories():
    """获取素材分类列表"""
    return asset_store.get_categories()


@router.get("/categories/stats")
async def get_category_stats(project_id: str | None = Query(None)):
    """各分类素材数量统计"""
    return asset_store.get_category_stats(project_id)


@router.get("/tags", response_model=list[AssetTagCount])
async def get_tags(project_id: str | None = Query(None)):
    """获取标签统计"""
    return asset_store.get_tags(project_id)


@router.get("/stats/summary")
async def get_stats_summary():
    """素材库概览统计"""
    return {
        "total_assets": asset_store.get_total_count(),
        "total_size_bytes": asset_store.get_total_size(),
        "categories": asset_store.get_category_stats(),
    }


@router.get("/list", response_model=AssetListResponse)
async def list_assets(
    project_id: str | None = Query(None),
    category: str | None = Query(None),
    mime_type: str | None = Query(None),
    tag: str | None = Query(None),
    search: str | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
):
    """F3.2 素材列表 — 支持过滤和搜索"""
    items, total = asset_store.list_assets(
        project_id=project_id, category=category,
        mime_type=mime_type, tag=tag, search=search,
        page=page, size=size,
    )
    return AssetListResponse(items=items, total=total, page=page, size=size)


@router.post("/upload", response_model=AssetInfo)
async def upload_asset(
    project_id: str = Form(...),
    file: UploadFile = File(...),
    category: str = Form("uncategorized"),
    tags: str = Form(""),
    source: str = Form("uploaded"),
    source_task_id: str | None = Form(None),
):
    """F3.1 素材上传"""
    if file.content_type not in _ALLOWED_MIME:
        raise HTTPException(status_code=400, detail=f"不支持的文件类型: {file.content_type}")
    content = await file.read()
    if len(content) > _MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="文件超过大小限制(100MB)")
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
    filename = file.filename or f"unnamed_{uuid.uuid4().hex[:8]}"
    asset = asset_store.add_asset(
        project_id=project_id, filename=filename, original_name=filename,
        file_size=len(content), mime_type=file.content_type or "application/octet-stream",
        category=category, tags=tag_list, source=source, source_task_id=source_task_id,
    )
    asset_store.save_file(asset.id, filename, content)
    return asset


@router.post("/upload-from-mock", response_model=AssetInfo)
async def mock_upload(project_id: str = "default"):
    """模拟从M2生成结果入库"""
    asset = asset_store.add_asset(
        project_id=project_id,
        filename=f"mock_gen_{uuid.uuid4().hex[:8]}.png",
        original_name="AI生成图片.png",
        file_size=1024 * 50, mime_type="image/png",
        category="scene", tags=["AI生成", "场景"],
        source="generated", width=1920, height=1080,
    )
    return asset


# ---- 参数化路径 ----

@router.get("/{asset_id}", response_model=AssetInfo)
async def get_asset(asset_id: str):
    """F3.5 素材详情"""
    asset = asset_store.get_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="素材不存在")
    return asset


@router.get("/{asset_id}/file")
async def get_asset_file(asset_id: str):
    """获取素材文件"""
    asset = asset_store.get_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="素材不存在")
    file_path = asset_store.get_file_path(asset_id, asset.filename)
    if not file_path:
        raise HTTPException(status_code=404, detail="文件不存在")
    return FileResponse(file_path, media_type=asset.mime_type, filename=asset.original_name)


@router.put("/{asset_id}", response_model=AssetInfo)
async def update_asset(asset_id: str, req: AssetUpdateRequest):
    """F3.3 素材更新"""
    asset = asset_store.update_asset(asset_id, category=req.category, tags=req.tags, original_name=req.original_name)
    if not asset:
        raise HTTPException(status_code=404, detail="素材不存在")
    return asset


@router.delete("/{asset_id}")
async def delete_asset(asset_id: str):
    """F3.4 素材删除（软删除）"""
    if not asset_store.delete_asset(asset_id):
        raise HTTPException(status_code=404, detail="素材不存在")
    return {"success": True}
