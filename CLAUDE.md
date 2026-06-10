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
- **Agent Service**: FastAPI 0.109 + Python 3.11, stateless gateway, invokes local CLI tools via asyncio subprocess, no database access. Tracks session state via in-memory `_session_tracker` (per conversationId+agentType).
- **Agent Execution**: Local CLI — `claude -p "prompt"` / `claude --continue -p "prompt"` (native session memory) / `codex exec "prompt"` / `codex exec resume --last "prompt"`, stdout streaming. Claude Code uses `--continue` to restore session context; Codex uses `exec resume --last` + workspace isolation for session persistence.
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
│   ├── stores/settings.ts          # Pinia store: global theme (4 presets), CSS variable injection, scrollbar JS fix, localStorage persistence
│   ├── stores/auth.ts              # Pinia store: JWT token management, auth state, login/register/logout
│   ├── websocket/
│   │   └── wsClient.ts            # STOMP client singleton: connect/subscribe/sendMessage via native WebSocket, auto-reconnect, heartbeat
│   ├── views/
│   │   ├── ChatView.vue           # Route container: watch route.params → selectConversation() {immediate}, onMounted → initWebSocket()
│   │   └── OfficeView.vue         # Thin wrapper around office/OfficeView.vue component
│   └── components/
│       ├── chat/
│       │   ├── ChatList.vue       # Conversation list: search, create btn (→CreateConversationModal), route push on select, agent tags, relative time
│       │   ├── ChatWindow.vue     # Main chat area: header + message list + MessageInput. Real WebSocket/STOMP send, offline toast. Agent dropdown REMOVED
│       │   ├── ChatMessage.vue    # Message bubble (text/code/artifact_preview), avatar, click→artifact overlay, streaming plain-text mode
│       │   ├── MessageInput.vue   # Shared input: toolbar + textarea + send btn, emits 'send'. Keyed by conversationId for auto-clear
│       │   ├── CreateConversationModal.vue # Teleport modal: title + type(direct/group) + agent selection (dropdown/checkboxes)
│       │   ├── CodeEditor.vue     # Monaco Editor: vs-dark, copy btn, ResizeObserver, reactive code/lang props
│       │   ├── ArtifactSandbox.vue # Iframe sandbox (srcdoc), HTML/CSS/JS/TS preview with error handling
│       │   ├── ArtifactWindow.vue  # Full-screen overlay: preview/code toggle, back button
│       │   └── ProjectBundleCard.vue # Foldable file-tree card: iframe preview with base injection, code highlighting, ZIP download
│       ├── layout/
│       │   ├── SideBar.vue         # Left nav (theme gradient): chat/office/settings icons + logout, useRoute/useRouter for active state
│       │   └── ThemeSettingsModal.vue # Teleport modal: 4 theme presets (modern/ocean/forest/sunset) with color swatches
│       └── office/
│           ├── OfficeView.vue     # SVG office: 8 seats, 3D desks, door, plant decor, GSAP kick/walk, invite panel, multi-office management
│           ├── CreateOfficeModal.vue # Modal for creating new office rooms (name/description/maxMembers/theme)
│           ├── OfficeChair.vue    # SVG chair with backrest and legs
│           └── StickFigure.vue    # Detailed SVG character: idle breathe, eye blink, walk/kick/shocked, hair/clothing/face per role
├── package.json                   # vue 3.5, pinia 3, vue-router 4.6, gsap 3, monaco-editor 0.55, @stomp/stompjs 7, sockjs-client, axios, tailwind 4, TS 6, Vite 8
├── vite.config.ts                 # Vue + @tailwindcss/vite plugins only (no proxy, no @ alias)
└── index.html

backend-java/                      # Spring Boot — ~75% complete (data + service + REST + WebSocket + artifact + JWT auth all done)
├── src/main/java/com/agenthub/
│   ├── AgenthubApplication.java  # @SpringBootApplication entry
│   ├── config/
│   │   ├── WebSocketConfig.java   # STOMP: /app prefix, /topic broker, /ws-chat + SockJS, CORS origins from yml
│   │   ├── CorsConfig.java        # CorsFilter Bean (Servlet Filter layer, reads cors.allowed-origins)
│   │   ├── ArtifactConfig.java    # Static resource mapping: /artifacts/** → file:./artifacts/
│   │   └── SecurityConfig.java    # Spring Security + JWT: stateless session, /auth/** + /ws-chat/** + /h2-console/** permitAll, custom 401/403 JSON response
│   ├── controller/
│   │   ├── WebSocketController.java # @MessageMapping("/chat.send") — handler filled: save→route→SSE→STOMP push, group→Orchestrator routing
│   │   ├── AgentController.java   # CRUD: GET/POST /agents, GET /agents/{id}
│   │   ├── ArtifactController.java # CRUD + POST /internal/artifacts (Python→Java upload), WebSocket push preview_card
│   │   ├── AuthController.java    # POST /auth/register + /auth/login, BCrypt password, JWT token response
│   │   ├── ConversationController.java # CRUD: 7 REST endpoints for conversation + agent management
│   │   └── MessageController.java  # Paginated message history + pin/unpin
│   ├── security/
│   │   ├── JwtAuthenticationFilter.java # OncePerRequestFilter: Bearer token extraction + validation
│   │   └── JwtTokenProvider.java   # jjwt 0.12.5: HS256 generate/validate, key from ${JWT_SECRET} env var
│   ├── dto/                        # SendMessageRequest, MessageChunk, ArtifactDTO, etc. (6 DTOs)
│   ├── model/                     # User, Conversation, Message, Agent, Artifact JPA entities
│   ├── repository/                # 5 JPA data access interfaces
│   └── service/
│       ├── AgentGatewayService.java # WebClient SSE parser, AgentToken callback, null agentType passthrough
│       ├── ArtifactService.java   # Upload/query/download/delete, saveFromContent for text-based artifacts
│       ├── ConversationService.java # CRUD, agent add/remove, archive, user-scoped queries
│       ├── MessageService.java    # Send, paginated history, pin/unpin
│       └── WebSocketSessionManager.java # STOMP session management via SimpMessagingTemplate
├── src/main/resources/
│   ├── application.yml            # H2 default + spring.config.import optional:application-secret.yml + JWT ${JWT_SECRET:default}
│   ├── application-pg.yml         # PostgreSQL Profile (optional, -Dspring.profiles.active=pg)
│   ├── application-secret.yml.example # 本地敏感配置模板（复制为 application-secret.yml 使用）
│   ├── data.sql                   # H2 seed data: Claude Code + Codex agents (MERGE INTO)
│   └── data-pg.sql                # PostgreSQL seed data (INSERT ON CONFLICT)
└── pom.xml                        # SB 3.2.5: web, websocket, jpa, webflux, postgresql, h2, lombok, security, jjwt 0.12.5

agent-service/                     # FastAPI — ~92% complete, stateless gateway, no DB access
├── main.py                        # FULL: FastAPI app, CORS, /api/agent router, global error handlers, /health. Windows: default ProactorEventLoop
├── models.py                      # FULL: AgentChatRequest (agentType Optional[str] for Orchestrator), AgentChatResponse, HealthResponse, ErrorResponse
├── config.py                      # FULL: pydantic-settings + AGENT_REGISTRY + CLAUDE_STREAM_ARGS + CODEX_SKIP_GIT_CHECK + AGENT_WORKSPACE_ROOT, CLI commands, timeout 300s
├── orchestrator.py                # FULL: LLM驱动的多Agent编排器 — Claude分析意图→JSON计划→串行调度→三层降级
├── adapters/
│   ├── base_adapter.py            # FULL: strip_ansi(), build_prompt(), chat_stream() abstract, session_created event contract
│   ├── adapter_factory.py         # FULL: ADAPTER_MAP {claude_code, codex, custom} → ValueError on unknown type
│   ├── claude_adapter.py          # FULL: claude -p --output-format stream-json --include-partial-messages --verbose (逐token实时流式), --continue会话延续, cwd=workspace, text_delta解析+thinking_delta过滤+message_stop→msg_end
│   └── codex_adapter.py           # FULL: codex exec (1st, session_created) / codex exec resume --last (subsequent), session ID extraction, stderr diagnostics
├── prompts/
│   └── system_prompts.py          # FULL: 8 role prompts, positive guidance (直接输出代码), no "permission" wording
├── app/
│   ├── api/endpoints/
│   │   ├── messages.py            # FULL: POST /chat, _session_tracker (is_first + cli_session_id), Orchestrator routing, session_created handling
│   │   └── agents.py              # FULL: get_agents()/get_agent()/agent_exists() utility
│   └── utils/
│       ├── artifact_uploader.py   # FULL: detect_code_blocks() + _infer_filename() 真实文件名推断 + write_blocks_to_workspace() 代码块落盘 + detect_and_upload() 批量上传
│       └── workspace_scanner.py   # FULL: snapshot_workspace() SHA256快照 + diff_snapshots() 增量检测 + scan_and_upload() 磁盘文件批量上传
├── .env.example                   # 环境变量模板（ANTHROPIC_API_KEY, OPENAI_API_KEY）
├── .gitignore                     # 保护 .env 不被提交
├── agent_workspaces/              # Session-isolated Agent working directories (gitignored)
└── requirements.txt               # fastapi, uvicorn, httpx, pydantic, pydantic-settings

> **Agent metadata**: Java DB is source of truth, Python AGENT_REGISTRY is fallback cache. Java sends systemPrompt from DB + conversationId + workingDirectory. P1: availableAgents[] in request → Redis shared cache.
> **Artifact pipeline (v2.0 — unified project_bundle)**: Agent stdout → Python detect_code_blocks() + filename inference → write_blocks_to_workspace() 落盘 → workspace_scanner 磁盘扫描 → POST /internal/artifacts/batch 批量上传 → Java saveFromContent() + WebSocket push project_bundle (1.5s延迟) → frontend ProjectBundleCard 可折叠文件树 + iframe base注入预览。刷新后 loadMessages 按 messageId 聚合 artifact 为 project_bundle 保持卡片一致。
> **Not yet implemented**: `http_adapter.py` (D13).

docs/                              # 设计文档 + 规范
├── 项目概述与技术栈总览.md
├── 架构拓扑图与项目目录结构.md
├── 数据模型设计.md
├── API 契约定义与通信协议规范.md
├── 基础设施配置.md                 # Updated: H2/PG dual DB + JWT + quick-start checklist + config templates
├── CLI原生记忆设计方案.md          # v3.1: Claude Code --continue + Codex exec resume integrated
├── 团队代码合并规范.md             # Commit规范 + PR模板 + Code Review流程
└── 开发记录模板.md
docker-compose.yml                  # PostgreSQL 15-alpine 本地开发容器
```

## Current State Summary

### Frontend — ~95% (UI + routing + WebSocket + REST API + Markdown + agent selection + theme system + auth + project_bundle all done)
- Vue Router 4: `/chat/:conversationId` (ChatView), `/office` (lazy), root redirect
- 3-col IM layout: SideBar + ChatList (hover delete, search, create) + ChatWindow (auto-scroll, MessageInput decoupled)
- Message types: text (Markdown rendered, code blocks with copy button) / code (Monaco Editor) / artifact_preview (click→full-screen overlay) / project_bundle (collapsible file-tree card with iframe preview + ZIP download)
- **Agent selection**: Moved to CreateConversationModal (type toggle direct/group + agent dropdown/checkboxes), selected agent stored in Pinia, sent via STOMP
- **Markdown rendering**: messages parsed with `marked`, full styling for headings/code blocks/tables/blockquotes
- **Code blocks**: DeepSeek-style dark theme header bar with language label + copy button
- **Message actions**: hover action bar (copy button), extensible container for future buttons
- **Conversation delete**: hover X button on ChatList items, store handles API + local cleanup + auto-navigate
- **C7 complete**: ChatWindow connected to real STOMP/WebSocket, replaced setTimeout mock
- **Theme system**: 4 presets (modern/ocean/forest/sunset) via Tailwind @theme + CSS variables, scrollbar JS workaround, localStorage persistence
- **Auth**: LoginView (login/register), JWT token in localStorage, axios interceptor auto-attach, logout clears state + WebSocket
- **REST API connected**: conversation/agent list, message history, artifact list (refresh-safe preview cards)
- WebSocket initialized in `ChatView.onMounted`, `sendMessage()` checks `ws.connected` — sends via WS or shows offline toast
- All API calls gracefully degrade to mock data on failure
- **Unified project_bundle card**: ProjectBundleCard 可折叠文件树 + iframe srcdoc with base injection (兼容无head的HTML5) + 按文件名查找资源端点 + 下载全部ZIP按钮
- **Refresh-safe artifact aggregation**: loadMessages 按 messageId 聚合同批 artifact → project_bundle，刷新前后卡片类型一致
- **Streaming output**: Claude CLI `--output-format=stream-json` + `--include-partial-messages` 实时逐token输出，Python异步解析text_delta→SSE→STOMP→前端tokenQueue 30ms逐帧渲染，原生WebSocket避免SockJS帧缓冲延迟
- **Pending**: agent settings panel (conversation-scoped agent configuration)

### Backend Java — ~80% (data + service + REST + WebSocket + artifact + JWT auth + PG Profile + batch upload + project download all done)
- Spring Boot compiles and starts on port 8080
- **Config layer done**: WebSocketConfig (原生WS :8080 + SockJS :8080/ws-chat-sockjs 双模式), CorsConfig, ArtifactConfig, SecurityConfig (JWT stateless + custom 401/403 JSON + /artifacts/** + /conversations/*/download permitAll)
- **Security layer done**: AuthController (/auth/register + /auth/login), JwtAuthenticationFilter, JwtTokenProvider (jjwt 0.12.5, ${JWT_SECRET})
- **Data layer done**: 5 JPA entities + 5 Repository interfaces (ArtifactRepository 新增 findByConversationIdAndFilename)
- `data.sql` (H2 `MERGE INTO`), `data-pg.sql` (PostgreSQL `INSERT ON CONFLICT`)
- **Service layer done**: ConversationService, MessageService, AgentGatewayService (null→Orchestrator), ArtifactService (saveFromContent + findByConversationIdAndFilename), WebSocketSessionManager
- **REST controllers done**: 6 controllers — Agent, Artifact, Auth, Conversation, Message, WebSocket
- **Artifact batch upload**: POST /internal/artifacts/batch — Python 批量上传 → 单条 project_bundle WS 推送（1.5s 延迟确保文本先到）
- **Artifact by filename**: GET /artifacts/conversation/{id}/{filename} — iframe 中相对路径 CSS/JS 资源解析
- **Project ZIP download**: GET /conversations/{id}/download — 打包工作目录全部文件
- **Fallback delay**: finish 先于 token 到达时延迟 2s 确认，避免 Agent 慢启动误触发 "CLI 未连接"
- **Dual database**: H2 default (zero-dependency), PostgreSQL via `-Dspring.profiles.active=pg`
- **Config separation**: `${VAR:default}` pattern, `application-secret.yml.example`, `application-pg.yml` profile
- **Agent routing**: group→agentType=null→Orchestrator, direct→agentId from DB
- **Pending**: `http_adapter.py` (D13)
### Agent Service — ~94% (adapters + prompts + registry + session tracking + orchestrator + workspace_scanner + artifact detection all done)
- FastAPI starts, single router `/api/agent` with `POST /chat`
- **ClaudeAdapter**: 1st message: `claude -p --output-format stream-json ...`; subsequent: `claude --continue -p`. `is_first_message` via kwargs. cwd=session workspace. has_content 守卫防止空 msg_end 误触发 Java fallback
- **CodexAdapter**: 1st message: `codex exec` → `session_created` event; subsequent: `codex exec resume --last`. Session ID extraction via regex. `CODEX_SKIP_GIT_CHECK` configurable
- **Orchestrator**: LLM-driven multi-agent dispatcher — Claude Code analyzes intent → JSON execution plan → sequential sub-agent dispatch → streaming aggregate. Three-tier fallback: plan failure→single agent, sub-agent error→Claude retry, Claude error→friendly message
- **Session tracking**: `messages.py` maintains `_session_tracker: dict` keyed by `{conversationId}:{agentType}`, stores `is_first` + `cli_session_id` (Codex session UUID). In-memory (restart-safe: gracefully degrades, re-injects system_prompt once)
- **System prompts**: 8 role templates, auto-lookup by agentType. Positive guidance (直接输出完整代码), no "permission" wording. 注入工作区隔离指令（禁止Agent访问工作目录外文件）
- **AGENT_REGISTRY**: 4-agent fallback cache + agents.py utility module
- **Workspace scanner**: workspace_scanner.py — snapshot_workspace() SHA256 全量快照 + diff_snapshots() 增量检测 + scan_and_upload() 磁盘文件批量上传到 Java /internal/artifacts/batch。全局 `_workspace_snapshots` 按 conversationId 维护状态
- **Unified artifact pipeline**: `_upload_merged_artifacts()` 串行流程：detect_code_blocks() → 文件名推断 → write_blocks_to_workspace() 代码块落盘 → workspace_scanner.scan_and_upload() 磁盘扫描（权威来源）→ scanner 未找到? → detect_and_upload() 代码块回退上传
- **Artifact auto-detection**: artifact_uploader.py regex-extracts code blocks, `_infer_filename()` 从 Agent 文本上下文推断真实文件名（如 "创建 index.html"），`write_blocks_to_workspace()` 将 stdout 代码块写入工作目录供 scanner 后续发现
- **Session workspace isolation**: `os.makedirs(./agent_workspaces/{conversationId})`, Agent CLI cwd=isolated directory. 工作空间根路径通过 `${AGENT_WORKSPACE_ROOT}` 可配置
- Stream: SSE, non-stream: JSON
- `/health` endpoint, global error handlers (400/404/500)
- **Windows**: default `ProactorEventLoop` (supports `create_subprocess_exec`)
- Friendly error messages: adapter errors mapped to user-friendly Chinese text in Java layer
- **No database access** — receives pre-assembled `context` from Java, returns token stream
- **Pending**: `http_adapter.py` (D13)

### Doc-vs-Code Gaps
- **Python is stateless gateway** — docs originally planned Python sharing H2 via JPype/jaydebeapi. Now pure CLI subprocess forwarding, zero DB access. Planned agents/conversations/artifacts CRUD endpoints were removed.
- **Local CLI instead of cloud API** — docs `config.py` planned `CLAUDE_API_KEY`/`CODEX_API_KEY` for direct Anthropic/OpenAI HTTP calls. Now uses asyncio subprocess with local CLI; API keys read by CLI tools from system env, Agent Service never touches them.
- **CLI native session memory** — Java no longer assembles conversation history via `buildContextString()`. Claude Code uses `--continue` for context restoration; Python `_session_tracker` manages is_first_message state.
- **Docs planned but unimplemented**: `http_adapter.py` (D13)
- **H2 + PostgreSQL dual mode** — H2 default for zero-dependency dev, PG via `-Dspring.profiles.active=pg` with `docker-compose.yml`
- **JWT auth implemented** — Spring Security + jjwt 0.12.5, `/auth/register` + `/auth/login`, stateless Bearer token
- **Frontend is TypeScript, not JavaScript** — docs say `JavaScript ES2022+`, actual code is all `.ts` / `<script setup lang="ts">`
- **WebSocket endpoint is `/ws-chat`** — docs API contract says `/ws`, actual code uses `/ws-chat`
- **SendMessageRequest DTO** — actual code has `agentId` field, but API contract says frontend should NOT send `agentType`/`agentId` (Orchestrator handles scheduling). Needs alignment during implementation.
- **No Redis/MinIO** in current phase — reserved for P2
- **Config templates**: `.env.example` + `application-secret.yml.example` — copy & fill to use
- **Vue Router 4** drives view switching (URL shareable)
- **Monaco Editor** (Vite web worker loading) + **GSAP** animations
- **dev branch** is the active development branch
