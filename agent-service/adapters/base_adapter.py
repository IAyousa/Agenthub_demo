"""
AgentHub Agent Service — Agent 适配器抽象基类

本模块定义了所有 LLM Agent 适配器必须实现的统一接口契约。
每个具体适配器（ClaudeAdapter、CodexAdapter）继承此基类并实现
chat_stream 方法，通过 SSE 协议流式返回 LLM 生成内容。

接口契约：
    - chat_stream 必须是异步生成器，逐个 yield 消息块
    - 消息块格式为 dict，包含 type 字段：
        {"type": "msg_start", "message_id": "uuid", "sender_id": "...", "role": "assistant"}
        {"type": "msg_chunk", "message_id": "uuid", "delta": "增量文本"}
        {"type": "msg_end", "message_id": "uuid"}
    - 调用方（messages.py 端点）通过异步迭代消费这些消息块并转发给客户端

扩展新 Agent 的方法：
    1. 创建 new_adapter.py，继承 BaseAdapter
    2. 实现 chat_stream 方法
    3. 在 AdapterFactory 中注册新的类型映射
"""

import re
from typing import AsyncGenerator, List, Any

ANSI_ESCAPE_RE = re.compile(r"\x1b\[[0-9;]*[a-zA-Z]")


class BaseAdapter:
    """Agent 适配器抽象基类，所有 LLM 适配器的契约定义。

    这里不声明抽象方法，而是通过文档约定接口，因为 Python 的
    ABC 机制在流式生成器场景下会增加不必要的复杂度。
    """

    @staticmethod
    def strip_ansi(text: str) -> str:
        """移除字符串中的 ANSI 转义序列（颜色代码等）。"""
        return ANSI_ESCAPE_RE.sub("", text)

    @staticmethod
    def build_prompt(
        message: str,
        system_prompt: str = "",
        history: List[dict] = None,
    ) -> str:
        """将系统提示词、历史记录和用户消息组合成完整 prompt。"""
        parts = []
        if system_prompt:
            parts.append(system_prompt)
        if history:
            for entry in history:
                role = entry.get("role", "user")
                content = entry.get("content", "")
                if role == "user":
                    parts.append(f"用户：{content}")
                elif role == "assistant":
                    parts.append(f"助手：{content}")
        parts.append(message)
        return "\n\n".join(parts)

    async def chat_stream(
        self,
        message: str,
        system_prompt: str = "",
        history: List[dict] = None,
        **kwargs
    ) -> AsyncGenerator[dict, None]:
        """流式对话接口，逐个 yield SSE 消息块。

        Args:
            message: 用户当前发送的消息文本
            system_prompt: Agent 的系统提示词（从数据库 agents.system_prompt 读取）
            history: 对话历史列表，格式为 [{"role": "user/assistant", "content": "..."}, ...]
            **kwargs: 额外参数，传递给具体 LLM API（如 temperature、max_tokens）

        Yields:
            dict: SSE 消息块
                - {"type": "msg_start", "message_id": str, "sender_id": str, "role": str}
                - {"type": "msg_chunk", "message_id": str, "delta": str}
                - {"type": "msg_end", "message_id": str}

        Raises:
            NotImplementedError: 子类必须重写此方法
        """
        raise NotImplementedError("子类必须实现 chat_stream 方法")
