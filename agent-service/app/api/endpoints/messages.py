"""
AgentHub Agent Service — Spring Boot → FastAPI 内部 Agent 调用端点

本模块是 Agent 服务的核心 API 端点，负责接收 Java 后端 AgentGatewayService
转发的用户消息，调用对应的 Agent 适配器，并以 SSE（Server-Sent Events）
格式流式返回生成内容。严格对齐 API 契约文档第 4 节。

调用链路：
    用户 → Vue 前端 → WebSocket → Spring Boot WebSocketController
    → AgentGatewayService → HTTP POST /api/agent/chat
    → 本模块 chat() → AdapterFactory → Claude/Codex 适配器
    → Agent → 流式解析 → SSE 返回 → Spring Boot 转发 WebSocket → 前端

请求格式（JSON）：
    {
        "agentType": "claude_code",
        "systemPrompt": "你是一个前端开发专家，擅长 React。",
        "context": "用户：帮我写一个 React 组件\\n",
        "stream": true
    }

流式响应（SSE）：
    data: {"token": "好的", "finish": false, "agentId": "...", "agentName": "..."}
    ...
    data: {"token": "", "finish": true, "messageId": "msg_456"}

非流式响应（JSON）：
    {"content": "...", "messageId": "msg_456"}
"""

import json
from datetime import datetime, timezone

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, StreamingResponse

from adapters.adapter_factory import AdapterFactory
from models import AgentChatRequest, AgentChatResponse, ErrorResponse

router = APIRouter()

AGENT_DISPLAY_NAMES = {
    "claude_code": "Claude Code",
    "codex": "Codex",
    "custom": "Custom Agent",
}

# 会话跟踪字典：记录每个 (conversationId, agentType) 的状态
# 格式: {
#     "conv_id:agent_type": {
#         "is_first": False,
#         "cli_session_id": "a1b2c3d4-..."  # Codex session UUID（Claude 不需要）
#     }
# }
# 进程内存状态，服务重启后丢失。
# 安全降级：重启后首次调用会重新注入 system_prompt（不影响正确性）。
_session_tracker: dict = {}

_SSE_EXAMPLE = (
    'data: {"token":"好的","finish":false,"agentId":"agent_claude_code","agentName":"Claude Code"}\n\n'
    'data: {"token":"，这是","finish":false,"agentId":"agent_claude_code","agentName":"Claude Code"}\n\n'
    'data: {"token":"生成的代码","finish":false,"agentId":"agent_claude_code","agentName":"Claude Code"}\n\n'
    'data: {"token":"","finish":true,"messageId":"msg_456"}'
)


def _error_json(status_code: int, error_code: str, message: str, path: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(
            error=error_code,
            message=message,
            timestamp=datetime.now(timezone.utc).isoformat(),
            path=path,
        ).model_dump(),
    )


@router.post(
    "/chat",
    summary="Agent 对话",
    description="""
接收 Java 后端转发的 Agent 调用请求，根据 `stream` 参数返回流式或非流式响应。

**流式模式**（`stream=true`，默认）：通过 SSE 协议逐 token 推送生成内容，
Java 后端解析后通过 WebSocket 转发给前端，实现打字机效果。

**非流式模式**（`stream=false`）：等待 Agent 完整生成后一次性返回 JSON。

**支持的 Agent 类型**：
- `claude_code` — 本机 Claude Code CLI
- `codex` — 本机 OpenAI Codex CLI
- `custom` — 自定义 Agent（默认使用 Claude Code CLI）

对齐 API 契约文档第 4.2 节。
""",
    responses={
        200: {
            "description": """
**流式响应**（stream=true）: Content-Type: text/event-stream，
每行格式为 `data: <JSON>\\n\\n`。

**非流式响应**（stream=false）: Content-Type: application/json，
包含 `content` 和 `messageId`。
""",
            "content": {
                "text/event-stream": {
                    "example": _SSE_EXAMPLE,
                },
                "application/json": {
                    "example": {
                        "content": "好的，这是生成的 React 组件代码：\n```javascript\nimport React from 'react';\n\nconst App = () => {\n  return <div>Hello World</div>;\n};\n\nexport default App;\n```",
                        "messageId": "msg_456",
                    },
                },
            },
        },
        400: {
            "description": "请求参数校验失败（context 为空或 agentType 不支持）",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "error": "VALIDATION_ERROR",
                        "message": "context 字段不能为空",
                        "timestamp": "2026-05-25T10:30:00",
                        "path": "/api/agent/chat",
                    },
                },
            },
        },
        502: {
            "description": "Agent 服务调用失败（CLI 进程异常退出或未安装）",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "error": "AGENT_ERROR",
                        "message": "Claude Code CLI 异常退出（code=1）: ...",
                        "timestamp": "2026-05-25T10:30:00",
                        "path": "/api/agent/chat",
                    },
                },
            },
        },
    },
)
async def chat(data: AgentChatRequest, request: Request):
    """接收 Java 后端转发的 Agent 调用请求，根据 stream 参数返回流式或非流式响应。"""
    context = data.context.strip()
    if not context:
        return _error_json(400, "VALIDATION_ERROR", "context 字段不能为空", "/api/agent/chat")

    agent_type = data.agentType
    system_prompt = data.systemPrompt

    # Session tracking: determine if this is the first message in the conversation
    conv_id = data.conversationId
    track_key = f"{conv_id}:{agent_type}" if conv_id else None
    is_first_message = True
    if track_key and track_key in _session_tracker:
        is_first_message = False

    # Fallback: if Java didn't provide a system prompt, look up from local templates
    if not system_prompt and agent_type:
        from prompts.system_prompts import SYSTEM_PROMPTS
        system_prompt = SYSTEM_PROMPTS.get(agent_type, SYSTEM_PROMPTS.get("coder", ""))

    agent_name = AGENT_DISPLAY_NAMES.get(agent_type, agent_type)
    agent_id = f"agent_{agent_type}"

    # Create session workspace directory if specified (Agent isolation)
    import os
    wd = data.workingDirectory
    if wd and wd != ".":
        os.makedirs(wd, exist_ok=True)

    try:
        adapter = AdapterFactory.get_adapter(agent_type)
    except ValueError as e:
        return _error_json(400, "VALIDATION_ERROR", str(e), "/api/agent/chat")

    if data.stream:
        return _stream_response(
            adapter, agent_type, agent_name, agent_id,
            context, system_prompt, data.workingDirectory,
            conv_id, is_first_message, track_key,
        )
    else:
        return await _non_stream_response(
            adapter, context, system_prompt, data.workingDirectory,
            conv_id, is_first_message, track_key,
        )


def _stream_response(adapter, agent_type, agent_name, agent_id, context, system_prompt,
                     working_directory, conversation_id, is_first_message, track_key):
    """SSE 流式响应，严格对齐 API 契约文档 4.2 节 SSE 格式。"""

    async def event_generator():
        nonlocal is_first_message
        message_id = None
        full_text: list[str] = []

        # 获取已存储的 CLI session ID（用于 Codex 等需要显式 session ID 的 CLI）
        existing_session_id = None
        if track_key and track_key in _session_tracker:
            existing_session_id = _session_tracker[track_key].get("cli_session_id")

        async for chunk in adapter.chat_stream(
            message=context,
            system_prompt=system_prompt,
            history=[],
            working_directory=working_directory,
            is_first_message=is_first_message,
            session_id=existing_session_id,
        ):
            chunk_type = chunk.get("type")

            if chunk_type == "msg_start":
                message_id = chunk.get("message_id", "")

            elif chunk_type == "msg_chunk":
                delta = chunk.get("delta", "")
                full_text.append(delta)
                sse_data = {
                    "token": delta,
                    "finish": False,
                    "agentId": agent_id,
                    "agentName": agent_name,
                }
                yield f"data: {json.dumps(sse_data, ensure_ascii=False)}\n\n"

            elif chunk_type == "session_created":
                # Codex 首轮执行后回传新 session UUID，存入 tracker 供后续恢复
                new_session_id = chunk.get("session_id")
                if track_key and new_session_id:
                    _session_tracker[track_key] = {
                        "is_first": False,
                        "cli_session_id": new_session_id,
                    }
                elif track_key:
                    # session ID 解析失败，仅标记非首轮（下次全新执行）
                    _session_tracker[track_key] = {"is_first": False}

            elif chunk_type == "msg_end":
                # Claude：标记会话非首轮，后续消息使用 --continue
                if track_key and is_first_message and track_key not in _session_tracker:
                    _session_tracker[track_key] = {"is_first": False}

                sse_data = {
                    "token": "",
                    "finish": True,
                    "messageId": message_id or "",
                }
                yield f"data: {json.dumps(sse_data, ensure_ascii=False)}\n\n"

                # After agent completes, detect code blocks and upload artifacts
                if conversation_id and message_id:
                    import asyncio
                    from app.utils.artifact_uploader import detect_and_upload
                    asyncio.ensure_future(
                        detect_and_upload("".join(full_text), conversation_id, message_id)
                    )

            elif chunk_type == "error":
                sse_data = {
                    "token": "",
                    "finish": True,
                    "messageId": message_id or "",
                    "error": chunk.get("message", "Unknown error"),
                }
                yield f"data: {json.dumps(sse_data, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


async def _non_stream_response(adapter, context, system_prompt, working_directory,
                                conversation_id, is_first_message, track_key):
    """非流式响应，收集完整内容后返回 JSON，严格对齐 API 契约文档 4.2 节。"""
    full_content = ""
    message_id = ""

    # 获取已存储的 CLI session ID
    existing_session_id = None
    if track_key and track_key in _session_tracker:
        existing_session_id = _session_tracker[track_key].get("cli_session_id")

    async for chunk in adapter.chat_stream(
        message=context,
        system_prompt=system_prompt,
        history=[],
        working_directory=working_directory,
        is_first_message=is_first_message,
        session_id=existing_session_id,
    ):
        chunk_type = chunk.get("type")
        if chunk_type == "msg_start":
            message_id = chunk.get("message_id", "")
        elif chunk_type == "msg_chunk":
            full_content += chunk.get("delta", "")
        elif chunk_type == "session_created":
            new_session_id = chunk.get("session_id")
            if track_key and new_session_id:
                _session_tracker[track_key] = {
                    "is_first": False,
                    "cli_session_id": new_session_id,
                }
            elif track_key:
                _session_tracker[track_key] = {"is_first": False}
        elif chunk_type == "error":
            return _error_json(
                502, "AGENT_ERROR",
                chunk.get("message", "Agent 服务调用失败"),
                "/api/agent/chat",
            )

    # Mark session as started so subsequent messages use --continue
    if track_key and is_first_message and track_key not in _session_tracker:
        _session_tracker[track_key] = {"is_first": False}

    # Detect code blocks and upload artifacts
    if conversation_id and message_id:
        import asyncio
        from app.utils.artifact_uploader import detect_and_upload
        asyncio.ensure_future(
            detect_and_upload(full_content, conversation_id, message_id)
        )

    return JSONResponse(
        status_code=200,
        content=AgentChatResponse(
            content=full_content,
            messageId=message_id,
        ).model_dump(),
    )
