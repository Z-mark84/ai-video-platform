"""M1 提示词优化引擎 + M2 AI绘图服务 - FastAPI 应用入口"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.prompt import router as prompt_router
from app.api.draw import router as draw_router
from app.api.asset import router as asset_router
from app.api.copywrite import router as copywrite_router
from app.api.tts import router as tts_router
from app.api.edit import router as edit_router
from app.api.character import router as character_router
from app.api.quality import router as quality_router

app = FastAPI(
    title="AI长视频生成平台",
    description="M1 提示词引擎 | M2 AI绘图 | M3 素材管理 | M4 文案生成 | M5 TTS配音 | M6 智能剪辑 | M7 角色一致性 | M8 质量评估",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(prompt_router, prefix="/api/v1/prompt")
app.include_router(draw_router, prefix="/api/v1/draw")
app.include_router(asset_router, prefix="/api/v1/asset")
app.include_router(copywrite_router, prefix="/api/v1/copywrite")
app.include_router(tts_router, prefix="/api/v1/tts")
app.include_router(edit_router, prefix="/api/v1/edit")
app.include_router(character_router, prefix="/api/v1/character")
app.include_router(quality_router, prefix="/api/v1/quality")

@app.get("/health")
async def health():
    return {"status": "ok", "modules": ["M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8"], "version": "1.0.0"}
