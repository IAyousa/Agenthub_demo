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
from config import settings

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


async def _upload_merged_artifacts(
    full_text: str, conversation_id: str, message_id: str, working_directory: str,
) -> None:
    """合并代码块检测 + 工作区扫描 → 一次批量上传 → 一张 project_bundle 卡片。

    流程（顺序执行）：
      1. 从 stdout 文本中检测代码块（不立即上传）
      2. 将代码块写入工作目录磁盘（供 workspace_scanner 发现）
      3. workspace_scanner 扫描磁盘 → 上传到 Java（含真实文件名）
      4. 若 scanner 未找到文件 → 回退：直接上传代码块到 Java
    """
    from app.utils.artifact_uploader import detect_code_blocks, write_blocks_to_workspace, detect_and_upload
    from app.utils.workspace_scanner import scan_and_upload

    # Step 1: 从 stdout 文本中检测代码块
    blocks = detect_code_blocks(full_text)

    # Step 2: 将代码块写入工作目录磁盘（保护已存在的文件）
    if blocks and working_directory:
        write_blocks_to_workspace(blocks, working_directory)

    # Step 3: 工作区扫描（磁盘上已有代码块文件 + Agent 可能写入的其他文件）
    scan_files = await scan_and_upload(conversation_id, message_id, working_directory)

    # Step 4: 若 scanner 未找到任何磁盘文件，回退到上传代码块
    if not scan_files:
        await detect_and_upload(full_text, conversation_id, message_id)
        return

    # scanner 已上传并推送 project_bundle — 权威来源，无需补传
    print(f"[artifact_uploader] Skipped — workspace_scanner already uploaded {len(scan_files)} files",
          flush=True)


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

    # Create session workspace directory (isolated OUTSIDE project tree)
    import os
    from pathlib import Path
    conv_id = data.conversationId
    if conv_id:
        # 强制使用绝对路径，忽略 Java 传入的相对路径
        workspace_root = Path(os.path.expanduser(settings.AGENT_WORKSPACE_ROOT))
        if not workspace_root.is_absolute():
            workspace_root = Path.home() / "agenthub_workspaces"
        wd = str(workspace_root / conv_id)
    else:
        wd = data.workingDirectory if data.workingDirectory and data.workingDirectory != "." else None

    if wd:
        os.makedirs(wd, exist_ok=True)
        # 注入工作区隔离指令 — 禁止 Agent 访问工作目录之外的文件
        isolation_directive = (
            f"\n\n## 工作区隔离规则（必须严格遵守）\n"
            f"- 你的工作目录是: `{wd}`\n"
            f"- 你只能读取、写入、修改工作目录内的文件\n"
            f"- 严禁访问工作目录之外的任何文件或目录（包括父目录和系统目录）\n"
            f"- 严禁使用 `cd ..` 或绝对路径访问工作目录外的内容\n"
            f"- 所有文件操作（读、写、创建、删除）必须在工作目录内进行\n"
            f"- 如果用户要求你查看项目外的内容，请拒绝并说明你只能在工作目录内操作"
        )
        system_prompt = (system_prompt or "") + isolation_directive

    # Orchestrator 路由：agentType 为空/null/orchestrator 时走多 Agent 编排
    is_orchestrator = not agent_type or agent_type == "orchestrator"

    if is_orchestrator:
        from orchestrator import Orchestrator
        orchestrator = Orchestrator()
        if data.stream:
            return _orchestrator_stream(
                orchestrator, context, system_prompt,
                wd, conv_id,
            )
        else:
            return await _orchestrator_non_stream(
                orchestrator, context, system_prompt,
                wd, conv_id,
            )

    try:
        adapter = AdapterFactory.get_adapter(agent_type)
    except ValueError as e:
        return _error_json(400, "VALIDATION_ERROR", str(e), "/api/agent/chat")

    if data.stream:
        return _stream_response(
            adapter, agent_type, agent_name, agent_id,
            context, system_prompt, wd,
            conv_id, is_first_message, track_key,
        )
    else:
        return await _non_stream_response(
            adapter, context, system_prompt, wd,
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

                # After agent completes, detect code blocks + scan workspace
                # → merge and upload as ONE project_bundle
                if conversation_id and message_id:
                    import asyncio
                    asyncio.ensure_future(
                        _upload_merged_artifacts(
                            "".join(full_text), conversation_id, message_id, working_directory)
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

    # Detect code blocks and workspace files
    if conversation_id and message_id:
        import asyncio
        asyncio.ensure_future(
            _upload_merged_artifacts(full_content, conversation_id, message_id, working_directory)
        )

    return JSONResponse(
        status_code=200,
        content=AgentChatResponse(
            content=full_content,
            messageId=message_id,
        ).model_dump(),
    )


# ==========================================================================
# Orchestrator 多 Agent 编排响应
# ==========================================================================

def _orchestrator_stream(orchestrator, context, system_prompt,
                         working_directory, conversation_id):
    """Orchestrator 流式响应 — 多 Agent 协作编排。"""

    async def event_generator():
        message_id = None
        full_text: list[str] = []

        async for chunk in orchestrator.execute(
            message=context,
            working_directory=working_directory,
            conversation_id=conversation_id,
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
                    "agentId": chunk.get("agent_id", "agent_system"),
                    "agentName": chunk.get("agent_name", "Orchestrator"),
                }
                yield f"data: {json.dumps(sse_data, ensure_ascii=False)}\n\n"

            elif chunk_type == "agent_switch":
                # 仅更新 Agent 信息，不产生 token（避免幽灵占位符）
                pass

            elif chunk_type == "msg_end":
                sse_data = {
                    "token": "",
                    "finish": True,
                    "messageId": message_id or "",
                }
                yield f"data: {json.dumps(sse_data, ensure_ascii=False)}\n\n"

                # Artifact detection + workspace scan → merged project_bundle
                if conversation_id and message_id:
                    import asyncio
                    asyncio.ensure_future(
                        _upload_merged_artifacts("".join(full_text), conversation_id, message_id, working_directory)
                    )

            elif chunk_type == "error":
                sse_data = {
                    "token": "",
                    "finish": True,
                    "messageId": message_id or "",
                    "error": chunk.get("message", "Orchestrator error"),
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


async def _orchestrator_non_stream(orchestrator, context, system_prompt,
                                    working_directory, conversation_id):
    """Orchestrator 非流式响应 — 收集完整结果后返回 JSON。"""
    full_content = ""
    message_id = ""

    async for chunk in orchestrator.execute(
        message=context,
        working_directory=working_directory,
        conversation_id=conversation_id,
    ):
        chunk_type = chunk.get("type")
        if chunk_type == "msg_start":
            message_id = chunk.get("message_id", "")
        elif chunk_type == "msg_chunk":
            full_content += chunk.get("delta", "")
        elif chunk_type == "agent_switch":
            full_content += f"\n\n**{chunk.get('agent_name', 'Agent')}**: "
        elif chunk_type == "error":
            return _error_json(
                502, "AGENT_ERROR",
                chunk.get("message", "Orchestrator 执行失败"),
                "/api/agent/chat",
            )

    if conversation_id and message_id:
        import asyncio
        asyncio.ensure_future(
            _upload_merged_artifacts(full_content, conversation_id, message_id, working_directory)
        )

    return JSONResponse(
        status_code=200,
        content=AgentChatResponse(
            content=full_content,
            messageId=message_id,
        ).model_dump(),
    )
