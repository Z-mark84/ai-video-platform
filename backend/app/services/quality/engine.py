"""M8 质量评估 - 评估引擎（Mock模式）

模拟CLIP Score、LPIPS、光流检测等评估算法。
"""

from __future__ import annotations
import uuid
import random
from datetime import datetime
from typing import Optional

from app.models.quality import (
    QualityScore, QualityReport, EvaluateRequest, UserFeedbackRequest,
)

# 评分阈值
_THRESHOLDS = {
    "lpips": 0.15,       # LPIPS越低越好
    "clip_score": 0.75,  # CLIP越高越好
    "face_sim": 0.85,    # 面部相似度
    "optical_flow": 0.7, # 光流平滑度
}


class QualityEngine:
    """质量评估引擎"""

    def __init__(self):
        self._reports: dict[str, QualityReport] = {}
        self._feedbacks: list[dict] = []

    def evaluate(self, req: EvaluateRequest) -> QualityReport:
        """F8.1+F8.2 综合评估：帧间一致性 + 语义对齐"""
        report_id = f"q-{uuid.uuid4().hex[:12]}"

        # 模拟LPIPS评分（0~0.3区间，越低越好）
        lpips = round(random.uniform(0.03, 0.25), 3)

        # 模拟CLIP评分（0.5~0.95区间，越高越好）
        clip = round(random.uniform(0.55, 0.93), 3)

        # 模拟光流平滑度
        flow = round(random.uniform(0.5, 0.95), 3)

        # 模拟面部一致性（50%概率有值）
        face_sim = round(random.uniform(0.7, 0.95), 3) if random.random() > 0.5 else None

        passed = (
            lpips <= _THRESHOLDS["lpips"]
            and clip >= _THRESHOLDS["clip_score"]
        )

        scores = QualityScore(
            task_id=req.task_id,
            lpips_avg=lpips,
            clip_score_avg=clip,
            optical_flow_smoothness=flow,
            face_similarity=face_sim,
            passed=passed,
            evaluated_at=datetime.now().isoformat(),
        )

        suggestions = self._generate_suggestions(scores)
        summary = self._generate_summary(scores)

        report = QualityReport(
            id=report_id,
            project_id=req.project_id,
            task_type=req.task_type,
            scores=scores,
            suggestions=suggestions,
            summary=summary,
        )
        self._reports[report_id] = report
        return report

    def _generate_suggestions(self, scores: QualityScore) -> list[str]:
        suggestions = []
        if scores.lpips_avg and scores.lpips_avg > _THRESHOLDS["lpips"]:
            suggestions.append(f"帧间一致性偏低(LPIPS={scores.lpips_avg})，建议增加seed一致性或使用图生图重绘")
        if scores.clip_score_avg and scores.clip_score_avg < _THRESHOLDS["clip_score"]:
            suggestions.append(f"语义对齐度偏低(CLIP={scores.clip_score_avg})，建议优化提示词或调整CFG Scale")
        if scores.face_similarity and scores.face_similarity < _THRESHOLDS["face_sim"]:
            suggestions.append(f"面部一致性偏低({scores.face_similarity})，建议使用更多参考图或调整InstantID权重")
        if scores.lpips_avg and scores.lpips_avg <= _THRESHOLDS["lpips"] and scores.clip_score_avg and scores.clip_score_avg >= _THRESHOLDS["clip_score"]:
            suggestions.append("质量达标，无需优化")
        return suggestions

    def _generate_summary(self, scores: QualityScore) -> str:
        if scores.passed:
            return "✅ 质量评估通过"
        issues = []
        if scores.lpips_avg and scores.lpips_avg > _THRESHOLDS["lpips"]:
            issues.append("帧间一致性")
        if scores.clip_score_avg and scores.clip_score_avg < _THRESHOLDS["clip_score"]:
            issues.append("语义对齐")
        return f"⚠️ 需优化: {', '.join(issues)}"

    def get_report(self, report_id: str) -> Optional[QualityReport]:
        return self._reports.get(report_id)

    def list_reports(self, project_id: Optional[str] = None) -> list[QualityReport]:
        items = list(self._reports.values())
        if project_id:
            items = [r for r in items if r.project_id == project_id]
        return items

    def submit_feedback(self, req: UserFeedbackRequest) -> bool:
        """F8.5 用户评分反馈"""
        feedback = {
            "task_id": req.task_id,
            "rating": req.rating,
            "comment": req.comment,
            "created_at": datetime.now().isoformat(),
        }
        self._feedbacks.append(feedback)

        # 关联到报告
        for report in self._reports.values():
            if report.scores.task_id == req.task_id:
                report.scores.user_rating = req.rating
                break
        return True

    def get_feedback_stats(self) -> dict:
        """用户反馈统计"""
        if not self._feedbacks:
            return {"total": 0, "avg_rating": 0, "counts": {}}
        ratings = [f["rating"] for f in self._feedbacks]
        avg = sum(ratings) / len(ratings)
        from collections import Counter
        counts = dict(Counter(ratings))
        return {"total": len(ratings), "avg_rating": round(avg, 2), "counts": counts}


engine = QualityEngine()
