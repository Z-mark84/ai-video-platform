# AI 长视频生成平台

> 🎬 一键生成 AI 长视频 — 从主题输入到完整视频输出的全自动化流水线  
> 🌐 [在线体验](https://你的用户名.github.io/ai-video-platform/) | [部署指南](./DEPLOY.md)

## 📋 项目概述

AI 长视频生成平台是一个全栈应用，覆盖了 AI 生成视频的完整流程：**提示词优化 → 文案生成 → AI绘图 → TTS配音 → 智能剪辑 → 质量评估**。

### 核心能力

| 模块 | 功能 | 状态 |
|------|------|------|
| **🎬 Pipeline** | 一键视频生成流水线（串联全部模块） | ✅ v0.4.0 |
| **M1** 提示词引擎 | 自然语言→标准化绘图关键词，双通道输入，冲突清洗，感性词映射 | ✅ 完成 |
| **M2** AI绘图 | 文生图/图生图，批量渲染，多管线支持，SDXL参数配置 | ✅ Mock |
| **M3** 素材管理 | 素材库CRUD，分类检索，标签管理 | ✅ 完成 |
| **M4** 文案生成 | 主题→结构化视频文案，LLM/Mock双模式，多类型模板 | ✅ Mock+LLM |
| **M5** TTS配音 | 多声线选择，情感参数调节，批量分段配音 | ✅ Mock |
| **M6** 智能剪辑 | 分镜自动匹配，时间线编辑，字幕/转场/BGM，视频合成 | ✅ Mock |
| **M7** 角色一致性 | 角色创建/属性管理，一致性评分，参考图管理 | ✅ Mock |
| **M8** 质量评估 | LPIPS/CLIP评分，帧间一致性，语义对齐，优化建议 | ✅ Mock |

> 注：Mock 模式使用内置模拟数据，真实 AI 服务（ComfyUI/ChatTTS/Ollama）准备就绪后可无缝切换。

### 技术栈

| 层级 | 技术 |
|------|------|
| **前端** | Vue 3.5 + TypeScript + Vite 8 + Naive UI 2.44 + Pinia 4 |
| **后端** | Python FastAPI 0.115 + Uvicorn 0.30 + Pydantic 2.9 |
| **AI(预留)** | ComfyUI (SDXL) + ChatTTS/CosyVoice + Ollama (Qwen2.5-7B) |
| **分词** | jieba 0.42 |

## 🚀 快速启动

### 前置要求

- Python 3.10+
- Node.js 18+
- （可选）Ollama + ComfyUI（用于真实AI生成）

### 后端

```bash
cd backend
pip install -r requirements.txt
python main.py
# FastAPI 服务运行在 http://localhost:8000
# API 文档: http://localhost:8000/docs
```

### 前端

```bash
cd frontend
npm install
npm run dev
# Vite 开发服务器运行在 http://localhost:5173
```

### 生产构建

```bash
cd frontend
npm run build
# 产出在 dist/ 目录
```

## 🎬 Pipeline 一键生成

核心功能：输入一个视频主题，自动执行完整的 6 阶段视频生成流程。

### 流程

```
用户输入主题
    ↓
✏️ M1 提示词优化 → 生成标准化绘图关键词
    ↓
📝 M4 文案生成 → 生成结构化视频文案（段落+场景+情绪）
    ↓
🎨 M2 AI绘图 → 为每个段落生成对应配图
    ↓
🎙️ M5 TTS配音 → 为每个段落合成语音
    ↓
🎬 M6 智能剪辑 → 图片+音频+字幕合成为视频
    ↓
📊 M8 质量评估 → 综合评分和优化建议
```

### API

```bash
# 一键生成视频
curl -X POST http://localhost:8000/api/v1/pipeline/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "人工智能如何改变教育的未来",
    "genre": "cognitive",
    "target_length": "medium",
    "style": "normal",
    "voice_style": "documentary"
  }'

# 查询生成状态
curl http://localhost:8000/api/v1/pipeline/projects/{project_id}/status
```

## 📐 项目结构

```
ai-video-platform/
├── backend/
│   ├── main.py                    # 启动入口
│   ├── requirements.txt           # Python 依赖
│   └── app/
│       ├── __init__.py            # FastAPI 应用（注册9个路由）
│       ├── api/
│       │   ├── pipeline.py        # 🎬 视频生成流水线
│       │   ├── prompt.py          # M1 提示词引擎
│       │   ├── draw.py            # M2 AI绘图
│       │   ├── asset.py           # M3 素材管理
│       │   ├── copywrite.py       # M4 文案生成
│       │   ├── tts.py             # M5 TTS配音
│       │   ├── edit.py            # M6 智能剪辑
│       │   ├── character.py       # M7 角色一致性
│       │   └── quality.py         # M8 质量评估
│       ├── models/                # Pydantic 数据模型（9个模块）
│       └── services/              # 业务逻辑层
│           ├── pipeline/          # 🎬 流水线编排引擎
│           ├── mood_map.py        # M1 感性词映射
│           ├── conflict_checker.py # M1 冲突清洗
│           ├── classification.py  # M1 分类加权
│           ├── draw/renderer.py   # M2 渲染服务
│           ├── copywrite/         # M4 文案生成（LLM+Mock）
│           ├── tts/engine.py      # M5 TTS引擎
│           ├── edit/engine.py     # M6 剪辑引擎
│           ├── character/         # M7 角色服务
│           └── quality/engine.py  # M8 质量引擎
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   └── src/
│       ├── App.vue               # 主应用（9个Tab）
│       ├── api/                   # API 客户端（9个模块）
│       ├── stores/               # Pinia 状态管理
│       └── components/
│           ├── pipeline/          # 🎬 视频生成主界面
│           ├── prompt/            # M1 提示词面板
│           ├── draw/              # M2 绘图面板
│           ├── asset/             # M3 素材面板
│           ├── copywrite/         # M4 文案面板
│           ├── tts/               # M5 配音面板
│           ├── edit/              # M6 剪辑面板
│           ├── character/         # M7 角色面板
│           └── quality/           # M8 质量面板
└── README.md
```

## 🔌 完整 API 端点

### 🎬 Pipeline
| 方法 | 路径 | 功能 |
|------|------|------|
| POST | `/api/v1/pipeline/generate` | 一键生成视频 |
| GET | `/api/v1/pipeline/projects` | 项目列表 |
| GET | `/api/v1/pipeline/projects/{id}` | 项目详情 |
| GET | `/api/v1/pipeline/projects/{id}/status` | 项目状态 |

### M1 提示词引擎
| 方法 | 路径 | 功能 |
|------|------|------|
| POST | `/api/v1/prompt/nl-input` | 自然语言解析 |
| POST | `/api/v1/prompt/tag-input` | 标签输入预览 |
| POST | `/api/v1/prompt/conflict-check` | 冲突检测 |
| POST | `/api/v1/prompt/optimize` | 完整优化 |
| GET | `/api/v1/prompt/moods` | 感性词库 |
| GET | `/api/v1/prompt/templates` | 模板列表 |

### M2 AI绘图
| 方法 | 路径 | 功能 |
|------|------|------|
| POST | `/api/v1/draw/render` | 创建渲染任务 |
| POST | `/api/v1/draw/batch-render` | 批量渲染 |
| GET | `/api/v1/draw/tasks` | 任务列表 |
| GET | `/api/v1/draw/pipelines` | 管线列表 |
| GET | `/api/v1/draw/models` | 模型列表 |
| GET | `/api/v1/draw/workflows` | 工作流模板 |

### M4 文案生成
| 方法 | 路径 | 功能 |
|------|------|------|
| POST | `/api/v1/copywrite/generate` | 生成文案 |
| GET | `/api/v1/copywrite/projects` | 项目列表 |
| PUT | `/api/v1/copywrite/segments/{id}` | 编辑段落 |
| GET | `/api/v1/copywrite/templates` | 文案模板 |
| GET | `/api/v1/copywrite/status` | LLM状态 |

### M5 TTS配音
| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/api/v1/tts/voices` | 声线列表 |
| GET | `/api/v1/tts/emotion-presets` | 情感预设 |
| POST | `/api/v1/tts/synthesize` | 批量配音 |

### M6 智能剪辑
| 方法 | 路径 | 功能 |
|------|------|------|
| POST | `/api/v1/edit/projects` | 创建视频项目 |
| PUT | `/api/v1/edit/projects/{id}/timeline` | 更新时间线 |
| POST | `/api/v1/edit/projects/{id}/auto-match` | 分镜自动匹配 |
| POST | `/api/v1/edit/projects/{id}/render` | 渲染导出 |
| GET | `/api/v1/edit/bgm` | BGM列表 |
| GET | `/api/v1/edit/transitions` | 转场列表 |

### M7 角色一致性
| 方法 | 路径 | 功能 |
|------|------|------|
| POST | `/api/v1/character/characters` | 创建角色 |
| GET | `/api/v1/character/characters` | 角色列表 |
| PUT | `/api/v1/character/characters/{id}` | 更新属性 |
| GET | `/api/v1/character/characters/{id}/consistency` | 一致性评分 |

### M8 质量评估
| 方法 | 路径 | 功能 |
|------|------|------|
| POST | `/api/v1/quality/evaluate` | 综合评估 |
| GET | `/api/v1/quality/reports` | 报告列表 |
| POST | `/api/v1/quality/feedback` | 用户反馈 |

## 🧪 测试

```bash
# 后端健康检查
curl http://localhost:8000/health

# 测试视频生成
curl -X POST http://localhost:8000/api/v1/pipeline/generate \
  -H "Content-Type: application/json" \
  -d '{"topic":"为什么AI正在重塑教育行业","genre":"cognitive","target_length":"medium","style":"normal","voice_style":"documentary"}'

# 测试提示词优化
curl -X POST http://localhost:8000/api/v1/prompt/nl-input \
  -H "Content-Type: application/json" \
  -d '{"project_id":"test","text":"压抑黄昏山野","lang":"zh"}'
```

## 🗺️ 路线图

- [x] v0.3.0 — 8大模块完整搭建
- [x] v0.4.0 — Pipeline 视频生成流水线 + 一键生成主界面
- [ ] v1.0.0 — 接入真实 AI 服务（ComfyUI + Ollama + ChatTTS）
- [ ] v1.5.0 — 异步任务队列 + 实时进度推送
- [ ] v2.0.0 — 多租户 + 项目管理 + 云端部署
