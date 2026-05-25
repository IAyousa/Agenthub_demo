# Agenthub - 多 Agent 协作平台

Agenthub 是一个仿微信 PC 端交互风格的多 Agent 协作平台。支持主 Agent (Orchestrator) 调度多个专业 Agent（如 Coder, Designer），并集成类似 Claude 的 Artifact 实时代码预览功能。

## 🌟 核心特性

- **IM 风格布局**：经典三栏式设计，支持响应式移动端适配。
- **双后端协作架构**：工程侧用 Java 处理业务逻辑与长连接，AI 侧用 Python 调度大模型。
- **Artifact 预览**：聊天流内生成 HTML/JS/CSS 代码并实时全屏预览。
- **Monaco Editor**：内置专业级代码编辑器，支持语法高亮与自适应布局。
- **实时渲染沙箱**：基于 Iframe 的安全代码运行环境。

---

## 🚀 前端部署 (Frontend)

前端基于 **Vue 3 + Vite + TypeScript + Tailwind CSS 4** 构建。

### 1. 环境准备
- [Node.js](https://nodejs.org/) (建议 v18.0.0 或更高版本)
- [npm](https://www.npmjs.com/)

### 2. 安装依赖
```bash
cd frontend
npm install
```

### 3. 开发环境运行
```bash
npm run dev
```
访问 `http://localhost:5173` 进行预览。

---

## ☕ 后端主服务 (Backend-Java)

基于 **Spring Boot 3.2.x + Java 17**，负责业务逻辑、WebSocket(STOMP) 与数据库持久化。

### 1. 环境准备
- [JDK 17+](https://adoptium.net/)
- [Maven 3.8+](https://maven.apache.org/)
- [PostgreSQL 15+](https://www.postgresql.org/)

### 2. 运行服务
```bash
cd backend-java
mvn spring-boot:run
```
默认运行在 `http://localhost:8080`。

---

## 🤖 Agent 服务 (Agent-Service)

基于 **FastAPI + Python 3.11+**，负责 LLM 适配与 Agent 调度逻辑。

### 1. 环境准备
- [Python 3.11+](https://www.python.org/)
- 建议使用 `venv` 虚拟环境

### 2. 安装依赖
```bash
cd agent-service
python -m venv venv
# Windows 激活
.\venv\Scripts\activate
# Linux/macOS 激活
source venv/bin/activate

pip install -r requirements.txt
```

### 3. 运行服务
```bash
uvicorn main:app --reload --port 8000
```
API 文档访问 `http://localhost:8000/docs`。

---

## 📂 项目结构

```text
agenthub/
├── frontend/           # Vue 3 前端项目
│   ├── src/
│   │   ├── components/ # 聊天、预览与通用组件
│   │   ├── stores/     # Pinia 状态管理
│   │   └── websocket/  # STOMP 客户端封装
├── backend-java/       # Spring Boot 主服务 (工程中台)
│   ├── src/main/java/  # WebSocket, Controller, Service, Model
│   └── pom.xml         # Maven 配置
├── agent-service/      # Python FastAPI 服务 (AI 适配层)
│   ├── adapters/       # LLM 适配器 (Claude, etc.)
│   ├── prompts/        # System Prompt 模板
│   └── main.py         # FastAPI 入口
└── docs/               # 技术框架与 API 规范文档
```

---

## 📝 开发规范
请参考 [项目技术框架.md](file:///d:/HuaweiMoveData/Users/Yao/Desktop/Trae_project/项目技术框架.md) 与 [架构拓扑图与项目目录结构.md](file:///d:/HuaweiMoveData/Users/Yao/Desktop/Trae_project/架构拓扑图与项目目录结构.md) 进行协同开发。
