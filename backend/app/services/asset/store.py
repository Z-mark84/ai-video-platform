"""M3 素材管理 - 存储服务（内存+本地文件系统）"""

from __future__ import annotations
import uuid
import hashlib
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Optional

from app.models.asset import AssetInfo, AssetCategory, AssetTagCount

DATA_DIR = Path(__file__).parent.parent.parent / "data" / "assets"
ASSETS_DIR = DATA_DIR / "files"

# 默认分类
_BUILTIN_CATEGORIES: list[AssetCategory] = [
    AssetCategory(id="scene", name="场景", description="AI生成的场景图片", color="#22d3ee", icon="🌄", sort_order=1),
    AssetCategory(id="character", name="人物", description="AI生成的人物图片", color="#f472b6", icon="👤", sort_order=2),
    AssetCategory(id="bg", name="背景", description="纯背景/空镜素材", color="#6366f1", icon="🖼️", sort_order=3),
    AssetCategory(id="audio", name="音频", description="配音/BGM音频文件", color="#10b981", icon="🎵", sort_order=4),
    AssetCategory(id="video", name="视频", description="已渲染的视频片段", color="#f59e0b", icon="🎬", sort_order=5),
    AssetCategory(id="other", name="其他", description="其他类型素材", color="#6b7a90", icon="📦", sort_order=6),
]

# Mock图片数据（用于生成占位缩略图）
_MOCK_IMAGES = [
    # 格式: (mime, content, label)
    ("image/svg+xml", '<svg xmlns="http://www.w3.org/2000/svg" width="320" height="180" viewBox="0 0 320 180"><rect width="320" height="180" fill="#1a1f2b"/><text x="160" y="90" text-anchor="middle" fill="#6366f1" font-size="14" font-family="monospace">ASSET PLACEHOLDER</text></svg>', "placeholder"),
]


class AssetStore:
    """素材存储服务 - 内存+文件系统"""

    def __init__(self):
        self._assets: dict[str, AssetInfo] = {}
        self._categories = list(_BUILTIN_CATEGORIES)
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        ASSETS_DIR.mkdir(parents=True, exist_ok=True)
        self._load_index()

    # ---- CRUD ----

    def add_asset(
        self,
        project_id: str,
        filename: str,
        original_name: str,
        file_size: int,
        mime_type: str,
        category: str = "uncategorized",
        tags: list[str] | None = None,
        source: str = "uploaded",
        source_task_id: str | None = None,
        width: int | None = None,
        height: int | None = None,
        duration_sec: float | None = None,
    ) -> AssetInfo:
        """添加素材记录"""
        asset_id = f"ast-{uuid.uuid4().hex[:12]}"
        storage_path = f"assets/{asset_id}/{filename}"
        md5_hash = hashlib.md5(f"{asset_id}-{datetime.now().isoformat()}".encode()).hexdigest()

        asset = AssetInfo(
            id=asset_id,
            project_id=project_id,
            filename=filename,
            original_name=original_name,
            file_size=file_size,
            mime_type=mime_type,
            category=category,
            tags=tags or [],
            width=width,
            height=height,
            duration_sec=duration_sec,
            source=source,
            source_task_id=source_task_id,
            storage_path=storage_path,
            thumbnail_path=f"assets/{asset_id}/thumb_{filename}",
            md5_hash=md5_hash,
            created_at=datetime.now().isoformat(),
        )
        self._assets[asset_id] = asset
        self._save_index()
        return asset

    def get_asset(self, asset_id: str) -> AssetInfo | None:
        asset = self._assets.get(asset_id)
        if asset and not asset.is_deleted:
            return asset
        return None

    def list_assets(
        self,
        project_id: str | None = None,
        category: str | None = None,
        mime_type: str | None = None,
        tag: str | None = None,
        search: str | None = None,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[AssetInfo], int]:
        """列出素材（支持过滤和搜索）"""
        items = [a for a in self._assets.values() if not a.is_deleted]

        if project_id:
            items = [a for a in items if a.project_id == project_id]
        if category:
            items = [a for a in items if a.category == category]
        if mime_type:
            items = [a for a in items if a.mime_type.startswith(mime_type)]
        if tag:
            items = [a for a in items if tag in a.tags]
        if search:
            search_lower = search.lower()
            items = [a for a in items if search_lower in a.original_name.lower() or search_lower in a.filename.lower()]

        items.sort(key=lambda x: x.created_at, reverse=True)
        total = len(items)
        start = (page - 1) * size
        page_items = items[start:start + size]
        return page_items, total

    def update_asset(self, asset_id: str, **kwargs) -> AssetInfo | None:
        asset = self._assets.get(asset_id)
        if not asset or asset.is_deleted:
            return None
        for key, value in kwargs.items():
            if hasattr(asset, key) and value is not None:
                setattr(asset, key, value)
        self._save_index()
        return asset

    def delete_asset(self, asset_id: str) -> bool:
        """软删除"""
        asset = self._assets.get(asset_id)
        if not asset:
            return False
        asset.is_deleted = True
        self._save_index()
        return True

    def hard_delete_asset(self, asset_id: str) -> bool:
        """物理删除"""
        if asset_id in self._assets:
            del self._assets[asset_id]
            self._save_index()
            return True
        return False

    # ---- 分类 ----

    def get_categories(self) -> list[AssetCategory]:
        return self._categories

    def get_category_stats(self, project_id: str | None = None) -> list[dict]:
        """各分类素材数量统计"""
        items = [a for a in self._assets.values() if not a.is_deleted]
        if project_id:
            items = [a for a in items if a.project_id == project_id]

        stats = {}
        for cat in self._categories:
            stats[cat.id] = {"name": cat.name, "icon": cat.icon, "count": 0, "color": cat.color}

        for a in items:
            cat_id = a.category if a.category in stats else "other"
            if cat_id in stats:
                stats[cat_id]["count"] += 1

        return list(stats.values())

    # ---- 标签 ----

    def get_tags(self, project_id: str | None = None) -> list[AssetTagCount]:
        """获取所有标签及其使用次数"""
        items = [a for a in self._assets.values() if not a.is_deleted]
        if project_id:
            items = [a for a in items if a.project_id == project_id]

        tag_counts: dict[str, int] = {}
        for a in items:
            for t in a.tags:
                tag_counts[t] = tag_counts.get(t, 0) + 1

        return sorted(
            [AssetTagCount(tag=t, count=c) for t, c in tag_counts.items()],
            key=lambda x: x.count,
            reverse=True,
        )

    # ---- 持久化 ----

    def _save_index(self):
        index_path = DATA_DIR / "index.json"
        data = {
            "assets": [
                a.model_dump() for a in self._assets.values()
            ],
        }
        index_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def _load_index(self):
        index_path = DATA_DIR / "index.json"
        if index_path.exists():
            data = json.loads(index_path.read_text(encoding="utf-8"))
            for item in data.get("assets", []):
                asset = AssetInfo(**item)
                self._assets[asset.id] = asset

    # ---- 文件操作 ----

    def save_file(self, asset_id: str, filename: str, content: bytes) -> str:
        """保存文件到本地存储"""
        asset_dir = ASSETS_DIR / asset_id
        asset_dir.mkdir(parents=True, exist_ok=True)
        file_path = asset_dir / filename
        file_path.write_bytes(content)
        return str(file_path)

    def get_file_path(self, asset_id: str, filename: str) -> str | None:
        path = ASSETS_DIR / asset_id / filename
        return str(path) if path.exists() else None

    # ---- 统计 ----

    def get_total_count(self, project_id: str | None = None) -> int:
        items = [a for a in self._assets.values() if not a.is_deleted]
        if project_id:
            items = [a for a in items if a.project_id == project_id]
        return len(items)

    def get_total_size(self) -> int:
        return sum(a.file_size for a in self._assets.values() if not a.is_deleted)


# 全局单例
asset_store = AssetStore()
