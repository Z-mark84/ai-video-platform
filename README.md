# AI 长视频生成平台 - M1 提示词优化引擎

## 📋 项目概述

M1 是全平台的**底层核心引擎**，所有 AI 出图效果的源头。将用户口语化的模糊感性输入，自动转换为量化、具象、无主观词的标准绘图关键词。

### 核心能力

| 功能 | 状态 | 描述 |
|---|---|---|
| F1.1 双通道输入面板 | ✅ 完成 | 自然语言 + 标签双通道，实时双向同步 |
| F1.2 感性词汇映射词库 | ✅ 完成 | 20+ 情感/场景/风格词 → 光影/色彩/构图量化参数 |
| F1.3 冲突关键词清洗 | ✅ 完成 | 自动检测 8 组互斥描述（明亮+昏暗等） |
| F1.4 分类加权与自动补全 | ✅ 完成 | 场景/人物/融合三类专属约束 + SDXL 标准参数 |
| F1.8 认知视频专用模板库 | ✅ 完成 | 4 组预设模板（黄昏山野/湖面独处/城市夜景/林间独处） |
| F1.9 词库热更新 | ✅ 完成 | 运行时 CRUD 词映射，无需重启 |

### 技术栈

- **前端**: Vue3 + TypeScript + Vite + Naive UI
- **后端**: Python FastAPI
- **分词**: jieba
- **LLM** (预留): Qwen2.5-7B / OpenAI API

## 🚀 快速启动

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

## 📐 项目结构

```
ai-video-platform/
├── backend/
│   ├── app/
│   │   ├── __init__.py         # FastAPI 应用入口
│   │   ├── api/
│   │   │   └── prompt.py       # M1 所有 API 路由
│   │   ├── models/
│   │   │   └── prompt.py       # Pydantic 数据模型
│   │   └── services/
│   │       ├── mood_map.py     # 感性词汇映射词库
│   │       ├── conflict_checker.py  # 冲突清洗引擎
│   │       └── classification.py    # 分类加权与补全
│   ├── data/                   # 运行时数据（词库JSON持久化）
│   ├── main.py                 # 启动入口
│   └── requirements.txt
├── frontend/
│   ├── src/                    # Vue3 + TS 源码
│   └── ...
└── README.md
```

## 🔌 API 端点

| 方法 | 路径 | 功能 |
|---|---|---|
| POST | `/api/v1/prompt/nl-input` | 自然语言 → 结构化标签 |
| POST | `/api/v1/prompt/tag-input` | 标签输入 → 预览 |
| POST | `/api/v1/prompt/conflict-check` | 冲突检测 |
| POST | `/api/v1/prompt/optimize` | 完整优化 → 标准输出JSON |
| GET | `/api/v1/prompt/moods` | 感性词库列表 |
| GET | `/api/v1/prompt/moods/{mood}` | 单个词映射详情 |
| POST | `/api/v1/prompt/moods/{mood}` | 词库热更新 |
| POST | `/api/v1/prompt/moods/bulk` | 批量更新 |
| GET | `/api/v1/prompt/classifications` | 画面分类列表 |
| GET | `/api/v1/prompt/templates` | 模板列表 |

## 🧪 测试

```bash
# 后端健康检查
curl http://localhost:8000/health

# 自然语言输入测试
curl -X POST http://localhost:8000/api/v1/prompt/nl-input \
  -H "Content-Type: application/json" \
  -d '{"project_id":"test","text":"压抑黄昏山野","lang":"zh"}'
```
