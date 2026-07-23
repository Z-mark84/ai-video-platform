"""M6 智能剪辑 - 编辑引擎（Mock模式）

模拟MoviePy+FFmpeg的视频合成流程。
支持：分镜匹配、字幕渲染、BGM混音、转场、调色。
"""

from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional
from app.models.edit import (
    VideoProject, TimelineSegment, GlobalSettings,
    EditingRequest, EditingSegment, RenderProgress,
)

# 内置BGM库
_BUILTIN_BGM = [
    {"id": "bgm_calm_01", "name": "宁静之音", "duration_sec": 120},
    {"id": "bgm_gentle_01", "name": "温柔旋律", "duration_sec": 90},
    {"id": "bgm_inspiring_01", "name": "鼓舞", "duration_sec": 60},
    {"id": "bgm_mystery_01", "name": "神秘氛围", "duration_sec": 75},
]

# 内置转场
_BUILTIN_TRANSITIONS = [
    {"id": "fade", "name": "淡入淡出", "duration_range": [0.3, 3.0]},
    {"id": "cut", "name": "硬切", "duration_range": [0, 0]},
    {"id": "dissolve", "name": "交叉溶解", "duration_range": [0.5, 2.0]},
    {"id": "blur", "name": "模糊转场", "duration_range": [0.5, 2.0]},
]


class EditingEngine:
    """智能剪辑引擎"""

    def __init__(self):
        self._projects: dict[str, VideoProject] = {}
        self._renders: dict[str, RenderProgress] = {}

    def create_project(self, req: EditingRequest) -> VideoProject:
        """创建视频项目"""
        project_id = f"vid-{uuid.uuid4().hex[:12]}"
        timeline = []
        for i, seg in enumerate(req.segments):
            timeline.append(TimelineSegment(
                seq=i + 1,
                image_url=seg.image_url,
                audio_url=seg.audio_url,
                subtitle_text=seg.subtitle_text,
                duration_sec=seg.duration_sec,
                transition=seg.transition,
                scene_description=seg.scene_description,
            ))
        project = VideoProject(
            id=project_id,
            name=req.project_name,
            timeline=timeline,
            status="draft",
            created_at=datetime.now().isoformat(),
        )
        self._projects[project_id] = project
        return project

    def get_project(self, project_id: str) -> Optional[VideoProject]:
        return self._projects.get(project_id)

    def list_projects(self) -> list[VideoProject]:
        return list(self._projects.values())

    def update_timeline(self, project_id: str, segments: list[TimelineSegment]) -> Optional[VideoProject]:
        project = self._projects.get(project_id)
        if not project:
            return None
        project.timeline = segments
        project.status = "draft"
        return project

    def auto_match(self, project_id: str, assets: list[str], audio_urls: list[str]) -> Optional[VideoProject]:
        """F6.1 分镜自动匹配：文案→素材自动对应"""
        project = self._projects.get(project_id)
        if not project:
            return None
        for i, seg in enumerate(project.timeline):
            if i < len(assets):
                seg.image_url = assets[i]
            if i < len(audio_urls):
                seg.audio_url = audio_urls[i]
        return project

    def render(self, project_id: str) -> RenderProgress:
        """F6.6 渲染导出（Mock）"""
        project = self._projects.get(project_id)
        if not project:
            return RenderProgress(project_id=project_id, status="failed", error="项目不存在")

        project.status = "completed"
        output_url = f"/mock/video/{project_id}/output_1080p.mp4"

        # 模拟渲染参数
        total_duration = sum(s.duration_sec for s in project.timeline)
        mock_params = {
            "resolution": project.global_settings.resolution,
            "fps": project.global_settings.fps,
            "total_duration_sec": round(total_duration, 1),
            "segments": len(project.timeline),
            "bgm": project.global_settings.bgm_id,
            "subtitle_style": project.global_settings.subtitle_style,
            "brightness": project.global_settings.brightness_delta,
            "saturation": project.global_settings.saturation_delta,
        }

        progress = RenderProgress(
            project_id=project_id,
            progress=1.0,
            status="completed",
            output_url=output_url,
        )
        self._renders[project_id] = progress
        return progress

    def get_render(self, project_id: str) -> Optional[RenderProgress]:
        return self._renders.get(project_id)

    def get_bgm_list(self) -> list[dict]:
        return list(_BUILTIN_BGM)

    def get_transitions(self) -> list[dict]:
        return list(_BUILTIN_TRANSITIONS)

    def estimate_duration(self, timeline: list[TimelineSegment]) -> float:
        total = sum(max(0.5, s.duration_sec) for s in timeline)
        return round(total, 1)


# 全局
engine = EditingEngine()
