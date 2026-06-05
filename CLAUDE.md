# AgentHub — Multi-Agent Collaboration Platform

## Project Identity

- **Name**: AgentHub (package name: `agenthub`)
- **Concept**: IM-style (WeChat PC-inspired) chat interface where users collaborate with multiple AI Agents running locally via CLI (Claude Code / OpenAI Codex), generating code and artifacts with inline preview.
- **Team**: 4 CS juniors. Primary Java/Spring Boot, Python basics with AI-assist.
- **Repo**: `D:\HuaweiMoveData\Users\Yao\Desktop\Trae_project`
- **Branch**: `dev` (main: `main`)
- **Git user**: IAyousa

## Architecture (3-Layer)

```
Vue 3 Frontend (localhost:5173)
  --REST/STOMP-WS--> Spring Boot (localhost:8080)
                       --HTTP+SSE--> FastAPI Agent Service (localhost:8000)
                                      --subprocess--> Claude Code / Codex CLI (local machine)
```

- **Frontend**: Vue 3.5 + TypeScript + Pinia + Vue Router 4 + Tailwind CSS 4 + Vite 8
- **Backend**: Spring Boot 3.2.5 + Java 17 + H2 (file mode, sole data source) + JPA + STOMP/WebSocket
- **Agent Service**: FastAPI 0.109 + Python 3.11, stateless gateway, invokes local CLI tools via asyncio subprocess, no database access
- **Agent Execution**: Local CLI — `claude -p "prompt"` / `codex exec "prompt"`, stdout streaming
- **Communication**: STOMP over WebSocket (frontend↔backend), HTTP+SSE (backend↔agent)

## Project Structure (Actual Code)

```
frontend/                          # Vue 3 Frontend — ~90% complete
├── src/
│   ├── main.ts                    # Entry: Pinia + Vue + Router + Monaco worker config
│   ├── App.vue                    # Root: SideBar + <RouterView v-slot> + Transition animation
│   ├── style.css                  # @import "tailwindcss"
│   ├── env.d.ts                   # Vue SFC type declarations
│   ├── api/
│   │   └── index.ts               # Axios instance: baseURL localhost:8080, timeout 30s, interceptors
│   ├── router/
│   │   └── index.ts               # Vue Router 4: / → redirect /chat/conv_frontend_001, /chat/:conversationId (ChatView), /office (lazy OfficeView)
│   ├── stores/chat.ts             # Pinia store: conversations, conversationList, agents, offices, artifact state, WebSocket send/stream callbacks
│   ├── websocket/
│   │   └── wsClient.ts            # STOMP client singleton: connect/subscribe/sendMessage via SockJS, auto-reconnect, heartbeat
│   ├── views/
│   │   ├── ChatView.vue           # Route container: watch route.params → selectConversation() {immediate}, onMounted → initWebSocket()
│   │   └── OfficeView.vue         # Thin wrapper around office/OfficeView.vue component
│   └── components/
│       ├── chat/
│       │   ├── ChatList.vue       # Conversation list: search, create btn, route push on select, agent tags, relative time
│       │   ├── ChatWindow.vue     # Main chat area: header + message list + MessageInput. Real WebSocket/STOMP send, offline toast
│       │   ├── ChatMessage.vue    # Message bubble (text/code/artifact_preview), avatar, click→artifact overlay
│       │   ├── MessageInput.vue   # Shared input: toolbar + textarea + send btn, emits 'send'. Keyed by conversationId for auto-clear
│       │   ├── CodeEditor.vue     # Monaco Editor: vs-dark, copy btn, ResizeObserver, reactive code/lang props
│       │   ├── ArtifactSandbox.vue # Iframe sandbox (srcdoc), HTML/CSS/JS/TS preview with error handling
│       │   └── ArtifactWindow.vue  # Full-screen overlay: preview/code toggle, back button
│       ├── layout/SideBar.vue     # Left nav (dark indigo): chat/office/settings icons, useRoute/useRouter for active state
│       └── office/
│           ├── OfficeView.vue     # SVG office: 8 seats, 3D desks, door, plant decor, GSAP kick/walk, invite panel, multi-office management
│           ├── CreateOfficeModal.vue # Modal for creating new office rooms (name/description/maxMembers/theme)
│           ├── OfficeChair.vue    # SVG chair with backrest and legs
│           └── StickFigure.vue    # Detailed SVG character: idle breathe, eye blink, walk/kick/shocked, hair/clothing/face per role
├── package.json                   # vue 3.5, pinia 3, vue-router 4.6, gsap 3, monaco-editor 0.55, @stomp/stompjs 7, sockjs-client, axios, tailwind 4, TS 6, Vite 8
├── vite.config.ts                 # Vue + @tailwindcss/vite plugins only (no proxy, no @ alias)
└── index.html

backend-java/                      # Spring Boot — ~55% complete (data + service + agent/artifact REST done)
├── src/main/java/com/agenthub/
│   ├── AgenthubApplication.java  # @SpringBootApplication entry
│   ├── config/
│   │   ├── WebSocketConfig.java   # STOMP: /app prefix, /topic broker, /ws-chat + SockJS, CORS origins from yml
│   │   ├── CorsConfig.java        # CorsFilter Bean (Servlet Filter layer, reads cors.allowed-origins)
│   │   ├── ArtifactConfig.java    # Static resource mapping: /artifacts/** → file:./artifacts/
│   │   └── SecurityConfig.java    # Comment placeholder (Spring Security + JWT reserved for P1)
│   ├── controller/
│   │   ├── WebSocketController.java # @MessageMapping("/chat.send") — handler filled: save→route→context→SSE→STOMP push
│   │   ├── AgentController.java   # CRUD: GET/POST /agents, GET /agents/{id}. Type validation, avatarUrl, isBuiltin detection
│   │   ├── ArtifactController.java # CRUD: POST/GET/DELETE /artifacts, GET /conversations/{id}/artifacts. Path traversal protection
│   │   ├── ConversationController.java # CRUD: 7 REST endpoints for conversation + agent management
│   │   └── MessageController.java  # Paginated message history + pin/unpin with conversation-scoped validation
│   ├── dto/
│   │   ├── SendMessageRequest.java # conversationId, content, agentId (Lombok @Data)
│   │   ├── MessageChunk.java      # content, isComplete, agentId, agentName, messageType, messageId, type
│   │   ├── ArtifactDTO.java       # id, filename, fileSize, conversationId, messageId, createdAt
│   │   ├── ConversationDTO.java   # id, title, type, agentIds, createdAt, updatedAt
│   │   └── PinRequest.java        # pinned: boolean
│   ├── model/                     # User, Conversation, Message, Agent, Artifact JPA entities. @PrePersist UUID + timestamps. Message has 2 DB indexes.
│   ├── repository/                # 5 JPA data access interfaces (User, Conversation, Message, Agent, Artifact)
│   └── service/
│       ├── AgentGatewayService.java # FULL: WebClient SSE parser, AgentToken callback (token/finish/error), aligned to /api/agent/chat
│       ├── ArtifactService.java   # Upload/query/download/delete, @PostConstruct orphan recovery, path traversal protection
│       ├── ConversationService.java # FULL: CRUD, agent add/remove, archive, user-scoped queries
│       ├── MessageService.java    # FULL: send, paginated history, pin/unpin, context assembly
│       └── WebSocketSessionManager.java # STOMP session management via SimpMessagingTemplate
├── src/main/resources/
│   ├── application.yml            # H2 file-based DB (AUTO_SERVER=TRUE), JPA ddl-auto update, CORS, port 8080
│   └── data.sql                   # Seed data: Claude Code + Codex agents (H2 MERGE INTO syntax)
└── pom.xml                        # SB 3.2.5: web, websocket, jpa, webflux, postgresql, h2, lombok

agent-service/                     # FastAPI — ~75% complete, stateless gateway, no DB access
├── main.py                        # FULL: FastAPI app, CORS, /api/agent router, global error handlers (400/404/500), /health with uptime
├── models.py                      # FULL: AgentChatRequest (incl. availableAgents P2 field), AgentChatResponse, HealthResponse, ErrorResponse
├── config.py                      # FULL: pydantic-settings + AGENT_REGISTRY fallback cache (4 agents), Claude/Codex CLI commands, timeout 300s
├── adapters/
│   ├── base_adapter.py            # FULL: strip_ansi(), build_prompt(), chat_stream() abstract, chunk contract (msg_start/msg_chunk/msg_end/error)
│   ├── adapter_factory.py         # FULL: ADAPTER_MAP {claude_code, codex, custom} → ValueError on unknown type
│   ├── claude_adapter.py          # FULL: asyncio subprocess claude -p "prompt", stdout streaming, stderr drain, timeout/kill, exit code check
│   └── codex_adapter.py           # FULL: asyncio subprocess codex exec "prompt", same pattern with error handling
├── prompts/
│   └── system_prompts.py          # FULL: 8 role prompts (claude_code/codex/orchestrator/custom + coder/designer/reviewer/architect fallback)
├── app/api/endpoints/
│   ├── messages.py                # FULL: POST /chat, stream/non-stream dispatch, auto-lookup systemPrompt from templates, SSE format per contract
│   └── agents.py                  # NEW: get_agents()/get_agent()/agent_exists() utility for AGENT_REGISTRY lookups
├── requirements.txt               # fastapi, uvicorn, httpx, pydantic, pydantic-settings, sse-starlette, langchain, langgraph, etc.
└── .env                           # ANTHROPIC_API_KEY, OPENAI_API_KEY (gitignored; CLI tools read from system env, Agent Service never touches keys)

> **Agent metadata architecture**: Java DB `agents` table is the single source of truth. Python `AGENT_REGISTRY` in config.py is a fallback cache. Java WebSocketController now sends `systemPrompt` from DB (previously hardcoded ""). P1: Java carries `availableAgents[]` in request. P1-late: Redis shared cache.
> **Doc vs code gaps**: `http_adapter.py` (custom Agent HTTP API, D13) and `orchestrator.py` (multi-agent scheduling, P2) — not implemented yet.

docs/                              # 5 design docs (v1.0)
├── 项目概述与技术栈总览.md
├── 架构拓扑图与项目目录结构.md
├── 数据模型设计.md
├── API 契约定义与通信协议规范.md
└── 基础设施配置.md                 # Updated: H2 config + quick-start checklist + MVP annotations
```

## Current State Summary

### Frontend — ~90% (UI + routing + WebSocket send done, REST API calls pending)
- Vue Router 4: `/chat/:conversationId` (ChatView), `/office` (lazy), root redirect
- 3-col IM layout: SideBar (route-based active state) + ChatList (route push, create conv) + ChatWindow (auto-scroll, MessageInput decoupled)
- Message types: text / code (Monaco Editor) / artifact_preview (click→full-screen overlay)
- **C7 complete**: ChatWindow connected to real STOMP/WebSocket, replaced setTimeout mock
- WebSocket initialized in `ChatView.onMounted`, `sendMessage()` checks `ws.connected` — sends via WS or shows offline toast
- Offline toast: floating "Service connection issue, please retry" prompt (4s auto-dismiss, manual X close, dismiss on conversation switch)
- Conversation switch: auto-cleans loading/error/streaming state, MessageInput re-created via `:key` for input clear
- Office scene: SVG 8-seat 3D desk layout, GSAP kick-out/walk-in animations, multi-office management (create/disband/switch), invite panel
- Axios configured (interceptors ready), API calls gracefully degrade to mock data on failure
- **Pending**: REST API conversation list/agent list loading, conversation creation API wiring

### Backend Java — ~65% (data + service + REST controllers + WebSocket handler all done)
- Spring Boot compiles and starts on port 8080
- **Config layer done**: WebSocketConfig (STOMP + SockJS at `/ws-chat`), CorsConfig (Servlet Filter), ArtifactConfig (static resource mapping), SecurityConfig (placeholder, P1)
- **Data layer done**: 5 JPA entities (all with @PrePersist UUID generation + timestamps), Message entity has 2 DB indexes
- 5 Repository interfaces (User, Conversation, Message, Agent, Artifact + custom queries)
- `data.sql` seeds Claude Code + Codex agents (H2 `MERGE INTO` syntax)
- **Service layer done**: ConversationService, MessageService, AgentGatewayService, ArtifactService, WebSocketSessionManager (STOMP session management)
- **REST controllers done**: AgentController, ArtifactController, ConversationController (7 endpoints), MessageController (paginated messages + pin with conversation-scoped validation)
- **WebSocketController handler filled**: save message → agent routing → context build → AgentGatewayService SSE call → STOMP push to topic
- AgentGatewayService SSE parser fixed: handles Netty buffer chunking + missing `data:` prefix
- H2 file-based DB, Java-exclusive (Python is stateless gateway, no DB access)
- **Pending**: Frontend REST API wiring for conversation/agent list loading, end-to-end user auth

### Agent Service — ~80% (adapters + prompts + agent registry all done)
- FastAPI starts, single router `/api/agent` with `POST /chat`
- **ClaudeAdapter**: `asyncio.subprocess` → `claude -p "prompt"` → stdout line-by-line SSE
- **CodexAdapter**: same pattern with `codex exec "prompt"`
- **System prompts**: 8 role templates (claude_code/codex/orchestrator/custom + 4 legacy fallback). Auto-lookup by agentType when Java sends empty systemPrompt.
- **AGENT_REGISTRY**: 4-agent fallback cache in config.py, with `agents.py` utility module for lookup. Java DB is source of truth.
- Stream: SSE `data: {"token":"...", "finish":false, "agentId":"...", "agentName":"..."}`, non-stream: JSON
- `/health` endpoint: returns `status`, `version`, `uptime`
- Global error handlers: 400/404/500 with unified `{error, message, timestamp, path}` format
- **No database access** — receives pre-assembled `context` (chat history text) from Java, returns token stream
- **Pending**: `http_adapter.py` (D13, custom Agent HTTP API), `orchestrator.py` (P2, multi-agent scheduling)

### Doc-vs-Code Gaps
- **Python is stateless gateway** — docs originally planned Python sharing H2 via JPype/jaydebeapi. Now pure CLI subprocess forwarding, zero DB access. Planned agents/conversations/artifacts CRUD endpoints were removed.
- **Local CLI instead of cloud API** — docs `config.py` planned `CLAUDE_API_KEY`/`CODEX_API_KEY` for direct Anthropic/OpenAI HTTP calls. Now uses asyncio subprocess with local CLI; API keys read by CLI tools from system env, Agent Service never touches them.
- **Docs planned but unimplemented**: `http_adapter.py` (D13), `orchestrator.py` (P2)
- **H2 instead of PostgreSQL** — docs specify PostgreSQL datasource, actual MVP uses H2 file mode. P1 migration: change 5 lines in YAML + 2 SQL statements.
- **Frontend is TypeScript, not JavaScript** — docs say `JavaScript ES2022+`, actual code is all `.ts` / `<script setup lang="ts">`
- **WebSocket endpoint is `/ws-chat`** — docs API contract says `/ws`, actual code uses `/ws-chat`
- **SendMessageRequest DTO** — actual code has `agentId` field, but API contract says frontend should NOT send `agentType`/`agentId` (Orchestrator handles scheduling). Needs alignment during implementation.
- **No Redis/MinIO/auth** in MVP — reserved for P1
- **Vue Router 4** drives view switching (URL shareable)
- **Monaco Editor** (Vite web worker loading) + **GSAP** animations
- **dev branch** is the active development branch
