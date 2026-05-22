# Multi-Agent Collaboration Platform API Specification (v1.0)

本文档定义了多 Agent 协作平台的前后端交互协议，包含 REST API、WebSocket 实时通信以及数据模型定义。

## 一、 通用约定
- **Base URL**: `/api/v1`
- **Content-Type**: `application/json`
- **认证方式**: HTTP Header `Authorization: Bearer <JWT_TOKEN>`

---

## 二、 数据模型 (Data Models)

### 1. Agent (智能体)
```json
{
  "id": "string",
  "name": "string",
  "avatar": "string",
  "description": "string",
  "system_prompt": "string",
  "tools": ["string"], // 工具列表，如 ["web_search", "calculator"]
  "capabilities": ["string"], // 能力标签，如 ["code", "image", "data_analysis"]
  "created_at": "timestamp"
}
```

### 2. Conversation (会话)
```json
{
  "id": "string",
  "title": "string",
  "type": "direct" | "group",
  "participants": ["agent_id", "user_id"],
  "last_message_at": "timestamp",
  "created_at": "timestamp"
}
```

### 3. Message (消息)
```json
{
  "id": "string",
  "conversation_id": "string",
  "sender_id": "string", // 用户 ID 或 Agent ID
  "sender_type": "user" | "agent",
  "content": {
    "type": "text" | "code" | "diff" | "artifact_preview",
    "text": "string", // 当 type 为 text 时使用
    "code_block": { // 当 type 为 code 时使用
      "language": "string",
      "code": "string",
      "filename": "string"
    },
    "diff": { // 当 type 为 diff 时使用
      "original": "string",
      "modified": "string"
    },
    "artifact_id": "string" // 当 type 为 artifact_preview 时关联产物
  },
  "is_pinned": "boolean",
  "created_at": "timestamp"
}
```

---

## 三、 REST API 接口

### 1. 智能体管理 (Agent Management)
- **GET `/agents`**: 获取可用 Agent 列表
- **GET `/agents/{id}`**: 获取 Agent 详情
- **POST `/agents`**: 创建自定义 Agent (参数同模型定义)

### 2. 会话管理 (Conversation Management)
- **GET `/conversations`**: 获取当前用户的会话列表
- **POST `/conversations`**: 创建新会话
  - Body: `{ "title": "string", "type": "direct" | "group", "participant_ids": [] }`
- **DELETE `/conversations/{id}`**: 删除会话

### 3. 消息管理 (Message Management)
- **GET `/conversations/{id}/messages`**: 分页获取会话历史消息
  - Query: `limit=20&offset=0`
- **POST `/conversations/{id}/pin/{message_id}`**: 置顶消息

### 4. 产物管理 (Artifact Management)
- **GET `/artifacts/{id}`**: 获取产物内容 (HTML/JS/Code)
- **POST `/artifacts/deploy`**: 一键部署产物 (P2 功能)

---

## 四、 实时通信协议 (Real-time Protocol)

由于 Agent 生成内容具有流式特征，采用 **WebSocket** 进行双向通信。

### 1. WebSocket 连接
- **URL**: `ws://domain/ws/chat/{conversation_id}`

### 2. 客户端发送 (Client -> Server)
```json
{
  "type": "chat_message",
  "content": "帮我写一个 React 计数器组件",
  "mention_ids": ["agent_id_1"] // 可选，指定唤起某个 Agent
}
```

### 3. 服务端推送 (Server -> Client)

#### A. 消息开始生成 (Message Start)
```json
{
  "type": "msg_start",
  "message_id": "uuid",
  "sender_id": "agent_id",
  "role": "orchestrator" | "worker"
}
```

#### B. 消息内容增量 (Message Chunk - Stream)
```json
{
  "type": "msg_chunk",
  "message_id": "uuid",
  "delta": "string" // 增量的文本或代码片段
}
```

#### C. 消息结束 (Message End)
```json
{
  "type": "msg_end",
  "message_id": "uuid",
  "full_content": { ... } // 最终结构化内容
}
```

#### D. 状态同步 (Status Sync)
```json
{
  "type": "agent_status",
  "agent_id": "uuid",
  "status": "thinking" | "executing" | "idle",
  "current_step": "正在调用搜索工具..."
}
```

---

## 五、 错误处理
所有接口错误均返回标准 JSON：
```json
{
  "error_code": "string",
  "message": "错误描述详情",
  "details": {}
}
```
