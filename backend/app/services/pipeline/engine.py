"""Pipeline 视频生成引擎 - 核心编排服务

串联 M1→M4→M2→M5→M6→M8 六个模块的完整视频生成流程。
当前使用 Mock 模式模拟各阶段，真实 AI 服务可用时替换对应模块即可。
"""

from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional

from app.models.pipeline import (
    PipelineStage, StageStatus, PipelineStageResult,
    PipelineGenerateRequest, PipelineGenerateResponse,
    PipelineProject,
)
from app.models.draw import RenderTaskRequest
from app.models.copywrite import GenerateRequest as CopywriteRequest
from app.models.tts import TTSJobRequest
from app.models.edit import EditingRequest, EditingSegment


class PipelineEngine:
    """视频生成流水线引擎"""

    def __init__(self):
        self._projects: dict[str, PipelineProject] = {}

    def generate(self, req: PipelineGenerateRequest) -> PipelineGenerateResponse:
        """执行完整视频生成流水线"""
        project_id = f"vid-{uuid.uuid4().hex[:12]}"
        stages: list[PipelineStageResult] = []

        # ---- Stage 1: M1 提示词优化 ----
        stage1 = self._run_prompt_stage(req, project_id)
        stages.append(stage1)

        # ---- Stage 2: M4 文案生成 ----
        stage2 = self._run_copywrite_stage(req, project_id, stage1)
        stages.append(stage2)

        # ---- Stage 3: M2 AI绘图 ----
        stage3 = self._run_draw_stage(req, project_id, stage2)
        stages.append(stage3)

        # ---- Stage 4: M5 TTS配音 ----
        stage4 = self._run_tts_stage(req, project_id, stage2)
        stages.append(stage4)

        # ---- Stage 5: M6 智能剪辑 ----
        stage5 = self._run_edit_stage(req, project_id, stage3, stage4)
        stages.append(stage5)

        # ---- Stage 6: M8 质量评估 ----
        stage6 = self._run_quality_stage(project_id, stage5)
        stages.append(stage6)

        # 计算总进度
        completed_stages = sum(1 for s in stages if s.status == StageStatus.COMPLETED)
        overall_progress = completed_stages / len(stages)

        # 估算总时长
        est_duration = stage2.output.get("total_duration_sec", 0)

        title = req.topic
        if stage2.status == StageStatus.COMPLETED and stage2.output.get("title"):
            title = stage2.output["title"]

        response = PipelineGenerateResponse(
            project_id=project_id,
            title=title,
            status="completed" if overall_progress >= 1.0 else "running",
            stages=stages,
            current_stage="quality",
            overall_progress=overall_progress,
            estimated_duration_sec=est_duration,
            created_at=datetime.now().isoformat(),
        )

        self._projects[project_id] = PipelineProject(
            id=project_id,
            title=title,
            topic=req.topic,
            genre=req.genre,
            target_length=req.target_length,
            status="completed",
            stages=stages,
            overall_progress=overall_progress,
            created_at=response.created_at,
        )

        return response

    def _run_prompt_stage(self, req: PipelineGenerateRequest, project_id: str) -> PipelineStageResult:
        """M1 提示词优化阶段"""
        try:
            from app.services.mood_map import mood_service
            from app.services.conflict_checker import conflict_cleaner
            from app.services.classification import enhancer

            # 解析氛围标签
            mood_results = mood_service.resolve_mood_weights(req.topic)
            tags = []
            for mood, params, weight in mood_results:
                tags.append({"tag": mood, "category": "emotion", "weight": round(weight, 2)})
            for tag in req.mood_tags:
                tags.append({"tag": tag, "category": "custom", "weight": 1.0})

            # 冲突清洗
            from app.models.prompt import TagItem
            tag_items = [TagItem(tag=t["tag"], category=t["category"], weight=t["weight"]) for t in tags]
            conflict_result = conflict_cleaner.check(tag_items)

            # 分类
            classification = enhancer.classify_text(req.topic)

            # 生成优化后的提示词
            prompt_output = enhancer.enhance(
                tags=conflict_result.cleaned_tags if conflict_result.has_conflict else tag_items,
                classification=classification,
            )

            return PipelineStageResult(
                stage=PipelineStage.PROMPT,
                status=StageStatus.COMPLETED,
                progress=1.0,
                message=f"提示词优化完成: {classification} 类",
                output={
                    "classification": classification,
                    "positive_prompt": prompt_output.positive_prompt,
                    "negative_prompt": prompt_output.negative_prompt,
                    "params": prompt_output.params,
                },
            )
        except Exception as e:
            return PipelineStageResult(
                stage=PipelineStage.PROMPT,
                status=StageStatus.FAILED,
                error=str(e),
                message="提示词优化失败",
            )

    def _run_copywrite_stage(self, req: PipelineGenerateRequest, project_id: str, prev: PipelineStageResult) -> PipelineStageResult:
        """M4 文案生成阶段"""
        try:
            from app.services.copywrite.generator import copywrite_service
            from app.models.copywrite import GenerateRequest as CWReq

            cw_req = CWReq(
                topic=req.topic,
                genre=req.genre,
                target_length=req.target_length,
                style=req.style,
            )
            project, segments = copywrite_service.generate(cw_req)

            seg_list = []
            for seg in segments:
                seg_list.append({
                    "id": seg.id,
                    "title": seg.title,
                    "content": seg.content,
                    "word_count": seg.word_count,
                    "estimated_duration_sec": seg.estimated_duration_sec,
                    "scene_description": seg.scene_description,
                    "emotion": seg.emotion,
                })

            total_duration = sum(s.estimated_duration_sec for s in segments)

            return PipelineStageResult(
                stage=PipelineStage.COPYWRITE,
                status=StageStatus.COMPLETED,
                progress=1.0,
                message=f"文案生成完成: {project.title}，{len(segments)} 个段落，{total_duration:.0f}秒",
                output={
                    "project_id": project.id,
                    "title": project.title,
                    "segments": seg_list,
                    "total_word_count": sum(s.word_count for s in segments),
                    "total_duration_sec": round(total_duration, 1),
                    "mode": "llm" if copywrite_service.has_llm else "mock",
                },
            )
        except Exception as e:
            return PipelineStageResult(
                stage=PipelineStage.COPYWRITE,
                status=StageStatus.FAILED,
                error=str(e),
                message="文案生成失败",
            )

    def _run_draw_stage(self, req: PipelineGenerateRequest, project_id: str, prev: PipelineStageResult) -> PipelineStageResult:
        """M2 AI绘图阶段 - 为每个文案段落生成配图"""
        try:
            from app.services.draw.renderer import renderer

            segments = prev.output.get("segments", [])
            prompt_en = ""
            # 尝试从 prompt 阶段获取英文提示词
            # (由于阶段是顺序的，我们需要独立获取)
            images = []
            for i, seg in enumerate(segments):
                task_req = RenderTaskRequest(
                    project_id=project_id,
                    prompt_id=f"{project_id}-seg{i}",
                    count=1,
                    positive_prompt=seg.get("scene_description", req.topic),
                    negative_prompt="low quality, blurry, distorted",
                )
                task = renderer.create_task(task_req)
                images.append({
                    "segment_index": i,
                    "task_id": task.task_id,
                    "image_url": task.results[0] if task.results else "",
                    "scene": seg.get("scene_description", ""),
                })

            return PipelineStageResult(
                stage=PipelineStage.DRAW,
                status=StageStatus.COMPLETED,
                progress=1.0,
                message=f"AI绘图完成: {len(images)} 张配图生成完毕",
                output={
                    "images": images,
                    "total_images": len(images),
                    "pipeline": "mock",
                },
            )
        except Exception as e:
            return PipelineStageResult(
                stage=PipelineStage.DRAW,
                status=StageStatus.SKIPPED if not prev.output.get("segments") else StageStatus.FAILED,
                error=str(e),
                message=f"AI绘图阶段: {e}",
            )

    def _run_tts_stage(self, req: PipelineGenerateRequest, project_id: str, prev: PipelineStageResult) -> PipelineStageResult:
        """M5 TTS配音阶段 - 为每个文案段落合成语音"""
        try:
            from app.services.tts.engine import tts_engine
            from app.models.tts import TTSJobRequest

            segments = prev.output.get("segments", [])
            tts_segments = []
            for seg in segments:
                tts_segments.append({
                    "id": seg.get("id", ""),
                    "text": seg.get("content", ""),
                    "voice_id": "vo-male-calm-01" if req.voice_style == "documentary" else "vo-female-warm-01",
                    "emotion": seg.get("emotion", "neutral"),
                })

            tts_req = TTSJobRequest(
                project_id=project_id,
                voice_id="vo-male-calm-01",
                segments=tts_segments,
                pause_between_segments=0.5,
            )
            result = tts_engine.synthesize(tts_req)

            audio_segments = []
            for a in result.segments_audio:
                audio_segments.append({
                    "segment_index": a["segment_index"],
                    "audio_url": a["audio_url"],
                    "duration_sec": a["duration_sec"],
                    "word_count": a["word_count"],
                })

            return PipelineStageResult(
                stage=PipelineStage.TTS,
                status=StageStatus.COMPLETED,
                progress=1.0,
                message=f"TTS配音完成: {len(result.segments_audio)} 个段落，总时长 {result.total_duration_sec}秒",
                output={
                    "job_id": result.job_id,
                    "audio_segments": audio_segments,
                    "total_duration_sec": result.total_duration_sec,
                    "mode": "mock",
                },
            )
        except Exception as e:
            return PipelineStageResult(
                stage=PipelineStage.TTS,
                status=StageStatus.SKIPPED if not prev.output.get("segments") else StageStatus.FAILED,
                error=str(e),
                message=f"TTS配音阶段: {e}",
            )

    def _run_edit_stage(
        self,
        req: PipelineGenerateRequest,
        project_id: str,
        draw_stage: PipelineStageResult,
        tts_stage: PipelineStageResult,
    ) -> PipelineStageResult:
        """M6 智能剪辑阶段 - 合成图片+音频为视频"""
        try:
            from app.services.edit.engine import engine
            from app.models.edit import EditingRequest as EditReq, EditingSegment

            images = draw_stage.output.get("images", [])
            audio_segments = tts_stage.output.get("audio_segments", [])

            edit_segments = []
            for i in range(max(len(images), len(audio_segments))):
                img = images[i] if i < len(images) else {}
                aud = audio_segments[i] if i < len(audio_segments) else {}
                edit_segments.append(EditingSegment(
                    seq=i,
                    image_url=img.get("image_url", ""),
                    audio_url=aud.get("audio_url", ""),
                    subtitle_text=aud.get("text", f"段落 {i+1}"),
                    duration_sec=aud.get("duration_sec", 30),
                    transition="fade" if i > 0 else "cut",
                    scene_description=img.get("scene", ""),
                ))

            edit_req = EditReq(
                project_name=req.topic[:50],
                segments=edit_segments,
                global_settings={
                    "resolution": "1920x1080",
                    "fps": 24,
                    "bgm_id": "bgm_calm_01",
                    "bgm_volume": 0.3,
                    "subtitle_style": "default",
                    "brightness_delta": 0,
                    "saturation_delta": 0,
                },
            )
            video_project = engine.create_project(edit_req)

            # 触发渲染
            render_result = engine.render(video_project.id)

            return PipelineStageResult(
                stage=PipelineStage.EDIT,
                status=StageStatus.COMPLETED,
                progress=1.0,
                message=f"视频合成完成: {len(edit_segments)} 个片段，输出 1080p",
                output={
                    "project_id": video_project.id,
                    "video_url": render_result.output_url if render_result.status == "completed" else "",
                    "segments_count": len(edit_segments),
                    "total_duration_sec": sum(s.duration_sec for s in edit_segments),
                    "resolution": "1920x1080",
                },
            )
        except Exception as e:
            return PipelineStageResult(
                stage=PipelineStage.EDIT,
                status=StageStatus.SKIPPED if draw_stage.status != StageStatus.COMPLETED else StageStatus.FAILED,
                error=str(e),
                message=f"视频合成阶段: {e}",
            )

    def _run_quality_stage(self, project_id: str, prev: PipelineStageResult) -> PipelineStageResult:
        """M8 质量评估阶段"""
        try:
            from app.services.quality.engine import engine
            from app.models.quality import EvaluateRequest

            eval_req = EvaluateRequest(
                task_id=f"task-{project_id}",
                project_id=project_id,
                task_type="video",
                image_urls=[],
            )
            report = engine.evaluate(eval_req)

            return PipelineStageResult(
                stage=PipelineStage.QUALITY,
                status=StageStatus.COMPLETED,
                progress=1.0,
                message=f"质量评估完成: {'通过' if report.scores.passed else '需优化'}",
                output={
                    "report_id": report.id,
                    "passed": report.scores.passed,
                    "lpips_avg": report.scores.lpips_avg,
                    "clip_score_avg": report.scores.clip_score_avg,
                    "suggestions": report.suggestions,
                    "summary": report.summary,
                },
            )
        except Exception as e:
            return PipelineStageResult(
                stage=PipelineStage.QUALITY,
                status=StageStatus.FAILED,
                error=str(e),
                message=f"质量评估失败: {e}",
                output={},
            )

    def get_project(self, project_id: str) -> Optional[PipelineProject]:
        return self._projects.get(project_id)

    def list_projects(self) -> list[PipelineProject]:
        return list(self._projects.values())


# 全局单例
pipeline_engine = PipelineEngine()
