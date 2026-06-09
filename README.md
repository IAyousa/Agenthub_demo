# AgentHub — 多 Agent 协作平台

AgentHub 是一个仿微信 PC 端交互风格的多 Agent 协作平台。用户可在 IM 聊天界面中与多个 AI Agent（Claude Code、Codex）协作编码，支持 Orchestrator 自动调度、实时流式回复、代码预览与 JWT 安全认证。

## 🌟 核心特性

- **IM 风格布局**：经典三栏式设计（会话列表 + 聊天窗口 + 代码预览）
- **多 Agent 协作**：Orchestrator 自动分析任务 → 分派给 Claude Code / Codex → 流式返回
- **Artifact 预览**：Agent 生成的 HTML/JS/CSS 代码自动检测并生成 iframe 实时预览
- **Monaco Editor**：内嵌 VS Code 同款编辑器，支持语法高亮与自适应布局
- **JWT 认证**：Spring Security + jjwt 无状态认证，开发环境零配置
- **双数据库支持**：默认 H2 文件数据库（零依赖），可选 PostgreSQL Profile

---

## 🚀 快速启动

### 前置条件

| 依赖 | 版本 | 说明 |
|------|------|------|
| Node.js | ≥18 | 前端构建 |
| JDK | 17+ | Java 后端 |
| Maven | 3.8+ | Java 构建 |
| Python | 3.11+ | Agent 服务 |
| Claude Code CLI | 最新 | AI Agent（需 ANTHROPIC_API_KEY） |
| Codex CLI | ≥0.137 | AI Agent（可选，需 OPENAI_API_KEY） |

### 1. 配置模板

```bash
# 复制配置模板（首次使用）
cp agent-service/.env.example agent-service/.env
cp backend-java/src/main/resources/application-secret.yml.example backend-java/src/main/resources/application-secret.yml
# 编辑 .env 填入你的 API Key
```

### 2. 启动 Agent 服务（Python）

```bash
cd agent-service
pip install -r requirements.txt
uvicorn main:app --port 8000 --reload
# API 文档: http://localhost:8000/docs
```

### 3. 启动后端服务（Java）

```bash
cd backend-java
mvn spring-boot:run
# 默认运行在 http://localhost:8080
# H2 控制台: http://localhost:8080/h2-console
```

### 4. 启动前端

```bash
cd frontend
npm install
npm run dev
# 访问 http://localhost:5173
```

### PostgreSQL（可选）

```bash
docker-compose up -d                                    # 启动 PostgreSQL
mvn spring-boot:run -Dspring-boot.run.profiles=pg       # 切换到 PG
```

---

## 📂 项目结构

```text
agenthub/
├── frontend/                 # Vue 3 前端项目
│   ├── src/
│   │   ├── components/       # 聊天、预览与通用组件
│   │   ├── stores/           # Pinia 状态管理
│   │   └── websocket/        # STOMP 客户端封装
├── backend-java/             # Spring Boot 主服务
│   ├── src/main/java/        # WebSocket, Controller, Service, Security
│   └── pom.xml               # Maven 配置
├── agent-service/            # Python FastAPI Agent 服务
│   ├── adapters/             # LLM 适配器 (Claude, Codex)
│   ├── prompts/              # System Prompt 模板
│   ├── orchestrator.py       # 多 Agent 任务编排器
│   └── main.py               # FastAPI 入口
├── docker-compose.yml        # PostgreSQL 本地开发容器
├── docs/                     # 技术框架与 API 规范文档
└── agent_collaboration/      # 开发过程记录
```

---

## 🔐 JWT 认证

```bash
# 注册
curl -X POST http://localhost:8080/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123456"}'

# 登录（获取 Token）
curl -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123456"}'

# 使用 Token 访问 API
curl http://localhost:8080/agents \
  -H "Authorization: Bearer <token>"
```

---

## 📝 开发规范

请参考 `docs/` 目录下的技术框架文档与 API 规范文档进行协同开发。
