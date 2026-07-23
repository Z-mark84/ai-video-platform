# 🚀 部署指南 — GitHub Pages

## 适用场景

国内用户无需 VPN，GitHub Pages 可直接访问（速度中等，CDN 加速）。

本项目已配置自动部署：推送代码到 `main` 分支后，GitHub Actions 自动构建并发布。

---

## 第一步：推送到 GitHub

```bash
cd ai-video-platform

# 在 github.com/new 先创建空仓库（如：ai-video-platform），然后：
git remote add origin https://github.com/你的用户名/ai-video-platform.git
git add .
git commit -m "v0.4.0: GitHub Pages 部署就绪"
git branch -M main
git push -u origin main
```

## 第二步：启用 GitHub Pages

1. 打开仓库 → **Settings** → **Pages**
2. **Source** 选择 `GitHub Actions`
3. 推送后 Actions 自动运行，完成后页面地址：
   ```
   https://你的用户名.github.io/ai-video-platform/
   ```

## 第三步：验证

等待 Actions 完成（约 2-3 分钟），打开上面的地址即可看到 AI 长视频生成平台。

> 🎬 默认进入「视频生成」页面，所有功能在 Demo 模式下运行（浏览器内置模拟数据），无需后端。

---

## 本地运行（开发用）

```bash
# 终端1 — 后端
cd ai-video-platform/backend
pip install -r requirements.txt
python main.py

# 终端2 — 前端
cd ai-video-platform/frontend
npm install
npm run dev

# 浏览器 → http://localhost:5173
```

---

## 技术说明

| 项目 | 说明 |
|------|------|
| **托管方式** | GitHub Pages（纯静态，无后端） |
| **自动部署** | GitHub Actions（`.github/workflows/deploy.yml`） |
| **前端框架** | Vue 3 + Vite + Naive UI |
| **Demo 模式** | 后端不可用时自动回退到浏览器内置模拟流水线 |
| **base 路径** | `/ai-video-platform/`（已在 vite.config.ts 配置） |
