# Agenthub - 多 Agent 协作平台

Agenthub 是一个仿微信 PC 端交互风格的多 Agent 协作平台。支持主 Agent (Orchestrator) 调度多个专业 Agent（如 Coder, Designer），并集成类似 Claude 的 Artifact 实时代码预览功能。

## 🌟 核心特性

- **IM 风格布局**：经典三栏式设计，支持响应式移动端适配。
- **多 Agent 协作**：支持切换不同的专业 Agent 进行对话。
- **Artifact 预览**：聊天流内生成 HTML/JS/CSS 代码并实时全屏预览。
- **Monaco Editor**：内置专业级代码编辑器，支持语法高亮与自适应布局。
- **实时渲染沙箱**：基于 Iframe 的安全代码运行环境。

---

## 🚀 前端部署 (Frontend)

前端基于 **Vue 3 + Vite + TypeScript + Tailwind CSS 4** 构建。

### 1. 环境准备
- [Node.js](https://nodejs.org/) (建议 v18.0.0 或更高版本)
- [npm](https://www.npmjs.com/) 或 [pnpm](https://pnpm.io/)

### 2. 安装依赖
进入前端目录并安装所需软件包：
```bash
cd frontend
npm install
```

### 3. 开发环境运行
启动 Vite 开发服务器：
```bash
npm run dev
```
启动后，可在浏览器访问 `http://localhost:5173` (或终端显示的其它端口) 进行预览。

### 4. 项目打包
构建生产环境版本：
```bash
npm run build
```
打包产物将生成在 `frontend/dist` 目录下。

---

## 🛠️ 后端部署 (Backend)

后端基于 **FastAPI + Python 3.10+** 构建。

### 1. 环境准备
- [Python 3.10+](https://www.python.org/)
- 建议使用 `venv` 虚拟环境

### 2. 安装依赖
进入后端目录并安装依赖项：
```bash
cd backend
python -m venv venv
# Windows 激活
.\venv\Scripts\activate
# Linux/macOS 激活
source venv/bin/activate

pip install -r requirements.txt
```

### 3. 运行服务
启动 FastAPI 开发服务器：
```bash
uvicorn app.main:app --reload
```
API 文档可通过 `http://localhost:8000/docs` 访问。

---

## 📂 项目结构

```text
├── frontend/           # Vue 3 前端项目
│   ├── src/
│   │   ├── components/ # 核心组件 (Chat, Artifact, Layout)
│   │   ├── stores/     # Pinia 状态管理
│   │   └── App.vue     # 布局主入口
├── backend/            # FastAPI 后端项目
│   ├── app/
│   │   ├── api/        # 路由定义
│   │   ├── models/     # 数据模型 (Pydantic)
│   │   └── main.py     # 入口文件
└── docs/               # 设计文档与 API 规范
```

---

## 📝 开发规范
请参考项目内部文档或 `api_spec.md` 进行协同开发。
