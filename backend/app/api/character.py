"""M7 角色一致性管理 - API 路由"""

from fastapi import APIRouter, HTTPException
from app.models.character import CharacterInfo, CharacterCreateRequest, CharacterAttributes, CharacterConsistencyScore
from app.services.character.service import character_service

router = APIRouter()


@router.post("/characters", response_model=CharacterInfo)
async def create_character(req: CharacterCreateRequest):
    """F7.1 创建角色"""
    return character_service.create(req)


@router.get("/characters", response_model=list[CharacterInfo])
async def list_characters():
    """角色列表"""
    return character_service.list_all()


@router.get("/characters/{char_id}", response_model=CharacterInfo)
async def get_character(char_id: str):
    char = character_service.get(char_id)
    if not char:
        raise HTTPException(status_code=404, detail="角色不存在")
    return char


@router.put("/characters/{char_id}", response_model=CharacterInfo)
async def update_character(char_id: str, attrs: CharacterAttributes):
    """F7.3 更新角色属性"""
    char = character_service.update(char_id, attributes=attrs)
    if not char:
        raise HTTPException(status_code=404, detail="角色不存在")
    return char


@router.delete("/characters/{char_id}")
async def delete_character(char_id: str):
    if not character_service.delete(char_id):
        raise HTTPException(status_code=404, detail="角色不存在")
    return {"success": True}


@router.get("/characters/{char_id}/consistency", response_model=CharacterConsistencyScore)
async def check_consistency(char_id: str):
    """F7.5 角色一致性评分"""
    return character_service.check_consistency(char_id)
