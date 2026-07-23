"""M3 素材管理服务 - Pydantic 数据模型"""

from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class AssetInfo(BaseModel):
    """素材信息"""
    id: str
    project_id: str
    filename: str
    original_name: str
    file_size: int  # bytes
    mime_type: str  # image/png, audio/wav, video/mp4
    category: str = "uncategorized"  # scene/character/bg/audio/video/other
    tags: list[str] = Field(default_factory=list)
    width: Optional[int] = None
    height: Optional[int] = None
    duration_sec: Optional[float] = None  # 音频/视频时长
    source: str = "generated"  # generated / uploaded
    source_task_id: Optional[str] = None  # 来自哪个渲染任务
    storage_path: str  # 本地或OSS路径
    thumbnail_path: Optional[str] = None
    md5_hash: str = ""
    is_deleted: bool = False
    created_at: str = ""


class AssetUploadRequest(BaseModel):
    """素材上传请求（元数据）"""
    project_id: str
    category: str = "uncategorized"
    tags: list[str] = Field(default_factory=list)
    source: str = "uploaded"
    source_task_id: Optional[str] = None


class AssetListResponse(BaseModel):
    """素材列表"""
    items: list[AssetInfo]
    total: int
    page: int = 1
    size: int = 20


class AssetUpdateRequest(BaseModel):
    """素材更新请求"""
    category: Optional[str] = None
    tags: Optional[list[str]] = None
    original_name: Optional[str] = None


class AssetCategory(BaseModel):
    """素材分类"""
    id: str
    name: str
    description: str = ""
    color: str = "#6366f1"
    icon: str = "📁"
    sort_order: int = 0


class AssetTagCount(BaseModel):
    """标签统计"""
    tag: str
    count: int
