"""M1 感性词汇 → 量化参数 映射词库（核心底层引擎）

将"压抑""孤独""温馨"等氛围感口语词汇，自动映射为
光影/色彩/构图三轴量化参数，消除SDXL/Flux出图崩坏。
"""

from __future__ import annotations
import json
import os
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent.parent / "data"

# ============================================================
# 内置映射词库（硬编码默认值，支持热更新覆盖）
# ============================================================

# 格式: 感性词 → { 光影, 色彩, 构图, 风格 } 四维量化参数
_BUILTIN_MOOD_MAP: dict[str, dict] = {
    # ---- 基础情感 ----
    "压抑": {
        "light": "侧逆光,暗角强度0.4",
        "color": "饱和度-30,冷色温4000K",
        "composition": "画面亮度降低15%",
        "style": "film_grain 0.3",
    },
    "孤独": {
        "light": "柔和散射光,低对比",
        "color": "去饱和,灰蓝色调",
        "composition": "广角远景,人物占比<15%",
        "style": "matte_finish",
    },
    "温馨": {
        "light": "暖色侧光,柔焦",
        "color": "饱和度+10,暖色温5500K",
        "composition": "中景,人物居中",
        "style": "soft_glow",
    },
    "紧张": {
        "light": "底部硬光,高对比",
        "color": "去饱和,冷绿偏色",
        "composition": "特写/微距,浅景深",
        "style": "grainy,shaky_cam",
    },
    "悲伤": {
        "light": "柔光,低对比,偏暗",
        "color": "冷蓝调,饱和度-20",
        "composition": "远景或空镜,留白",
        "style": "faded_colors",
    },
    "喜悦": {
        "light": "明亮散射光",
        "color": "饱和度+15,暖色温5800K",
        "composition": "中近景,人物动态",
        "style": "bokeh",
    },
    "神秘": {
        "light": "单束顶光/侧逆光",
        "color": "紫蓝偏色,饱和度-10",
        "composition": "阴影占比>60%",
        "style": "mist,volumetric_fog",
    },
    "宁静": {
        "light": "柔光,低对比",
        "color": "饱和度-10,偏青",
        "composition": "大景深,水平线构图",
        "style": "pastel_tone",
    },
    "愤怒": {
        "light": "硬光,高对比,红色补光",
        "color": "高饱和红色/橙色,色温偏暖",
        "composition": "特写面部,对角线构图",
        "style": "高纹理,gritty",
    },
    "梦幻": {
        "light": "背光+柔光晕,镜头光晕",
        "color": "饱和度+5,色温偏暖",
        "composition": "虚焦前景,浅景深",
        "style": "dreamy,soft_focus",
    },
    "恐惧": {
        "light": "底部光,高对比,硬阴影",
        "color": "冷蓝/紫,极低饱和",
        "composition": "鱼眼/广角变形,倾斜构图",
        "style": "noise,grainy",
    },
    "希望": {
        "light": "丁达尔光,逆光,光晕",
        "color": "暖金调,饱和度+5",
        "composition": "仰角,画面下方留光",
        "style": "god_rays,lens_flare",
    },
    # ---- 场景氛围 ----
    "黄昏": {
        "light": "暖色逆光/侧光",
        "color": "橙红调,色温3000K",
        "composition": "剪影或暖调为主",
        "style": "golden_hour",
    },
    "夜晚": {
        "light": "点光源,蓝调环境光",
        "color": "冷蓝调,高对比",
        "composition": "高感光噪点,暗部细节",
        "style": "night_photography",
    },
    "废墟": {
        "light": "顶部破光,尘埃光束",
        "color": "棕褐/灰绿,低饱和",
        "composition": "广角,破败前景+远景",
        "style": "rustic,decay",
    },
    "赛博朋克": {
        "light": "霓虹光,高对比",
        "color": "紫/粉/蓝,高饱和",
        "composition": "城市远景+近景招牌",
        "style": "cyberpunk,neon",
    },
    # ---- 画质/风格 ----
    "写实": {
        "light": "自然光",
        "color": "真实色温",
        "composition": "标准构图",
        "style": "photorealistic,8k_uhd",
    },
    "二次元": {
        "light": "平光/赛璐珞光",
        "color": "高饱和,明快色调",
        "composition": "标准动漫构图",
        "style": "anime,cell_shaded",
    },
    "水墨": {
        "light": "柔光",
        "color": "黑白或单色,极低饱和",
        "composition": "留白构图",
        "style": "ink_wash,brush_stroke",
    },
    "油画": {
        "light": "暖光",
        "color": "饱和+10",
        "composition": "经典构图",
        "style": "oil_painting,impasto",
    },
}


class MoodMappingService:
    """感性词汇映射服务 - 支持运行时热更新"""

    def __init__(self):
        self._map: dict[str, dict] = dict(_BUILTIN_MOOD_MAP)
        self._conflict_rules: list[tuple[set, str]] = [
            ({"明亮", "昏暗", "黑暗"}, "亮度冲突"),
            ({"白天", "夜晚", "夜间"}, "时间冲突"),
            ({"写实", "二次元", "水墨", "油画"}, "风格冲突"),
            ({"温暖", "寒冷", "冰冷"}, "色温冲突"),
            ({"静态", "动态", "运动"}, "画面动态冲突"),
        ]

    # ---- 查询 ----
    def lookup(self, mood: str) -> dict | None:
        """查询单个感性词映射结果"""
        return self._map.get(mood)

    def lookup_multi(self, moods: list[str]) -> list[dict]:
        """批量查询"""
        return [self._map.get(m, {}) for m in moods]

    def get_all_moods(self) -> list[str]:
        """获取所有支持的感性词"""
        return list(self._map.keys())

    def get_categories(self) -> dict[str, list[str]]:
        """按类别分组"""
        groups: dict[str, list[str]] = {"emotion": [], "scene": [], "style": []}
        for mood in self._map:
            if mood in {"写实", "二次元", "水墨", "油画"}:
                groups["style"].append(mood)
            elif mood in {"黄昏", "夜晚", "废墟", "赛博朋克"}:
                groups["scene"].append(mood)
            else:
                groups["emotion"].append(mood)
        return groups

    # ---- 热更新 ----
    def update_mood(self, mood: str, params: dict) -> bool:
        """运行时更新单个词映射（F1.9 词库热更新）"""
        self._map[mood] = params
        return True

    def delete_mood(self, mood: str) -> bool:
        """删除词映射"""
        return self._map.pop(mood, None) is not None

    def bulk_update(self, mapping: dict[str, dict]) -> int:
        """批量更新"""
        count = 0
        for mood, params in mapping.items():
            self._map[mood] = params
            count += 1
        return count

    # ---- 持久化 ----
    def save_to_disk(self, path: str | None = None) -> str:
        """持久化到JSON文件"""
        save_path = Path(path or DATA_DIR / "mood_map.json")
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_text(json.dumps(self._map, ensure_ascii=False, indent=2), encoding="utf-8")
        return str(save_path)

    def load_from_disk(self, path: str | None = None) -> int:
        """从JSON文件加载"""
        load_path = Path(path or DATA_DIR / "mood_map.json")
        if not load_path.exists():
            return 0
        data = json.loads(load_path.read_text(encoding="utf-8"))
        self._map.update(data)
        return len(data)

    # ---- 工具方法 ----
    def resolve_mood(self, text: str) -> list[tuple[str, dict]]:
        """从文本中提取已知的感性词并返回映射"""
        found = []
        for mood in self._map:
            if mood in text:
                found.append((mood, self._map[mood]))
        return found

    def resolve_mood_weights(self, text: str) -> list[tuple[str, dict, float]]:
        """提取感性词并基于位置分配权重"""
        results = self.resolve_mood(text)
        weighted = []
        base_weight = 1.2  # 用户关键词基础权重
        for i, (mood, params) in enumerate(results):
            # 越靠前的词权重越高
            w = base_weight - i * 0.05
            weighted.append((mood, params, max(0.8, w)))
        return weighted


# 全局单例
mood_service = MoodMappingService()
