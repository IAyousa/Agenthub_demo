"""
AgentHub — Claude Code 适配器

本模块封装了对 Anthropic Claude Messages API 的流式调用。
ClaudeAdapter 负责将内部消息格式转换为 Anthropic API 格式，
并通过 SSE（Server-Sent Events）流式解析响应，逐块返回。

Anthropic API 参考：https://docs.anthropic.com/en/api/messages

数据流：
    messages.py 端点
        → ClaudeAdapter.chat_stream()
        → httpx 异步 POST → api.anthropic.com/v1/messages（stream=true）
        → 逐行读取 HTTP 响应流
        → 解析 SSE data 字段中的 JSON
        → 提取 content_block_delta.delta.text
        → yield {"type": "msg_chunk", "delta": "text"}
"""

import json
import uuid
from typing import AsyncGenerator, List, Optional

import httpx

from config import settings
from .base_adapter import BaseAdapter


class ClaudeAdapter(BaseAdapter):
    """Anthropic Claude Messages API 适配器。

    支持 Claude 3.5 Sonnet / Claude 3 Opus 等模型，通过环境变量
    配置 API Key 和模型名称（见 config.py）。

    使用方式：
        adapter = ClaudeAdapter()
        async for chunk in adapter.chat_stream("你好", system_prompt="你是..."):
            print(chunk)  # {"type": "msg_chunk", "delta": "你好！"}
    """

    def __init__(self):
        self.api_url = settings.CLAUDE_API_URL
        self.api_key = settings.CLAUDE_API_KEY
        self.model = settings.CLAUDE_MODEL
        self.max_tokens = settings.AGENT_MAX_TOKENS
        self.timeout = settings.AGENT_TIMEOUT

    async def chat_stream(
        self,
        message: str,
        system_prompt: str = "",
        history: List[dict] = None,
        **kwargs
    ) -> AsyncGenerator[dict, None]:
        """调用 Anthropic Claude API 进行流式对话。

        Anthropic SSE 响应格式：
            event: content_block_delta
            data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"增量文字"}}

        我们只提取 type=content_block_delta 的事件中 delta.text 作为增量输出。
        """
        message_id = str(uuid.uuid4())

        messages = []
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": message})

        request_body = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "stream": True,
            "messages": messages,
        }
        if system_prompt:
            request_body["system"] = system_prompt

        yield {
            "type": "msg_start",
            "message_id": message_id,
            "role": "assistant",
        }

        async with httpx.AsyncClient(timeout=httpx.Timeout(self.timeout)) as client:
            async with client.stream(
                "POST",
                self.api_url,
                json=request_body,
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if not line or not line.startswith("data: "):
                        continue
                    data_str = line[len("data: "):]

                    try:
                        event = json.loads(data_str)
                    except json.JSONDecodeError:
                        continue

                    if event.get("type") == "content_block_delta":
                        delta = event.get("delta", {})
                        text = delta.get("text", "")
                        if text:
                            yield {
                                "type": "msg_chunk",
                                "message_id": message_id,
                                "delta": text,
                            }

        yield {
            "type": "msg_end",
            "message_id": message_id,
        }
