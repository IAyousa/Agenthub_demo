# AgentHub 技术框架文档 — API 契约定义与通信协议规范

> **版本**: v1.0
> **最后更新**: 2026-05-25

---

## 1. 接口分类概览

本项目涉及三类接口：

| 接口类型 | 通信双方 | 协议 | 用途 |
|---------|---------|------|------|
| **REST API** | 前端 ↔ Spring Boot | HTTP/JSON | 会话管理、Agent 管理、历史消息查询 |
| **WebSocket** | 前端 ↔ Spring Boot | STOMP over WebSocket | 实时消息收发 |
| **内部 HTTP** | Spring Boot ↔ FastAPI | HTTP/JSON + SSE | Agent 调用 |

---

## 2. REST API（前端 ↔ Spring Boot）

### 2.1 基础约定

| 约定项 | 规范 |
|--------|------|
| Base URL | `http://localhost:8080` |
| 请求格式 | `Content-Type: application/json` |
| 响应格式 | `application/json` |
| 成功状态码 | `200 OK` / `201 Created` |
| 错误状态码 | 可能返回：`400 Bad Request` / `404 Not Found` / `500 Internal Server Error` |
| 字段命名 | `camelCase`（驼峰） |
| 认证方式 | MVP 阶段不做认证，P1 阶段加 JWT |

### 2.2 会话管理

#### 2.2.1 获取会话列表

```http
GET /conversations?archived=false
```

##### 查询参数：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| archived | boolean | 否 | 是否只显示归档会话，默认 false |
##### 成功响应（200）：
```json
{
  "conversations": [
    {
      "id": "conv_abc123",
      "title": "开发博客前端",
      "type": "direct",
      "lastMessage": "已生成 App.jsx 组件",
      "updatedAt": "2026-05-25T10:30:00",
      "agentNames": ["Claude Code"],
      "isArchived": false
    },
    {
      "id": "conv_def456",
      "title": "重构后端接口",
      "type": "group",
      "lastMessage": "Codex 已完成接口重构",
      "updatedAt": "2026-05-25T09:15:00",
      "agentNames": ["Claude Code", "Codex"],
      "isArchived": false
    }
  ]
}
```
#### 2.2.2 创建新会话
```http
POST /conversations
```
##### 请求体：
```json
{
  "title": "开发博客前端",
  "type": "direct",
  "agentIds": ["agent_claude_001"]
}
```
##### 字段说明：
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | string | 是 | 会话标题，最大 200 字符 |
| type | string | 是 | direct（单聊）或 group（群聊） |
| agentIds | string[] | 是 | 参与 Agent 的 ID 列表 |
##### 成功响应（201）：
```json
{
  "id": "conv_abc123",
  "title": "开发博客前端",
  "type": "direct",
  "agentIds": ["agent_claude_001"],
  "createdAt": "2026-05-25T10:30:00"
}
```
##### 错误响应（400）：
```json
{
  "error": "VALIDATION_ERROR",
  "message": "title 不能为空",
  "timestamp": "2026-05-25T10:30:00"
}
```
#### 2.2.3 获取会话详情
```http
GET /conversations/{id}
```
##### 成功响应（200）：
```json
{
  "id": "conv_abc123",
  "title": "开发博客前端",
  "type": "direct",
  "agents": [
    {
      "id": "agent_claude_001",
      "name": "Claude Code",
      "type": "claude_code",
      "avatarUrl": "/avatars/claude.png"
    }
  ],
  "createdAt": "2026-05-25T10:30:00",
  "updatedAt": "2026-05-25T10:30:00"
}
```
##### 字段说明：
| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 会话 ID |
| title | string | 会话标题 |
| type | string | direct（单聊）或 group（群聊） |
| agents | array | 该会话关联的 Agent 列表（含名称、头像、类型） |
| createdAt | string | 创建时间 |
| updatedAt | string | 最后更新时间 |
#### 2.2.4 更新会话
```http
PATCH /conversations/{id}
```
##### 请求体（所有字段可选）：
```json
{
  "title": "新标题",
  "isArchived": true
}
```
##### 成功响应（200）：
```json
{
  "id": "conv_abc123",
  "title": "新标题",
  "isArchived": true,
  "updatedAt": "2026-05-25T11:00:00"
}
```
#### 2.2.5 删除会话
```http
DELETE /conversations/{id}
```
##### 成功响应（200）：
```json
{
  "message": "会话已删除",
  "deletedId": "conv_abc123"
}
```
#### 2.2.6 修改会话关联 Agent
```http
PUT /conversations/{id}/agents
```
##### 请求体：
```json
{
  "agentIds": ["agent_claude_001", "agent_codex_001"]
}
```
##### 字段说明：
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| agentIds | string[] | 是 | 替换整个会话的 Agent 列表，传空数组则移除所有 Agent |
##### 成功响应（200）：
```json
{
  "id": "conv_abc123",
  "agentIds": ["agent_claude_001", "agent_codex_001"],
  "updatedAt": "2026-05-25T11:00:00"
}
```
#### 2.2.7 获取会话历史消息
```http
GET /conversations/{id}/messages?page=0&size=50
```
##### 查询参数：
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| page | int | 否 | 0 | 页码（从 0 开始） |
| size | int | 否 | 50 | 每页条数 |
##### 成功响应（200）：
```json
{
  "messages": [
    {
      "id": "msg_001",
      "senderType": "user",
      "content": "帮我写一个 React 组件",
      "messageType": "text",
      "createdAt": "2026-05-25T10:30:00"
    },
    {
      "id": "msg_002",
      "senderType": "agent",
      "agentName": "Claude Code",
      "content": {
        "type": "code",
        "language": "javascript",
        "code": "import React from 'react';\n\nconst App = () => {\n  return <div>Hello</div>;\n};",
        "filename": "App.jsx"
      },
      "messageType": "code",
      "createdAt": "2026-05-25T10:30:30"
    }
  ],
  "page": 0,
  "size": 50,
  "total": 2
}
```
#### 2.2.8 置顶/取消置顶消息
```http
PUT /conversations/{conversationId}/messages/{messageId}/pin
```
##### 路径参数：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| conversationId | string | 是 | 会话 ID（URL 路径体现层级关系，用于归属校验） |
| messageId | string | 是 | 消息 ID |
##### 请求体：
```json
{
  "pinned": true
}
```
##### 字段说明：
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| pinned | boolean | 是 | true=置顶，false=取消置顶 |
##### 成功响应（200）：
```json
{
  "id": "msg_001",
  "pinned": true
}
```
##### 安全说明：
后端需校验 `messageId` 对应的消息是否归属于 `conversationId` 对应的会话，防止跨会话越权操作。
### 2.3 Agent 管理
#### 2.3.1 获取可用 Agent 列表
```http
GET /agents
```
##### 成功响应（200）：
```json
{
  "agents": [
    {
      "id": "agent_claude_001",
      "name": "Claude Code",
      "type": "claude_code",
      "avatarUrl": "/avatars/claude.png",
      "capabilities": ["代码生成", "代码审查", "Debug"],
      "isBuiltin": true
    },
    {
      "id": "agent_codex_001",
      "name": "Codex",
      "type": "codex",
      "avatarUrl": "/avatars/codex.png",
      "capabilities": ["代码生成", "全栈开发", "技术问答"],
      "isBuiltin": true
    }
  ]
}
```
#### 2.3.2 创建自定义 Agent
```http
POST /agents
```
##### 请求体：
```json
{
  "name": "我的前端助手",
  "type": "custom",
  "systemPrompt": "你是一个 React 前端专家，只使用函数组件和 Hooks。",
  "capabilities": ["React 开发", "组件设计"]
}
```
##### 成功响应（201）：
```json
{
  "id": "agent_custom_001",
  "name": "我的前端助手",
  "type": "custom",
  "systemPrompt": "你是一个 React 前端专家，只使用函数组件和 Hooks。",
  "capabilities": ["React 开发", "组件设计"],
  "createdAt": "2026-05-25T11:00:00"
}
```
#### 2.3.3 获取 Agent 详情
```http
GET /agents/{id}
```
##### 成功响应（200）：
```json
{
  "id": "agent_claude_001",
  "name": "Claude Code",
  "type": "claude_code",
  "avatarUrl": "/avatars/claude.png",
  "systemPrompt": "你是一个经验丰富的软件工程师...",
  "capabilities": ["代码生成", "代码审查", "Debug", "重构建议"],
  "isBuiltin": true,
  "createdAt": "2026-05-20T08:00:00"
}
```
### 2.4 产物管理
#### 2.4.1 上传产物
```http
POST /artifacts/upload
```
##### 请求格式：
`Content-Type: multipart/form-data`
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | file | 是 | 产物文件 |
| conversationId | string | 是 | 所属会话 ID |
| messageId | string | 否 | 关联消息 ID |
##### 成功响应（201）：
```json
{
  "id": "art_001",
  "filename": "App.jsx",
  "fileSize": 2048,
  "conversationId": "conv_abc123",
  "messageId": "msg_002",
  "createdAt": "2026-05-25T11:00:00"
}
```
#### 2.4.2 下载/预览产物
```http
GET /artifacts/{id}
```
##### 成功响应（200）：
返回原始文件内容，`Content-Type` 根据文件类型自动设置。
#### 2.4.3 获取会话下所有产物
```http
GET /conversations/{id}/artifacts
```
##### 成功响应（200）：
```json
{
  "artifacts": [
    {
      "id": "art_001",
      "filename": "App.jsx",
      "fileSize": 2048,
      "messageId": "msg_002",
      "createdAt": "2026-05-25T11:00:00"
    },
    {
      "id": "art_002",
      "filename": "style.css",
      "fileSize": 1024,
      "messageId": "msg_003",
      "createdAt": "2026-05-25T11:01:00"
    }
  ]
}
```
#### 2.4.4 内部产物创建（Python Agent → Java 后端）
```http
POST /internal/artifacts
```
> 此接口用于 Python Agent 服务在 Agent 生成代码后，直接向 Java 后端上传产物文件，无需绕路前端。前端用户的 `POST /artifacts/upload` 接口保留(P2 用户手动上传场景)。
##### 请求体（JSON，非 multipart）：
```json
{
  "conversationId": "conv_abc123",
  "messageId": "msg_002",
  "filename": "App.jsx",
  "content": "import React from 'react';\n\nconst App = () => {\n  return <div>Hello</div>;\n};",
  "contentType": "text/javascript"
}
```
##### 字段说明：
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| conversationId | string | 是 | 所属会话 ID |
| messageId | string | 是 | 关联消息 ID |
| filename | string | 是 | 文件名 |
| content | string | 是 | 文件内容（纯文本，非 base64） |
| contentType | string | 否 | MIME 类型 |
##### 成功响应（201）：
```json
{
  "id": "art_003",
  "filename": "App.jsx",
  "fileSize": 128,
  "conversationId": "conv_abc123",
  "messageId": "msg_002",
  "createdAt": "2026-05-25T12:00:00"
}
```
##### 调用链路：
```text
Agent 生成代码 → Python Agent 服务接收 stdout
  → HTTP POST /internal/artifacts → Java 后端
  → Java 后端存储文件到 ./artifacts/ + 数据库记录
  → WebSocket 推送 preview_card 给前端（含预览 URL）
  → 前端 iframe 加载 URL 预览
```
---
 ## 3. WebSocket 协议（前端 ↔ Spring Boot）
### 3.1 连接配置（与实际代码完全对齐）
| 配置项 | 值 |
|--------|----|
| 协议 | STOMP over WebSocket |
| 连接端点 | **http://localhost:8080/ws-chat** |
| 降级方案 | SockJS（/ws-chat 不可用时自动降级，自动追加 `/info` 后缀检测可用性） |
| 心跳 | 客户端自动发送，默认 10 秒间隔 |
| STOMP 消息前缀 | `/app` |
| 订阅主题模式 | `/topic/conversation.{conversationId}` |
### 3.2 目的地映射
| 方向 | 目的地 | 说明 |
|------|--------|------|
| 前端 → 后端 | /app/chat.send | 发送聊天消息 |
| 后端 → 前端 | /topic/conversation.{conversationId} | 订阅指定会话的实时消息 |
| 后端 → 前端 | /queue/errors | 个人错误通知（P1） |
### 3.3 消息格式
#### 3.3.1 发送消息（前端 → 后端）
##### 目的地: `/app/chat.send`
```json
{
  "conversationId": "conv_abc123",
  "content": "帮我写一个 React 组件"
}
```
##### 字段说明：
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| conversationId | string | 是 | 目标会话 ID |
| content | string | 是 | 消息文本内容 |
> **注意**：前端不再传递 `agentType` 和 `systemPrompt`。Agent 调度由 Orchestrator 在 Python 层自动完成，前端不感知任务拆分过程。
#### 3.3.2 接收消息（后端 → 前端）
##### 订阅地址: `/topic/conversation.{conversationId}`
##### 消息块格式（MessageChunk，当前代码实际定义）：
```json
{
  "content": "好的",
  "isComplete": false,
  "agentId": "agent_claude_code",
  "agentName": "Claude Code",
  "messageType": "text",
  "messageId": null,
  "type": "chunk"
}
```
##### 字段说明：
| 字段 | 类型 | 说明 |
|------|------|------|
| content | string | 消息内容片段（流式时为 token，完成时为完整内容） |
| isComplete | boolean | false=流式传输中，true=本条消息发送完毕 |
| agentId | string | **每个 chunk 都携带**，发送此消息的 Agent ID，前端据此区分不同 Agent 发言并切换头像，确保 agent_switch 丢失也能正确渲染 |
| agentName | string | **每个 chunk 都携带**，发送此消息的 Agent 名称，冗余保障 |
| messageType | string | 消息类型：text / code / diff / preview_card / error |
| messageId | string | 消息 ID（isComplete=true 时返回，用于后续操作） |
| type | string | chunk / agent_switch / finish 事件类型标识 |

&gt; **P3 架构评审修正**：与架构评审问题清单 P3 对齐，每个 MessageChunk 都携带 agentId 和 agentName，冗余但极其健壮。即使 agent_switch 事件在网络抖动中先收到 chunk 后收到切换通知，前端依然能正确渲染头像。

##### Agent 切换事件（agent_switch，P1 阶段保留用于过渡动画）
当 Orchestrator 切换调用的 Agent 时（群聊多 Agent 模式），后端推送切换通知，可用于触发"正在切换 Agent"的过渡动画效果：
```json
{
  "type": "agent_switch",
  "agentId": "agent_codex_001",
  "agentName": "Codex"
}
```
前端收到此事件后，可播放平滑过渡动画，然后后续 chunk 继续携带 agentId/agentName 按规则渲染。
### 3.4 流式推送时序
```text
时间轴：前端视角的消息接收过程

t=0.0s  用户点击发送
t=0.1s  前端在消息列表添加用户气泡（本地）
t=0.5s  收到第 1 个 chunk → 显示流式气泡 + 光标动画
        {"content": "好的", "isComplete": false, "agentId": "agent_claude_001", "agentName": "Claude Code"}
t=0.6s  收到第 2 个 chunk → 内容追加
        {"content": "，这是", "isComplete": false, "agentId": "agent_claude_001", "agentName": "Claude Code"}
t=1.5s  Orchestrator 切换到另一个 Agent：
        {"type": "agent_switch", "agentId": "agent_codex_001", "agentName": "Codex"}
t=1.6s  收到 Codex 的第 1 个 chunk → 气泡头像切换为 Codex
        {"content": "这部分的代码", "isComplete": false, "agentId": "agent_codex_001", "agentName": "Codex"}
...
t=3.0s  收到最终 chunk → 流式气泡消失，消息固化到列表
        {"content": "完整回复内容...", "isComplete": true, "messageId": "msg_002"}
```
---
## 4. 内部 HTTP 接口（Spring Boot ↔ FastAPI）

### 4.1 基础约定

| 约定项 | 规范 |
|--------|------|
| Base URL | http://localhost:8000 |
| API 前缀 | `/api/agent/` |
| 请求格式 | Content-Type: application/json |
| 流式响应 | Content-Type: text/event-stream（SSE 格式，每行 `data: <JSON>\n\n`） |
| 非流式响应 | Content-Type: application/json |
| 超时时间 | 300 秒（可在 `config.py` 中修改 `AGENT_TIMEOUT`） |
| 字段命名 | camelCase（驼峰，与 Java 后端 AgentGatewayService 序列化格式一致） |

### 4.2 Agent 对话接口

```http
POST /api/agent/chat
```

#### 请求体（架构评审 P1 修正：结构化 messages 数组替代裸字符串 context）：
```json
{
  "agentType": "claude_code",
  "systemPrompt": "你是一个前端开发专家，擅长 React 函数组件和 Hooks。",
  "messages": [
    {"role": "user", "content": "帮我写一个 React 计数器组件"},
    {"role": "agent", "agentName": "Claude Code", "content": "好的，我来帮你生成..."}
  ],
  "stream": true,
  "workingDirectory": "/path/to/project"
}
```

&gt; **重要 P1 修正说明**：与架构评审问题清单 P1 对齐，将原裸字符串 `context` 字段替换为结构化 `messages` 数组，与 Claude API / OpenAI API 消息格式天然兼容，Python 端无需二次解析。彻底避免了两侧格式不一致导致 Agent"忘记上文"的集成故障。

#### 请求字段说明：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| agentType | string | 否 | `"claude_code"` | Agent 类型：`claude_code`（CLI）/ `codex`（CLI）/ `custom`（HTTP API），空值表示 Orchestrator 多 Agent 调度模式 |
| systemPrompt | string | 否 | `""` | 系统提示词，覆盖 Agent 数据库中的默认 system_prompt。为空时 Python 端自动从 SYSTEM_PROMPTS 模板按 agentType 查询 fallback |
| messages | array | 否 | `[]` | 结构化对话历史数组，每个元素包含 role/content/可选 agentName，替代原来的裸字符串 context |
| stream | boolean | 否 | `false` | `true`=SSE 流式返回，`false`=收集完整后返回 JSON |
| workingDirectory | string | 否 | `null` | 本地 CLI Agent 执行任务的工作目录，仅 `claude_code`/`codex` 类型下有效 |
| availableAgents | array | 否 | `[]` | **P2 预留**：Java 传入的可用 Agent 列表，Orchestrator 据此做调度决策。MVP 阶段为空，Python 使用 config.py 的 AGENT_REGISTRY 作为 fallback

##### 单 Agent 模式 vs 多 Agent 模式路由（新增设计文档对齐）
- `agentType` 有具体值 → **单 Agent 模式**，直接调用对应适配器，每个 chunk 携带统一的 agentId/agentName，不推送 agent_switch
- `agentType` 为 null 或 "orchestrator" → **多 Agent 群聊模式**，启动 Orchestrator 调度器，动态生成执行计划，推送 agent_switch 事件切换发言人

#### 流式响应（stream=true）

##### 响应格式：SSE（Server-Sent Events），每行 `data: <JSON>\n\n`

```text
-- 单 Agent 模式（无 agent_switch，直接流式输出）
data: {"token":"好的","finish":false,"agentId":"agent_claude_code","agentName":"Claude Code"}

data: {"token":"，这是","finish":false,"agentId":"agent_claude_code","agentName":"Claude Code"}

data: {"token":"生成的代码","finish":false,"agentId":"agent_claude_code","agentName":"Claude Code"}

data: {"token":"","finish":true,"messageId":"msg_456"}
```

```text
-- 多 Agent 群聊模式（Orchestrator 调度，含 agent_switch）
data: {"type":"agent_switch","agentId":"agent_claude_code","agentName":"Claude Code"}

data: {"token":"我来设计前端页面...","finish":false,"agentId":"agent_claude_code","agentName":"Claude Code"}

data: {"token":"代码完成","finish":false,"agentId":"agent_claude_code","agentName":"Claude Code"}

data: {"type":"agent_switch","agentId":"agent_codex_code","agentName":"Codex"}

data: {"token":"我来审查代码...","finish":false,"agentId":"agent_codex_code","agentName":"Codex"}

data: {"token":"","finish":true,"messageId":"msg_789"}
```

##### SSE chunk 字段说明：

| 字段 | 类型 | 说明 |
|------|------|------|
| token | string | 本次推送的文本增量片段 |
| finish | boolean | `false`=流式传输中，`true`=本条消息发送完毕 |
| agentId | string | **每个 chunk 都携带**，发送此消息的 Agent ID（如 `agent_claude_code`），冗余保障 |
| agentName | string | **每个 chunk 都携带**，Agent 显示名称（如 `Claude Code`），冗余保障 |
| messageId | string | 消息 ID（`finish=true` 时返回） |
| type | string | 可选，标识 agent_switch 控制事件类型 |

#### 非流式响应（stream=false）

```json
{
  "content": "好的，这是生成的 React 计数器组件代码：\n```javascript\nimport React, { useState } from 'react';\n\nconst Counter = () => {\n  const [count, setCount] = useState(0);\n  return <div>{count}</div>;\n};\n\nexport default Counter;\n```",
  "messageId": "msg_456"
}
```
### 4.3 健康检查
```http
GET /health
```
#### 成功响应（200）：
```json
{
  "status": "ok",
  "version": "1.0.0",
  "uptime": 3600
}
```
---
## 5. 错误处理规范
### 5.1 REST API 错误格式
所有错误统一返回以下 JSON 结构：
```json
{
  "error": "ERROR_CODE",
  "message": "人类可读的错误描述",
  "timestamp": "2026-05-25T10:30:00",
  "path": "/api/conversations"
}
```
### 5.2 常见错误码
| HTTP 状态码 | error 值 | 说明 |
|-------------|----------|------|
| 400 | VALIDATION_ERROR | 请求参数校验失败 |
| 404 | NOT_FOUND | 资源不存在（会话/Agent/用户） |
| 500 | INTERNAL_ERROR | 服务器内部错误 |
| 502 | AGENT_ERROR | Agent 服务调用失败 |
| 504 | AGENT_TIMEOUT | Agent 服务超时 |

### 5.3 WebSocket 错误码枚举
流式推送错误时使用以下标准化错误码，前端据此决定 UI 行为：

| 错误码 | 说明 | 前端行为 |
|--------|------|----------|
| `AGENT_TIMEOUT` | Agent 调用超时 | 显示"重新发送"按钮 |
| `AGENT_UNAVAILABLE` | Agent 服务不可达（连接拒绝） | 显示"稍后重试"提示 |
| `CLI_NOT_FOUND` | 本地 CLI 工具未安装 | 显示配置引导 |
| `CONTEXT_TOO_LONG` | 上下文超出 token 限制 | 提示固定关键消息或开新会话 |
| `UNKNOWN_ERROR` | 未分类错误 | 显示通用错误提示 |

### 5.4 各层级异常捕获职责
| 层级 | 捕获范围 | 转换后的 errorCode |
|------|----------|-------------------|
| Python Agent 服务 | 本地 CLI 调用失败（subprocess.CalledProcessError） | `CLI_NOT_FOUND` |
| Python Agent 服务 | 自定义 Agent HTTP 调用超时（httpx.TimeoutException） | `AGENT_TIMEOUT` |
| Java AgentGatewayService | Python Agent 服务连接失败（ConnectException） | `AGENT_UNAVAILABLE` |
| Java AgentGatewayService | WebClient 超时 | `AGENT_TIMEOUT` |
| Java WebSocketController | 其他未捕获异常 | `UNKNOWN_ERROR` |

### 5.5 WebSocket 错误推送格式
当处理消息出现异常时，后端通过同一订阅通道推送错误消息：
```json
{
  "content": "抱歉，Agent 服务暂时不可用，请稍后重试。",
  "isComplete": true,
  "agentName": "System",
  "messageType": "error",
  "errorCode": "AGENT_TIMEOUT",
  "messageId": "msg_error_001",
  "retryable": true
}
```
前端处理逻辑：
- messageType 为 error 时，气泡显示为红色/警告样式，根据 errorCode 决定是否显示重试按钮。
- 保留用户输入内容，允许重新发送。
- 网络断开时，STOMP 客户端自动重连（内置机制）。