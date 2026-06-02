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
PUT /messages/{id}/pin
```
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
---
## 3. WebSocket 协议（前端 ↔ Spring Boot）
### 3.1 连接配置
| 配置项 | 值 |
|--------|----|
| 协议 | STOMP over WebSocket |
| 连接端点 | http://localhost:8080/ws |
| 降级方案 | SockJS（/ws 不可用时自动降级） |
| 心跳 | 客户端自动发送，默认 10 秒间隔 |
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
##### 消息块格式（MessageChunk）：
```json
{
  "content": "好的",
  "isComplete": false,
  "agentId": "agent_claude_001",
  "agentName": "Claude Code",
  "messageType": "text",
  "messageId": "msg_002"
}
```
##### 字段说明：
| 字段 | 类型 | 说明 |
|------|------|------|
| content | string | 消息内容片段（流式时为 token，完成时为完整内容） |
| isComplete | boolean | false=流式传输中，true=本条消息发送完毕 |
| agentId | string | 发送此消息的 Agent ID，前端据此区分不同 Agent 发言并切换头像 |
| agentName | string | 发送此消息的 Agent 名称 |
| messageType | string | 消息类型：text / code / diff / preview_card |
| messageId | string | 消息 ID（isComplete=true 时返回，用于后续操作） |
##### Agent 切换事件（agent_switch）
当 Orchestrator 切换调用的 Agent 时（如从 Coder 切到 Designer），后端推送切换通知：
```json
{
  "type": "agent_switch",
  "agentId": "agent_codex_001",
  "agentName": "Codex"
}
```
前端收到此事件后，后续渲染的消息气泡自动切换为对应 Agent 的头像和名称。
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

#### 请求体：
```json
{
  "agentType": "claude_code",
  "systemPrompt": "你是一个前端开发专家，擅长 React 函数组件和 Hooks。",
  "context": "帮我写一个 React 计数器组件",
  "stream": true,
  "workingDirectory": "/path/to/project"
}
```

#### 请求字段说明：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| agentType | string | 否 | `"claude_code"` | Agent 类型：`claude_code`（CLI）/ `codex`（CLI）/ `custom`（HTTP API） |
| systemPrompt | string | 否 | `""` | 系统提示词，覆盖 Agent 默认值 |
| context | string | 否 | `""` | 格式化后的聊天历史上下文，由 Java 后端组装 |
| stream | boolean | 否 | `false` | `true`=SSE 流式返回，`false`=收集完整后返回 JSON |
| workingDirectory | string | 否 | `null` | 本地 CLI Agent 执行任务的工作目录，仅 `claude_code`/`codex` 类型下有效 |

#### 流式响应（stream=true）

##### 响应格式：SSE（Server-Sent Events），每行 `data: <JSON>\n\n`

```text
data: {"token":"好的","finish":false,"agentId":"agent_claude_code","agentName":"Claude Code"}

data: {"token":"，这是","finish":false,"agentId":"agent_claude_code","agentName":"Claude Code"}

data: {"token":"生成的代码","finish":false,"agentId":"agent_claude_code","agentName":"Claude Code"}

data: {"token":"","finish":true,"messageId":"msg_456"}
```

##### SSE chunk 字段说明：

| 字段 | 类型 | 说明 |
|------|------|------|
| token | string | 本次推送的文本增量片段 |
| finish | boolean | `false`=流式传输中，`true`=本条消息发送完毕 |
| agentId | string | 发送此消息的 Agent ID（如 `agent_claude_code`） |
| agentName | string | Agent 显示名称（如 `Claude Code`） |
| messageId | string | 消息 ID（`finish=true` 时返回） |

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
### 5.3 WebSocket 错误处理
当处理消息出现异常时，后端通过同一订阅通道推送错误消息：
```json
{
  "content": "抱歉，Agent 服务暂时不可用，请稍后重试。",
  "isComplete": true,
  "agentName": "System",
  "messageType": "error",
  "messageId": "msg_error_001"
}
```
前端处理逻辑：
- messageType 为 error 时，气泡显示为红色/警告样式。
- 保留用户输入内容，允许重新发送。
- 网络断开时，STOMP 客户端自动重连（内置机制）。