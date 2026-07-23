"""F1.4 分类加权与自动补全引擎

根据画面分类（场景/人物/融合）追加专属约束词，
分配权重体系（用户1.2/系统1.0/负面1.5），
自动补全分辨率/采样步数/胶片质感等参数。
"""

from __future__ import annotations
from app.models.prompt import TagItem, PromptOutput

# 三类画面的专属正向约束词
_CLASSIFICATION_POSITIVE: dict[str, list[str]] = {
    "scene": [
        "wide angle landscape", "depth of field", "atmospheric",
        "cinematic lighting", "environmental storytelling",
    ],
    "character": [
        "detailed face", "sharp eyes", "natural skin texture",
        "professional portrait", "soft lighting on face",
        "half body shot",
    ],
    "fusion": [
        "character in environment", "natural integration",
        "consistent lighting between subject and background",
        "depth of field", "balanced composition",
    ],
}

# 三类画面的专属反向约束词
_CLASSIFICATION_NEGATIVE: dict[str, list[str]] = {
    "scene": [
        "blurry", "low quality", "watermark", "text", "signature",
        "deformed", "disfigured", "bad anatomy",
    ],
    "character": [
        "extra fingers", "deformed hands", "mutated hands",
        "bad anatomy", "ugly face", "asymmetrical face",
        "watermark", "text", "signature",
    ],
    "fusion": [
        "mismatched lighting", "cutout look", "paste feeling",
        "extra limbs", "deformed", "bad anatomy",
        "watermark", "text",
    ],
}

# 系统级画质词（全局通用，权重1.0）
_SYSTEM_QUALITY_WORDS: list[str] = [
    "masterpiece", "best quality", "high quality", "8k uhd",
    "highly detailed", "sharp focus", "professional",
]


class ClassificationEnhancer:
    """分类加权与自动补全服务"""

    def enhance(
        self,
        tags: list[TagItem],
        classification: str = "scene",
        user_input_raw: str = "",
    ) -> PromptOutput:
        """
        对解析后的标签进行分类加权和补全，生成标准 PromptOutput
        """
        if classification not in _CLASSIFICATION_POSITIVE:
            classification = "scene"

        # 1. 构建正向提示词
        positive_parts = []

        # 用户关键词（权重1.2）
        user_tags = [t for t in tags if t.weight >= 1.0]
        if user_tags:
            weighted_user = ", ".join(
                f"({t.tag}:{t.weight})" if t.weight != 1.0 else t.tag
                for t in user_tags
            )
            positive_parts.append(weighted_user)

        # 系统画质词（权重1.0）
        positive_parts.extend(_SYSTEM_QUALITY_WORDS)

        # 分类专属正向词
        positive_parts.extend(_CLASSIFICATION_POSITIVE[classification])

        positive_prompt = ", ".join(positive_parts)

        # 2. 构建反向提示词
        negative_prompt = ", ".join(_CLASSIFICATION_NEGATIVE[classification])

        # 3. 构建映射日志
        mapping_log = [
            {
                "source": "user_tags",
                "count": len(user_tags),
                "weight": 1.2,
                "items": [t.tag for t in user_tags],
            },
            {
                "source": "system_quality",
                "count": len(_SYSTEM_QUALITY_WORDS),
                "weight": 1.0,
                "items": _SYSTEM_QUALITY_WORDS,
            },
            {
                "source": f"classification_{classification}",
                "count": len(_CLASSIFICATION_POSITIVE[classification]),
                "weight": 1.0,
                "items": _CLASSIFICATION_POSITIVE[classification],
            },
        ]

        # 4. 生成输出
        import uuid
        return PromptOutput(
            id=f"prompt-{uuid.uuid4().hex[:12]}",
            version="1.0.0",
            classification=classification,
            input_raw=user_input_raw,
            positive_prompt=positive_prompt,
            negative_prompt=negative_prompt,
            params={
                "width": 1920,
                "height": 1080,
                "steps": 30,
                "cfg_scale": 7.0,
                "sampler": "DPM++ 2M Karras",
            },
            weights={
                "user_keywords": 1.2,
                "system_quality": 1.0,
                "negative_global": 1.5,
            },
            mapping_log=mapping_log,
        )

    def classify_text(self, text: str) -> str:
        """根据文本内容自动判断分类"""
        text_lower = text.lower()
        # 人物关键词
        character_keywords = {"人", "人物", "角色", "face", "portrait", "女孩", "男孩", "男人", "女人"}
        scene_keywords = {"景", "场景", "风景", "landscape", "环境", "山", "海", "森林", "城市"}

        # 简
        has_character = any(k in text for k in character_keywords)
        has_scene = any(k in text for k in scene_keywords)

        if has_character and has_scene:
            return "fusion"
        elif has_character:
            return "character"
        return "scene"

    def get_supported_classifications(self) -> list[str]:
        return ["scene", "character", "fusion"]


enhancer = ClassificationEnhancer()
