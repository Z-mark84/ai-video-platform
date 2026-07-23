"""M8 质量评估服务 - API 路由"""

from fastapi import APIRouter, HTTPException, Query
from app.models.quality import EvaluateRequest, QualityReport, UserFeedbackRequest
from app.services.quality.engine import engine

router = APIRouter()


@router.post("/evaluate", response_model=QualityReport)
async def evaluate(req: EvaluateRequest):
    """F8.1+F8.2 综合质量评估"""
    return engine.evaluate(req)


@router.get("/reports", response_model=list[QualityReport])
async def list_reports(project_id: str | None = Query(None)):
    return engine.list_reports(project_id)


@router.get("/reports/{report_id}", response_model=QualityReport)
async def get_report(report_id: str):
    r = engine.get_report(report_id)
    if not r:
        raise HTTPException(status_code=404, detail="报告不存在")
    return r


@router.post("/feedback")
async def submit_feedback(req: UserFeedbackRequest):
    """F8.5 用户评分反馈"""
    engine.submit_feedback(req)
    return {"success": True}


@router.get("/feedback/stats")
async def feedback_stats():
    """反馈统计"""
    return engine.get_feedback_stats()
