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
                                       --HTTP--> External LLM APIs (Claude, Codex)
```

- **Frontend**: Vue 3.5 + TypeScript + Pinia + Tailwind CSS 4 + Vite 8
- **Backend**: Spring Boot 3.2.5 + Java 17 + H2 (dev, in-memory) / PostgreSQL (doc plan) + JPA
- **Agent Service**: FastAPI 0.109 + Python 3.11 + LangChain/LangGraph
- **Communication**: STOMP over WebSocket (frontend↔backend), REST API, SSE streaming (backend↔agent)

## Project Structure (Actual Code)

```
frontend/                          # Vue 3 Frontend — most complete module
├── src/
│   ├── main.ts                    # Entry: Pinia + Vue + Monaco worker config
│   ├── App.vue                    # Root: 3-col layout (SideBar/ChatList/ChatWindow + OfficeView + ArtifactWindow)
│   ├── style.css                  # @import "tailwindcss"
│   ├── env.d.ts                   # Vue SFC type declarations
│   ├── stores/chat.ts             # Pinia store: conversations, messages, officeMembers, artifact state, mock data
│   └── components/
│       ├── chat/
│       │   ├── ChatList.vue       # Left conversation list (hardcoded 3 mock agents)
│       │   ├── ChatWindow.vue     # Main chat area: header + message list + textarea + send. Simulates AI via setTimeout
│       │   ├── ChatMessage.vue    # Message bubble renderer (text/code/artifact_preview)
│       │   ├── CodeEditor.vue    # Monaco Editor wrapper (vs-dark, readOnly, copy button, ResizeObserver)
│       │   ├── ArtifactSandbox.vue # Iframe sandbox (srcdoc), renders HTML/CSS/JS previews
│       │   └── ArtifactWindow.vue  # Full-screen overlay: preview/code toggle, back button
│       ├── layout/SideBar.vue     # Left nav bar (dark indigo): chat/office/settings icons
│       └── office/
│           ├── OfficeView.vue     # SVG office scene: 8 seats, 3D desk, door, GSAP kick/walk animations
│           ├── OfficeChair.vue    # SVG chair component
│           └── StickFigure.vue    # SVG character: idle breathe, eye blink, walk, kick, shocked states
├── package.json                   # vue 3.5, pinia 3, gsap 3, monaco-editor, @stomp/stompjs, axios, tailwindcss 4
├── vite.config.ts                 # Vue + Tailwind plugins
└── index.html

backend-java/                      # Spring Boot — skeleton only
├── src/main/java/com/agenthub/
│   ├── AgenthubApplication.java  # @SpringBootApplication entry
│   ├── config/WebSocketConfig.java        # STOMP: /app prefix, /topic broker, /ws-chat endpoint + SockJS
│   ├── controller/WebSocketController.java # @MessageMapping("/chat.send") — empty handler
│   ├── dto/SendMessageRequest.java        # conversationId, content, agentId (Lombok @Data)
│   └── service/AgentGatewayService.java   # WebClient baseUrl=localhost:8000, sendToAgent() unimplemented
├── src/main/resources/application.yml     # H2 in-memory DB, JPA ddl-auto update, port 8080
└── pom.xml                                 # SB 3.2.5: web, websocket, jpa, webflux, postgresql, h2, lombok

agent-service/                     # FastAPI — mock stubs
├── main.py                        # FastAPI app, CORS, routers at /api/v1/{agents,conversations,messages,artifacts}
├── models.py                      # Pydantic: Agent, Conversation, Message, CodeBlock, DiffBlock, MessageContent
├── config.py                      # Settings (pydantic-settings): Claude/Codex API keys, timeout 120s, max_tokens 4096
├── adapters/
│   ├── base_adapter.py           # Abstract: async chat(message, history) — pass
│   ├── adapter_factory.py        # Returns ClaudeAdapter for "claude", else None
│   └── claude_adapter.py         # Stub, chat() passes
├── prompts/system_prompts.py     # 2 stub prompts: coder, designer
├── app/api/endpoints/
│   ├── __init__.py
│   ├── agents.py                 # GET / → mock hardcoded agent
│   ├── conversations.py          # GET / → returns []
│   ├── messages.py               # POST /chat/stream → mock SSE streaming (NDJSON, simulates 100ms per word)
│   └── artifacts.py             # GET / → returns []
├── requirements.txt              # fastapi, uvicorn, httpx, pydantic, sse-starlette, langchain, langgraph, etc.
└── .env                          # CLAUDE_API_KEY, CODEX_API_KEY (gitignored)

docs/                              # 5 comprehensive design documents (v1.0)
└── {项目概述, 架构拓扑图, API契约, 数据模型, 基础设施配置}.md
```

## Current State Summary

### Working (Frontend — UI prototype ~60%)
- Full IM-style 3-column layout (SideBar/ChatList/ChatWindow) renders
- Chat messages: text bubbles, code blocks (Monaco Editor), artifact preview cards
- Artifact system: click card → full-screen overlay → preview (iframe srcdoc) / code toggle
- Office view: SVG scene with 8 seats, animated stick figures, GSAP kick-out/walk-in
- View switching: Chat ↔ Office via left nav
- **All data is mock/hardcoded** — no real API calls, no WebSocket client connected

### Skeleton (Backend Java — ~15%)
- Spring Boot app compiles and starts
- WebSocket STOMP configured but handlers are empty stubs
- AgentGatewayService has WebClient but sendToAgent() is unimplemented
- **Missing**: all JPA entities, repositories, REST controllers, services, security/CORS config
- Currently uses H2 in-memory DB (dev convenience), docs specify PostgreSQL

### Stub (Agent Service — ~20%)
- FastAPI app starts, endpoints return mock data
- `/api/v1/messages/chat/stream` returns fake SSE stream
- Adapter pattern defined (base/factory/claude) but implementations are `pass`
- No real LLM API integration yet

### Key Technical Decisions
- **MVP simplification**: H2 instead of PostgreSQL, in-memory session management (no Redis), local filesystem storage (no MinIO)
- **No router configured** in frontend yet — single-page with view switching via Pinia state
- **No authentication** in MVP — docs reserve it for P1
- **Monaco Editor workers** configured as Vite web workers in main.ts
- **GSAP** used for office animations (timeline-based kick/walk sequences)
- **dev branch** is the active development branch; main has only initial commits
