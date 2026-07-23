"""F1.3 冲突关键词清洗引擎

自动检测互斥描述（"明亮"+"昏暗"、"写实"+"二次元"），
基于规则引擎保留权重最高的关键词。
"""

from __future__ import annotations
from app.models.prompt import TagItem, ConflictCheckResponse

# 互斥分组：同一组内的词互斥
_CONFLICT_GROUPS: list[tuple[str, set[str], str]] = [
    ("亮度", {"明亮", "昏暗", "黑暗", "漆黑", "朦胧"}, "同一场景中亮度和暗度描述冲突"),
    ("时间", {"白天", "夜晚", "夜间", "清晨", "黄昏"}, "时间描述冲突"),
    ("风格", {"写实", "二次元", "水墨", "油画", "3D", "卡通"}, "画面风格冲突"),
    ("色温", {"温暖", "寒冷", "冰冷", "炽热"}, "色温感知冲突"),
    ("动态", {"静态", "动态", "运动", "静止"}, "画面动态冲突"),
    ("季节", {"春天", "夏天", "秋天", "冬天", "春季", "夏季", "秋季", "冬季"}, "季节描述冲突"),
    ("天气", {"晴天", "雨天", "雪天", "阴天", "暴风雨"}, "天气描述冲突"),
    ("景别", {"远景", "中景", "近景", "特写", "全景"}, "景别冲突"),
]


class ConflictCleaner:
    """冲突关键词清洗器"""

    def check(self, tags: list[TagItem]) -> ConflictCheckResponse:
        """检测并清洗冲突标签"""
        if not tags:
            return ConflictCheckResponse(has_conflict=False, conflicts=[], cleaned_tags=[])

        conflicts = []
        tag_texts = {t.tag for t in tags}
        tag_map = {t.tag: t for t in tags}

        for group_name, keywords, reason in _CONFLICT_GROUPS:
            matched = tag_texts & keywords
            if len(matched) >= 2:
                # 找到冲突：保留权重最高的，标记其余
                sorted_matched = sorted(
                    matched,
                    key=lambda x: tag_map[x].weight if x in tag_map else 1.0,
                    reverse=True,
                )
                keeper = sorted_matched[0]
                removed = list(sorted_matched[1:])
                conflicts.append({
                    "group": group_name,
                    "reason": reason,
                    "keeper": keeper,
                    "removed": removed,
                })

        # 生成清洗后的标签列表
        removed_set = set()
        for c in conflicts:
            removed_set.update(c["removed"])

        cleaned = [t for t in tags if t.tag not in removed_set]

        return ConflictCheckResponse(
            has_conflict=len(conflicts) > 0,
            conflicts=conflicts,
            cleaned_tags=cleaned,
        )

    def check_text(self, text: str) -> ConflictCheckResponse:
        """直接检测文本中的冲突关键词"""
        from app.services.mood_map import mood_service

        found_moods = [m for m, _ in mood_service.resolve_mood(text)]
        tags = [TagItem(tag=m, category="emotion", weight=1.0) for m in found_moods]
        return self.check(tags)


conflict_cleaner = ConflictCleaner()
