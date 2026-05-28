"""
AgentHub Agent Service — 消息处理与 Agent 调用端点

本模块是 Agent 服务的核心 API 端点，负责接收 Java 后端转发的用户消息，
调用对应的 LLM 适配器（Claude / Codex），并以 SSE（Server-Sent Events）
格式流式返回生成内容。

调用链路：
    用户 → Vue 前端 → WebSocket → Spring Boot WebSocketController
    → AgentGatewayService → HTTP POST /api/v1/messages/chat/stream
    → 本模块 chat_stream() → AdapterFactory → ClaudeAdapter/CodexAdapter
    → Anthropic/OpenAI API → 流式解析 → SSE 返回 → Spring Boot 转发 WebSocket → 前端

请求格式（JSON）：
    {
        "message": "帮我写一个 React 计数器",
        "agent_type": "claude_code",           # 必填，决定使用哪个适配器
        "system_prompt": "你是一个软件工程师...", # 必填，Agent 的系统提示词
        "history": [                            # 可选，对话历史
            {"role": "user", "content": "..."},
            {"role": "assistant", "content": "..."}
        ]
    }

响应格式（SSE / NDJSON，每行一个 JSON 对象）：
    {"type": "msg_start", "message_id": "uuid", "role": "assistant"}
    {"type": "msg_chunk", "message_id": "uuid", "delta": "增量文本"}
    {"type": "msg_end", "message_id": "uuid"}
"""

import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from adapters.adapter_factory import AdapterFactory
from models import ChatRequest

router = APIRouter()


@router.post("/chat/stream")
async def chat_stream(data: ChatRequest):
    """接收用户消息，调用对应 LLM 适配器进行流式回复。

    本端点被 Java 后端 AgentGatewayService 调用，Java 后端将
    SSE 流逐条转发为 WebSocket 消息推送给前端。
    """
    message = data.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="message 字段不能为空")

    agent_type = data.agent_type
    system_prompt = data.system_prompt
    history = [h.model_dump() for h in data.history]

    try:
        adapter = AdapterFactory.get_adapter(agent_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    async def event_generator():
        async for chunk in adapter.chat_stream(
            message=message,
            system_prompt=system_prompt,
            history=history,
        ):
            yield json.dumps(chunk, ensure_ascii=False) + "\n"

    return StreamingResponse(
        event_generator(),
        media_type="application/x-ndjson",
    )
