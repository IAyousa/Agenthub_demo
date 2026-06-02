"""
AgentHub — Agent 适配器工厂

本模块是适配器模式的核心工厂，负责根据 Agent 类型（agent.type）
返回对应的 Agent 适配器实例。

类型映射规则：
    claude_code       → ClaudeAdapter（本地 Claude Code CLI，执行任务于本机）
    codex             → CodexAdapter（本地 OpenAI Codex CLI，执行任务于本机）
    custom            → ClaudeAdapter（自定义 Agent 默认使用 Claude Code）

扩展方法：
    在 ADAPTER_MAP 中新增映射即可，无需修改工厂逻辑。

使用方式：
    adapter = AdapterFactory.get_adapter("claude_code")
    async for chunk in adapter.chat_stream("你好", system_prompt="...",
                                            working_directory="/path/to/project"):
        ...
"""

from .base_adapter import BaseAdapter
from .claude_adapter import ClaudeAdapter
from .codex_adapter import CodexAdapter


ADAPTER_MAP = {
    "claude_code": ClaudeAdapter,
    "codex": CodexAdapter,
    "custom": ClaudeAdapter,
}


class AdapterFactory:
    """适配器工厂，根据 Agent 类型创建对应的 LLM 适配器实例。"""

    @staticmethod
    def get_adapter(agent_type: str) -> BaseAdapter:
        """获取与 Agent 类型对应的适配器实例。

        Args:
            agent_type: Agent 类型，对应 agents 表的 type 字段。
                        可选值：claude_code、codex、custom

        Returns:
            BaseAdapter: 对应的适配器实例

        Raises:
            ValueError: 无法识别的 agent_type 时抛出
        """
        adapter_cls = ADAPTER_MAP.get(agent_type)
        if adapter_cls is None:
            raise ValueError(
                f"不支持的 Agent 类型: {agent_type}，"
                f"支持的类型: {list(ADAPTER_MAP.keys())}"
            )
        return adapter_cls()
