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
│   │   ├── ArtifactController.java # CRUD + POST /internal/artifacts (Python→Java upload), WebSocket push preview_card
│   │   ├── ConversationController.java # CRUD: 7 REST endpoints for conversation + agent management
│   │   └── MessageController.java  # Paginated message history + pin/unpin with conversation-scoped validation
│   ├── dto/
│   │   ├── SendMessageRequest.java # conversationId, content, agentId (Lombok @Data)
│   │   ├── MessageChunk.java      # content, isComplete, agentId, agentName, messageType, messageId, type
│   │   ├── ArtifactDTO.java       # id, filename, fileSize, conversationId, messageId, createdAt
│   │   ├── ConversationDTO.java   # id, title, type, agentIds, createdAt, updatedAt
│   │   ├── InternalArtifactRequest.java # conversationId, messageId, filename, content, contentType — Python→Java artifact upload
│   │   └── PinRequest.java        # pinned: boolean
│   ├── model/                     # User, Conversation, Message, Agent, Artifact JPA entities. @PrePersist UUID + timestamps. Message has 2 DB indexes.
│   ├── repository/                # 5 JPA data access interfaces (User, Conversation, Message, Agent, Artifact)
│   └── service/
│       ├── AgentGatewayService.java # FULL: WebClient SSE parser, AgentToken callback (token/finish/error), aligned to /api/agent/chat
│       ├── ArtifactService.java   # Upload(MultipartFile+text content)/query/download/delete, orphan recovery, path traversal protection
│       ├── ConversationService.java # FULL: CRUD, agent add/remove, archive, user-scoped queries
│       ├── MessageService.java    # FULL: send, paginated history, pin/unpin, context assembly
│       └── WebSocketSessionManager.java # STOMP session management via SimpMessagingTemplate
├── src/main/resources/
│   ├── application.yml            # H2 file-based DB (AUTO_SERVER=TRUE), JPA ddl-auto update, CORS, port 8080
│   └── data.sql                   # Seed data: Claude Code + Codex agents (H2 MERGE INTO syntax)
└── pom.xml                        # SB 3.2.5: web, websocket, jpa, webflux, postgresql, h2, lombok

agent-service/                     # FastAPI — ~80% complete, stateless gateway, no DB access
├── main.py                        # FULL: FastAPI app, CORS, /api/agent router, global error handlers (400/404/500), /health with uptime
├── models.py                      # FULL: AgentChatRequest (incl. availableAgents P2 + conversationId), AgentChatResponse, HealthResponse, ErrorResponse
├── config.py                      # FULL: pydantic-settings + AGENT_REGISTRY fallback cache (4 agents) + AGENT_WORKSPACE_ROOT, CLI commands, timeout 300s
├── adapters/
│   ├── base_adapter.py            # FULL: strip_ansi(), build_prompt(), chat_stream() abstract, chunk contract
│   ├── adapter_factory.py         # FULL: ADAPTER_MAP {claude_code, codex, custom} → ValueError on unknown type
│   ├── claude_adapter.py          # FULL: asyncio subprocess claude -p, cwd=working_directory (session isolation)
│   └── codex_adapter.py           # FULL: asyncio subprocess codex exec, same pattern
├── prompts/
│   └── system_prompts.py          # FULL: 8 role prompts (claude_code/codex/orchestrator/custom + coder/designer/reviewer/architect fallback)
├── app/
│   ├── api/endpoints/
│   │   ├── messages.py            # FULL: POST /chat, auto-lookup systemPrompt, artifact detection on completion
│   │   └── agents.py              # FULL: get_agents()/get_agent()/agent_exists() utility for AGENT_REGISTRY lookups
│   └── utils/
│       └── artifact_uploader.py   # NEW: detect_code_blocks() regex → httpx POST /internal/artifacts per code block
├── agent_workspaces/              # Session-isolated Agent working directories (gitignored)
├── requirements.txt               # fastapi, uvicorn, httpx, pydantic, pydantic-settings, sse-starlette, langchain, langgraph
└── .env                           # ANTHROPIC_API_KEY, OPENAI_API_KEY (gitignored)

> **Agent metadata**: Java DB is source of truth, Python AGENT_REGISTRY is fallback cache. Java sends systemPrompt from DB + conversationId + workingDirectory. P1: availableAgents[] in request → Redis shared cache.
> **Artifact pipeline**: Agent stdout → Python artifact_uploader regex code block detection → POST /internal/artifacts → Java saveFromContent() + WebSocket preview_card → frontend ArtifactSandbox iframe.
> **Not yet implemented**: `http_adapter.py` (D13), `orchestrator.py` (P2).

docs/                              # 5 design docs (v1.0)
├── 项目概述与技术栈总览.md
├── 架构拓扑图与项目目录结构.md
├── 数据模型设计.md
├── API 契约定义与通信协议规范.md
└── 基础设施配置.md                 # Updated: H2 config + quick-start checklist + MVP annotations
```

## Current State Summary

### Frontend — ~95% (UI + routing + WebSocket + REST API + Markdown + agent selection all done)
- Vue Router 4: `/chat/:conversationId` (ChatView), `/office` (lazy), root redirect
- 3-col IM layout: SideBar + ChatList (hover delete, search, create) + ChatWindow (auto-scroll, MessageInput decoupled)
- Message types: text (Markdown rendered, code blocks with copy button) / code (Monaco Editor) / artifact_preview (click→full-screen overlay, refresh-safe)
- **Agent selection**: ChatWindow header dropdown to switch between Claude Code / Codex, sends agentId via STOMP
- **Markdown rendering**: messages parsed with `marked`, full styling for headings/code blocks/tables/blockquotes
- **Code blocks**: DeepSeek-style dark theme header bar with language label + copy button
- **Message actions**: hover action bar (copy button), extensible container for future buttons
- **Conversation delete**: hover X button on ChatList items, store handles API + local cleanup + auto-navigate
- **C7 complete**: ChatWindow connected to real STOMP/WebSocket, replaced setTimeout mock
- **REST API connected**: conversation/agent list, message history, artifact list (refresh-safe preview cards)
- WebSocket initialized in `ChatView.onMounted`, `sendMessage()` checks `ws.connected` — sends via WS or shows offline toast
- All API calls gracefully degrade to mock data on failure
- **Artifact preview pipeline complete**: Agent code → Python detection → /internal/artifacts → preview_card → ArtifactSandbox iframe
- **Pending**: agent settings panel (conversation-scoped agent configuration)

### Backend Java — ~70% (data + service + REST + WebSocket + artifact pipeline all done)
- Spring Boot compiles and starts on port 8080
- **Config layer done**: WebSocketConfig (STOMP + SockJS at `/ws-chat`), CorsConfig (Servlet Filter), ArtifactConfig (static resource mapping), SecurityConfig (placeholder, P1)
- **Data layer done**: 5 JPA entities + 5 Repository interfaces
- `data.sql` seeds Claude Code + Codex agents (H2 `MERGE INTO` syntax)
- **Service layer done**: ConversationService, MessageService, AgentGatewayService, ArtifactService (saveFromContent for text-based artifacts), WebSocketSessionManager
- **REST controllers done**: 5 controllers — Agent, Artifact (incl. POST /internal/artifacts + preview_card push), Conversation (7 endpoints), Message (+ WebSocketController)
- **Artifact pipeline complete**: Python → POST /internal/artifacts → ArtifactService.saveFromContent() → WebSocket push preview_card → frontend iframe preview
- **Agent workspace isolation**: Java passes `./agent_workspaces/{conversationId}` to Python, Agent CLI runs in session-isolated directory
- AgentGatewayService SSE parser: split("\n") + compatible with/without "data:" prefix
- H2 file-based DB, Java-exclusive (Python is stateless gateway, no DB access)
- **Agent routing**: WebSocketController reads request.agentId, routes to correct agent adapter
- **Error handling**: friendlyErrorMessage() maps technical errors to user-friendly Chinese messages
- **Pending**: end-to-end user auth (P1)

### Agent Service — ~85% (adapters + prompts + registry + artifact detection all done)
- FastAPI starts, single router `/api/agent` with `POST /chat`
- **ClaudeAdapter**: `asyncio.subprocess` → `claude -p "prompt"`, cwd=session workspace directory
- **CodexAdapter**: same pattern with `codex exec "prompt"` (fixed _build_prompt typo + error dedup)
- **System prompts**: 8 role templates, auto-lookup by agentType. All prompts now explicitly state text-only mode (no file writing)
- **AGENT_REGISTRY**: 4-agent fallback cache + agents.py utility module
- **Artifact auto-detection**: artifact_uploader.py regex-extracts code blocks after agent completes → httpx POST /internal/artifacts
- **Session workspace isolation**: `os.makedirs(./agent_workspaces/{conversationId})`, Agent CLI cwd=isolated directory
- Stream: SSE, non-stream: JSON
- `/health` endpoint, global error handlers (400/404/500)
- Friendly error messages: adapter errors mapped to user-friendly Chinese text in Java layer
- **No database access** — receives pre-assembled `context` from Java, returns token stream
- **Pending**: `http_adapter.py` (D13), `orchestrator.py` (P2)

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
