"""
AgentHub — DeepSeek 适配器

本模块封装了对 DeepSeek Chat Completions API 的流式调用。
DeepSeek API 兼容 OpenAI Chat Completions 格式，因此适配器结构
与 CodexAdapter 类似，仅配置来源和默认模型不同。

DeepSeek API 参考：https://platform.deepseek.com/api-docs

可用模型：
    - deepseek-v4-pro   (DeepSeek V4 Pro)
    - deepseek-v4-flash  (DeepSeek V4 Flash)

数据流：
    messages.py 端点
        → DeepSeekAdapter.chat_stream()
        → httpx 异步 POST → api.deepseek.com/v1/chat/completions（stream=true）
        → 逐行读取 HTTP 响应流
        → 解析 SSE data 字段中的 JSON
        → 提取 choices[0].delta.content
        → yield {"type": "msg_chunk", "delta": "text"}
"""

import json
import uuid
from typing import AsyncGenerator, List, Optional

import httpx

from config import settings
from .base_adapter import BaseAdapter


class DeepSeekAdapter(BaseAdapter):
    """DeepSeek Chat Completions API 适配器。

    DeepSeek API 完全兼容 OpenAI 的 Chat Completions 接口格式，
    仅需替换 API URL 和认证 Key 即可接入。

    使用方式：
        adapter = DeepSeekAdapter(model="deepseek-v4-pro")
        async for chunk in adapter.chat_stream("你好", system_prompt="你是..."):
            print(chunk)  # {"type": "msg_chunk", "delta": "你好！"}
    """

    def __init__(self, model: str = None):
        self.api_url = settings.DEEPSEEK_API_URL
        self.api_key = settings.DEEPSEEK_API_KEY
        self.model = model or settings.DEEPSEEK_PRO_MODEL
        self.max_tokens = settings.AGENT_MAX_TOKENS
        self.timeout = settings.AGENT_TIMEOUT

    async def chat_stream(
        self,
        message: str,
        system_prompt: str = "",
        history: List[dict] = None,
        **kwargs
    ) -> AsyncGenerator[dict, None]:
        """调用 DeepSeek Chat Completions API 进行流式对话。

        DeepSeek SSE 响应格式（与 OpenAI 一致）：
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
