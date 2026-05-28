"""
AgentHub — Codex 适配器

本模块封装了对 OpenAI Chat Completions API 的流式调用。
CodexAdapter 将内部消息格式转换为 OpenAI API 格式，并通过
SSE 流式解析响应，逐块返回。

OpenAI API 参考：https://platform.openai.com/docs/api-reference/chat

数据流：
    messages.py 端点
        → CodexAdapter.chat_stream()
        → httpx 异步 POST → api.openai.com/v1/chat/completions（stream=true）
        → 逐行读取 HTTP 响应流
        → 解析 SSE data 字段中的 JSON
        → 提取 choices[0].delta.content
        → yield {"type": "msg_chunk", "delta": "text"}

兼容性说明：
    Codex 适配器使用 OpenAI 标准 Chat Completions API，因此也兼容
    任何 OpenAI API 兼容的服务（如 Azure OpenAI、本地 vLLM 等），
    只需修改 config.py 中的 CODEX_API_URL 即可。
"""

import json
import uuid
from typing import AsyncGenerator, List, Optional

import httpx

from config import settings
from .base_adapter import BaseAdapter


class CodexAdapter(BaseAdapter):
    """OpenAI Chat Completions API 适配器。

    支持 GPT-4o、GPT-4、GPT-3.5 等模型，通过环境变量配置 API Key
    和模型名称（见 config.py）。

    使用方式：
        adapter = CodexAdapter()
        async for chunk in adapter.chat_stream("你好", system_prompt="你是..."):
            print(chunk)  # {"type": "msg_chunk", "delta": "你好！"}
    """

    def __init__(self):
        self.api_url = settings.CODEX_API_URL
        self.api_key = settings.CODEX_API_KEY
        self.model = settings.CODEX_MODEL
        self.max_tokens = settings.AGENT_MAX_TOKENS
        self.timeout = settings.AGENT_TIMEOUT

    async def chat_stream(
        self,
        message: str,
        system_prompt: str = "",
        history: List[dict] = None,
        **kwargs
    ) -> AsyncGenerator[dict, None]:
        """调用 OpenAI Chat Completions API 进行流式对话。

        OpenAI SSE 响应格式：
            data: {"id":"...","choices":[{"delta":{"content":"增量文字"},"index":0}]}

        我们提取 choices[0].delta.content 作为增量输出。
        如果 content 为 None（首帧可能不含内容），则跳过。
        """
        message_id = str(uuid.uuid4())

        api_messages = []
        if system_prompt:
            api_messages.append({"role": "system", "content": system_prompt})
        if history:
            api_messages.extend(history)
        api_messages.append({"role": "user", "content": message})

        request_body = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "stream": True,
            "messages": api_messages,
        }

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
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if not line or not line.startswith("data: "):
                        continue
                    data_str = line[len("data: "):]

                    if data_str.strip() == "[DONE]":
                        break

                    try:
                        event = json.loads(data_str)
                    except json.JSONDecodeError:
                        continue

                    choices = event.get("choices", [])
                    if choices:
                        delta = choices[0].get("delta", {})
                        content = delta.get("content")
                        if content:
                            yield {
                                "type": "msg_chunk",
                                "message_id": message_id,
                                "delta": content,
                            }

        yield {
            "type": "msg_end",
            "message_id": message_id,
        }
