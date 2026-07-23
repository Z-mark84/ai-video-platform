"""M1 提示词优化引擎 - API 路由

实现 F1.1 双通道输入 / F1.2 映射 / F1.3 冲突清洗 / F1.4 加权补全
"""

from __future__ import annotations
import uuid

from fastapi import APIRouter, HTTPException

from app.models.prompt import (
    NLInputRequest,
    TagInputRequest,
    TagItem,
    PromptOutput,
    NLInputResponse,
    ConflictCheckRequest,
    ConflictCheckResponse,
    OptimizeRequest,
    TemplateItem,
)
from app.services.mood_map import mood_service
from app.services.conflict_checker import conflict_cleaner
from app.services.classification import enhancer

router = APIRouter()


@router.post("/nl-input", response_model=NLInputResponse)
async def natural_language_input(req: NLInputRequest):
    """F1.1 双通道输入 — 自然语言通道

    将口语化描述自动解析为结构化标签，生成中文+英文预览。
    """
    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="输入不能为空")

    # 1. 从感性词库中提取匹配
    mood_results = mood_service.resolve_mood_weights(text)
    parsed_tags = []
    for mood, params, weight in mood_results:
        parsed_tags.append(TagItem(
            tag=mood,
            category="emotion",
            weight=round(weight, 2),
            tag_zh=mood,
        ))

    # 2. 冲突清洗
    conflict_result = conflict_cleaner.check(parsed_tags)
    cleaned_tags = conflict_result.cleaned_tags if conflict_result.has_conflict else parsed_tags

    # 3. 分类判断
    classification = enhancer.classify_text(text)

    # 4. 生成预览
    from app.services.mood_map import _BUILTIN_MOOD_MAP
    preview_parts = []
    for t in cleaned_tags:
        if t.tag in _BUILTIN_MOOD_MAP:
            params = _BUILTIN_MOOD_MAP[t.tag]
            preview_parts.append(f"{t.tag}: {', '.join(params.values())}")
    preview_zh = " | ".join(preview_parts) if preview_parts else f"[{classification}] 待LLM深度优化"

    # 生成英文预览（简化版）
    preview_en = ", ".join(t.tag for t in cleaned_tags) if cleaned_tags else text

    return NLInputResponse(
        input_id=f"in-{uuid.uuid4().hex[:12]}",
        parsed_tags=cleaned_tags,
        preview_zh=preview_zh,
        preview_en=preview_en,
        confidence=min(0.95, 0.5 + len(cleaned_tags) * 0.1),
    )


@router.post("/tag-input", response_model=NLInputResponse)
async def tag_input(req: TagInputRequest):
    """F1.1 双通道输入 — 标签通道

    接收前端标签选择器提交的结构化标签，生成预览。
    """
    if not req.tags:
        raise HTTPException(status_code=400, detail="标签列表不能为空")

    # 冲突清洗
    conflict_result = conflict_cleaner.check(req.tags)
    cleaned = conflict_result.cleaned_tags if conflict_result.has_conflict else req.tags

    # 生成预览
    preview_zh = ", ".join(t.tag_zh or t.tag for t in cleaned)
    preview_en = ", ".join(f"({t.tag}:{t.weight})" if t.weight != 1.0 else t.tag for t in cleaned)

    return NLInputResponse(
        input_id=f"tag-{uuid.uuid4().hex[:12]}",
        parsed_tags=cleaned,
        preview_zh=preview_zh,
        preview_en=preview_en,
        confidence=min(0.95, 0.5 + len(cleaned) * 0.1),
    )


@router.post("/conflict-check", response_model=ConflictCheckResponse)
async def check_conflicts(req: ConflictCheckRequest):
    """F1.3 冲突关键词检测"""
    return conflict_cleaner.check(req.tags)


@router.post("/optimize", response_model=PromptOutput)
async def optimize_prompt(req: OptimizeRequest):
    """F1.4 完整优化：分类加权 + 自动补全 → 标准输出JSON"""
    return enhancer.enhance(
        tags=req.tags,
        classification=req.classification,
    )


@router.get("/moods", response_model=dict)
async def list_moods(category: str | None = None):
    """获取感性词库列表"""
    if category:
        groups = mood_service.get_categories()
        return {"category": category, "moods": groups.get(category, [])}
    return {
        "total": len(mood_service.get_all_moods()),
        "moods": mood_service.get_all_moods(),
        "categories": mood_service.get_categories(),
    }


@router.get("/moods/{mood}", response_model=dict)
async def get_mood(mood: str):
    """查询单个感性词映射详情"""
    result = mood_service.lookup(mood)
    if result is None:
        raise HTTPException(status_code=404, detail=f"未找到感性词 '{mood}'")
    return {"mood": mood, "mapping": result}


@router.post("/moods/{mood}", response_model=dict)
async def update_mood(mood: str, params: dict):
    """F1.9 词库热更新 — 更新单个词映射"""
    mood_service.update_mood(mood, params)
    return {"success": True, "mood": mood}


@router.post("/moods/bulk", response_model=dict)
async def bulk_update_moods(mapping: dict[str, dict]):
    """F1.9 批量更新词库"""
    count = mood_service.bulk_update(mapping)
    return {"success": True, "updated_count": count}


@router.get("/classifications", response_model=list[str])
async def list_classifications():
    """获取支持的画面分类"""
    return enhancer.get_supported_classifications()


@router.get("/templates", response_model=list[TemplateItem])
async def list_templates(genre: str | None = None):
    """F1.8 获取模板列表"""
    # 内置模板
    templates = [
        TemplateItem(
            id="tpl-sunset",
            name="黄昏山野",
            genre="scene",
            tags=[
                TagItem(tag="黄昏", category="scene", weight=1.2),
                TagItem(tag="山野", category="scene", weight=1.0),
                TagItem(tag="压抑", category="emotion", weight=1.0),
            ],
            style_guide="冷色调为主，饱和度适中偏暗",
        ),
        TemplateItem(
            id="tpl-lake",
            name="湖面独处",
            genre="scene",
            tags=[
                TagItem(tag="宁静", category="emotion", weight=1.2),
                TagItem(tag="湖面", category="scene", weight=1.0),
            ],
            style_guide="柔光，低对比，青蓝色调",
        ),
        TemplateItem(
            id="tpl-city",
            name="城市夜景",
            genre="fusion",
            tags=[
                TagItem(tag="夜晚", category="scene", weight=1.2),
                TagItem(tag="赛博朋克", category="style", weight=0.8),
            ],
            style_guide="霓虹光，高对比，紫粉蓝调",
        ),
        TemplateItem(
            id="tpl-forest",
            name="林间独处",
            genre="scene",
            tags=[
                TagItem(tag="孤独", category="emotion", weight=1.2),
                TagItem(tag="森林", category="scene", weight=1.0),
            ],
            style_guide="柔光散射，冷绿色调，人物占比<15%",
        ),
    ]
    if genre:
        templates = [t for t in templates if t.genre == genre]
    return templates
