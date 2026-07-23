"""M7 角色一致性 - 管理服务（Mock模式）

模拟InstantID/IP-Adapter的面部特征提取和一致性管理。
"""

from __future__ import annotations
import uuid
import random
from datetime import datetime
from typing import Optional

from app.models.character import (
    CharacterInfo, CharacterAttributes, CharacterCreateRequest, CharacterConsistencyScore,
)

# Mock角色库
_MOCK_CHARACTERS: list[dict] = [
    {
        "name": "沉思青年", "gender": "male", "age_range": "25-30",
        "style": "写实", "default_outfit": "深色卫衣", "tags": ["主角", "沉思"],
    },
    {
        "name": "温柔女性", "gender": "female", "age_range": "20-25",
        "style": "写实", "default_outfit": "浅色连衣裙", "tags": ["主角", "温柔"],
    },
    {
        "name": "老者", "gender": "male", "age_range": "55-70",
        "style": "写实", "default_outfit": "中山装", "tags": ["配角", "智慧"],
    },
]


class CharacterService:
    """角色一致性管理服务"""

    def __init__(self):
        self._characters: dict[str, CharacterInfo] = {}
        self._init_mock()

    def _init_mock(self):
        for mc in _MOCK_CHARACTERS:
            char = CharacterInfo(
                id=f"char-{uuid.uuid4().hex[:8]}",
                name=mc["name"],
                reference_images=[f"/mock/character/{mc['name']}/ref_1.png"],
                embedding_path=f"/mock/embeddings/{mc['name']}.bin",
                attributes=CharacterAttributes(
                    gender=mc["gender"], age_range=mc["age_range"],
                    style=mc["style"], default_outfit=mc["default_outfit"],
                ),
                tags=mc["tags"],
                usage_count=random.randint(0, 10),
                face_similarity=round(random.uniform(0.82, 0.95), 3),
                created_at=datetime.now().isoformat(),
            )
            self._characters[char.id] = char

    def create(self, req: CharacterCreateRequest) -> CharacterInfo:
        """F7.1 创建角色"""
        char = CharacterInfo(
            id=f"char-{uuid.uuid4().hex[:8]}",
            name=req.name,
            reference_images=req.reference_images or [f"/mock/character/{req.name}/ref_1.png"],
            embedding_path=f"/mock/embeddings/{uuid.uuid4().hex}.bin",
            attributes=CharacterAttributes(
                gender=req.gender, age_range=req.age_range,
                style=req.style, default_outfit=req.default_outfit,
            ),
            tags=req.tags,
            created_at=datetime.now().isoformat(),
        )
        self._characters[char.id] = char
        return char

    def get(self, character_id: str) -> Optional[CharacterInfo]:
        return self._characters.get(character_id)

    def list_all(self) -> list[CharacterInfo]:
        return list(self._characters.values())

    def update(self, character_id: str, **kwargs) -> Optional[CharacterInfo]:
        char = self._characters.get(character_id)
        if not char:
            return None
        for key, val in kwargs.items():
            if hasattr(char, key) and val is not None:
                setattr(char, key, val)
        return char

    def delete(self, character_id: str) -> bool:
        if character_id in self._characters:
            del self._characters[character_id]
            return True
        return False

    def check_consistency(self, character_id: str) -> CharacterConsistencyScore:
        """F7.5 角色一致性评分（模拟FaceNet/ArcFace）"""
        char = self._characters.get(character_id)
        if not char:
            return CharacterConsistencyScore(character_id=character_id, score=0, passed=False)
        score = char.face_similarity if char.face_similarity else random.uniform(0.75, 0.95)
        return CharacterConsistencyScore(
            character_id=character_id,
            score=round(score, 3),
            passed=score >= 0.85,
            details={
                "face_match": score >= 0.85,
                "style_match": True,
                "recommendation": "良好" if score >= 0.85 else "建议使用更多参考图",
            },
        )


# 全局
character_service = CharacterService()
