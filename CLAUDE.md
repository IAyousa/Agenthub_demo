# AgentHub — Multi-Agent Collaboration Platform

## Project Identity

- **Name**: AgentHub (package name: `agenthub`)
- **Concept**: IM-style (WeChat PC-inspired) chat interface where users collaborate with multiple AI Agents. Agents generate code/web artifacts with inline preview and editing.
- **Team**: 4 CS juniors. Primary language Java/Spring Boot, Python basics with AI-assist.
- **Repo**: `D:\HuaweiMoveData\Users\Yao\Desktop\Trae_project`
- **Branch**: `dev` (main: `main`)
- **Git user**: IAyousa

## Architecture (3-Layer)

```
Vue 3 Frontend (localhost:5173)
  --REST/STOMP-WS--> Spring Boot (localhost:8080)
                       --HTTP+SSE--> FastAPI Agent Service (localhost:8000)
                       \                        /
                        +--- H2 File (AUTO_SERVER) ---+
                                      |
                                      └── External LLM APIs (Claude, Codex, DeepSeek)
```

- **Frontend**: Vue 3.5 + TypeScript + Pinia + Tailwind CSS 4 + Vite 8
- **Backend**: Spring Boot 3.2.5 + Java 17 + H2 (dev, AUTO_SERVER=TRUE file mode, shared with Python) / PostgreSQL (doc plan) + JPA
- **Agent Service**: FastAPI 0.109 + Python 3.11 + LangChain/LangGraph
- **Communication**: STOMP over WebSocket (frontend↔backend), REST API, SSE streaming (backend↔agent)

## Project Structure (Actual Code)

```
frontend/                          # Vue 3 Frontend — ~80% complete (UI + routing done, pending real API integration)
├── src/
│   ├── main.ts                    # Entry: Pinia + Vue + Monaco worker config
│   ├── App.vue                    # Root: SideBar + RouterView + Transition (view switching via Vue Router)
│   ├── style.css                  # @import "tailwindcss"
│   ├── env.d.ts                   # Vue SFC type declarations
│   ├── api/
│   │   └── index.ts               # Axios instance: baseURL localhost:8080, timeout 30s, request/response interceptors
│   ├── router/
│   │   └── index.ts               # Vue Router 4: /chat/:conversationId (dynamic), /office (lazy-loaded), root redirect
│   ├── stores/chat.ts             # Pinia store: conversations, messages, officeMembers, artifact state (currently mock data)
│   ├── views/
│   │   ├── ChatView.vue           # Route-level container: watch route.params → chatStore.selectConversation() {immediate}
│   │   └── OfficeView.vue         # Route-level container for office scene (P2 bottom drawer chat panel pending)
│   └── components/
│       ├── chat/
│       │   ├── ChatList.vue       # Conversation list (useRouter push on select, auto-route by conversation.type)
│       │   ├── ChatWindow.vue     # Main chat area: header + message list + MessageInput. Simulates AI via setTimeout
│       │   ├── ChatMessage.vue    # Message bubble renderer (text/code/artifact_preview)
│       │   ├── MessageInput.vue   # Shared input component: toolbar + textarea + send button (reusable in OfficeView)
│       │   ├── CodeEditor.vue    # Monaco Editor wrapper (vs-dark, readOnly, copy button, ResizeObserver)
│       │   ├── ArtifactSandbox.vue # Iframe sandbox (srcdoc), renders HTML/CSS/JS previews
│       │   └── ArtifactWindow.vue  # Full-screen overlay: preview/code toggle, back button
│       ├── layout/SideBar.vue     # Left nav bar (dark indigo): chat/office icons, uses useRoute/useRouter for active state
│       └── office/
│           ├── OfficeView.vue     # SVG office scene: 8 seats, 3D desk, door, GSAP kick/walk animations
│           ├── CreateOfficeModal.vue # Modal for creating new office rooms (P2)
│           ├── OfficeChair.vue    # SVG chair component
│           └── StickFigure.vue    # SVG character: idle breathe, eye blink, walk, kick, shocked states
├── package.json                   # vue 3.5, pinia 3, gsap 3, monaco-editor, @stomp/stompjs, axios, tailwindcss 4
├── vite.config.ts                 # Vue + Tailwind plugins
└── index.html

backend-java/                      # Spring Boot — entities + repos done, controllers/services WIP
├── src/main/java/com/agenthub/
│   ├── AgenthubApplication.java  # @SpringBootApplication entry
│   ├── config/
│   │   ├── WebSocketConfig.java   # STOMP: /app prefix, /topic broker, /ws-chat endpoint + SockJS
│   │   └── CorsConfig.java        # CorsFilter Bean, reads cors.allowed-origins from yml
│   ├── controller/
│   │   └── WebSocketController.java # @MessageMapping("/chat.send") — empty handler
│   ├── dto/
│   │   └── SendMessageRequest.java # conversationId, content, agentId (Lombok @Data)
│   ├── model/
│   │   ├── User.java              # JPA entity: id, username, password, avatarUrl
│   │   ├── Conversation.java      # JPA entity: id, title, type, agents (ManyToMany → conv_agents)
│   │   ├── Message.java           # JPA entity: id, conversationId, senderId/Type, content, messageType, isPinned
│   │   └── Agent.java             # JPA entity: id, name, type, avatarUrl, systemPrompt, capabilities
│   ├── repository/
│   │   ├── UserRepository.java
│   │   ├── ConversationRepository.java
│   │   ├── MessageRepository.java
│   │   └── AgentRepository.java
│   └── service/
│       └── AgentGatewayService.java # WebClient baseUrl=localhost:8000, sendToAgent() unimplemented
├── src/main/resources/
│   ├── application.yml            # H2 file-based DB (AUTO_SERVER=TRUE), JPA ddl-auto update, CORS config, port 8080
│   └── data.sql                   # Seed data: Claude Code + Codex agents
└── pom.xml                        # SB 3.2.5: web, websocket, jpa, webflux, postgresql, h2, lombok

agent-service/                     # FastAPI — ~65% complete (full layered architecture, pending Orchestrator)
├── main.py                        # FastAPI app, CORS, routers at /api/v1/{agents,conversations,messages,artifacts}
├── models.py                      # Pydantic: Agent, Conversation, Message, CodeBlock, DiffBlock, MessageContent (DB-agnostic)
├── config.py                      # Settings (pydantic-settings): Claude/Codex/DeepSeek API keys, H2 DB path, timeout 120s
├── adapters/
│   ├── base_adapter.py            # Abstract: async chat(message, history, system_prompt) — stream token yield
│   ├── adapter_factory.py         # Registry pattern: get_adapter(agent_type) returns matching adapter instance
│   ├── claude_adapter.py          # Anthropic Messages API adapter, streaming via async generator
│   ├── codex_adapter.py           # OpenAI Chat Completions API adapter, streaming via async generator
│   └── deepseek_adapter.py        # DeepSeek V4 adapter, OpenAI-compatible format, streaming via async generator
├── prompts/system_prompts.py      # 2 stub prompts: coder, designer (pending real prompt engineering)
├── app/
│   ├── api/endpoints/
│   │   ├── __init__.py
│   │   ├── agents.py              # Full CRUD: GET / (list from DB), GET /{id}, POST / (create)
│   │   ├── conversations.py       # Full CRUD: GET /, POST /, GET /{id}, PATCH /{id}, DELETE /{id}
│   │   ├── messages.py            # POST /chat/stream — routes to Orchestrator → adapter → real SSE streaming
│   │   └── artifacts.py           # Full CRUD: POST /upload, GET /{id}, GET /conversations/{id}/artifacts
│   └── db/                        # Repository Pattern data access layer
│       ├── connection.py          # JVM bridge: JPype + jaydebeapi → H2 AUTO_SERVER=TRUE (shared with Java backend)
│       └── repository.py          # Parameterized queries: agents/conversations/messages CRUD (H2 JDBC implementation)
├── agenthub.db                    # Shared H2 database file (read/write by both Java & Python processes)
├── requirements.txt               # fastapi, pydantic-settings, jpype1, jaydebeapi (H2 JDBC bridge)
└── .env                           # CLAUDE_API_KEY, CODEX_API_KEY, DEEPSEEK_API_KEY (gitignored)

docs/                              # 6 design docs
├── 项目概述与技术栈总览.md
├── 架构拓扑图与项目目录结构.md
├── 数据模型设计.md
├── API 契约定义与通信协议规范.md    # Full REST + WebSocket + SSE contract (updated 2026-05-26)
├── api_spec.md
└── 基础设施配置.md

agent_collaboration/               # Internal team docs (not pushed to remote)
├── 团队任务分配.md                              # 4-member task assignment (v1.2), sprint goals, Agent Service migration tasks
├── 开发过程记录-JPA数据层搭建.md
├── 开发过程记录-CORS配置与接口文档更新.md
├── 开发过程记录-团队任务分配与群聊方案设计.md
├── 开发过程记录-C1-Axios实例配置.md
├── 开发过程记录-C6-MessageInput组件提取.md
├── 开发过程记录-C8-ChatList会话列表改造.md
├── 开发过程记录-C9-Vue-Router路由配置.md
├── 开发过程记录-Git-Commit模板配置.md
├── 开发过程记录-数据库持久化机制分析.md
├── 开发过程记录-Agent-Service分层架构说明文档升级.md
```

## Current State Summary

### Working (Frontend — UI prototype ~80%)
- Full IM-style 3-column layout (SideBar/ChatList/ChatWindow) renders
- Chat messages: text bubbles, code blocks (Monaco Editor), artifact preview cards
- Artifact system: click card → full-screen overlay → preview (iframe srcdoc) / code toggle
- Office view: SVG scene with 8 seats, animated stick figures, GSAP kick-out/walk-in
- Vue Router 4 configured: `/chat/:conversationId` dynamic route, `/office` lazy-loaded, root redirect
- View switching via URL routing (not Pinia state): SideBar uses useRoute/useRouter, ChatList auto-routes by conversation.type
- MessageInput extracted as shared component (reusable in ChatView and OfficeView)
- Axios HTTP client configured (`src/api/index.ts`): baseURL localhost:8080, interceptors ready
- **All data is mock/hardcoded** — ChatList shows conversations (not agents), ChatWindow uses simulated AI responses, no real API calls yet

### Backend (Java — ~35%)
- Spring Boot app compiles and starts
- JPA entities: User, Conversation, Message, Agent (with ManyToMany conv_agents join table)
- JPA repositories: 4 data access interfaces
- seed data: `data.sql` preloads Claude Code + Codex agents
- CorsConfig: CorsFilter Bean covering all paths (Servlet Filter layer)
- WebSocket STOMP configured but handlers are empty stubs
- AgentGatewayService has WebClient but sendToAgent() is unimplemented
- **Missing**: SecurityConfig, REST controllers, services, DTOs
- Database: H2 file-based (AUTO_SERVER=TRUE, shared with Python Agent Service), docs specify PostgreSQL for production

### Agent Service (Python — ~65%)
- FastAPI app starts, all 4 endpoint groups return real data from shared H2 database
- **Full layered architecture**: API endpoints → Pydantic models → Adapter cluster → Repository interface → Repository impl (JDBC) → Connection manager (JVM bridge)
- Repository Pattern: data access interfaces are DB-agnostic, current implementation uses JPype + jaydebeapi JDBC bridge to H2 `AUTO_SERVER=TRUE` (shared with Java backend)
- 3 LLM adapters: Claude (Anthropic Messages API), Codex (OpenAI Chat Completions), DeepSeek (OpenAI-compatible)
- Pydantic models layer is DB-agnostic — zero changes needed when migrating to PostgreSQL
- `POST /api/v1/messages/chat/stream` returns mock SSE stream (Orchestrator scheduling not yet implemented)
- Phase 1 migration plan documented: replace ~200 lines of JDBC bridge code with asyncpg + SQLAlchemy for PostgreSQL, zero changes to upper layers
- **Missing**: Orchestrator multi-agent scheduler, real prompt engineering, real LLM streaming integration

### Key Technical Decisions
- **MVP simplification**: H2 instead of PostgreSQL, in-memory session management (no Redis), local filesystem storage (no MinIO)
- **Vue Router 4 configured**: `/chat/:conversationId` dynamic route + `/office` lazy-loaded route, view switching driven by URL (previously Pinia state-based)
- **No authentication** in MVP — docs reserve it for P1
- **CORS strategy**: CorsFilter Bean (Servlet Filter layer) for dev, Nginx reverse proxy for production
- **Chat vs Office**: Two UI skins (ChatView/OfficeView) sharing one message engine (Pinia store + WebSocket client + components)
- **Agent dispatch**: Orchestrator pattern — Python Agent Service handles scheduling transparently, frontend only sends `{conversationId, content}`
- **Monaco Editor workers** configured as Vite web workers in main.ts
- **GSAP** used for office animations (timeline-based kick/walk sequences)
- **dev branch** is the active development branch; main has only initial commits
