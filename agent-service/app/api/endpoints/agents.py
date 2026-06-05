"""
AgentHub Agent Service — Agent 注册表工具模块

从 config.settings 的 AGENT_REGISTRY 获取 Agent 元数据列表，
提供模块级函数供 Python 端其他功能直接 import 使用。

数据流：
    config.py AGENT_REGISTRY（list） → 内存缓存
        → get_agents() / get_agent() / agent_exists() — 供其他模块调用

注意事项：
    - AGENT_REGISTRY 是 fallback 缓存，Java DB 是 Agent 元数据的唯一权威数据源
    - 当 Java 通过 availableAgents[] 传入 Agent 列表时，以 Java 传入的为准

使用方式：
    from app.api.endpoints.agents import get_agents, get_agent, agent_exists

    all_agents = get_agents()
    claude = get_agent("claude_code")
    if agent_exists("orchestrator"):
        ...
"""

from typing import Optional
from config import settings

# ==========================================================================
# Agent 配置加载
# ==========================================================================
_AGENTS: list = settings.AGENT_REGISTRY


def reload_agents() -> list:
    """强制重新加载 Agent 注册表。

    从 config.settings 重新读取 AGENT_REGISTRY，
    用于 .env 修改后无需重启服务的热更新场景。

    Returns:
        list[dict]: 最新的 Agent 元数据列表
    """
    global _AGENTS
    _AGENTS = settings.AGENT_REGISTRY
    return _AGENTS


def get_agents(status: Optional[str] = None) -> list:
    """获取所有 Agent 列表。

    Args:
        status: 可选过滤。None=全部，"active"=仅活跃，"inactive"=仅停用

    Returns:
        list[dict]: Agent 元数据列表
    """
    if status:
        return [a for a in _AGENTS if a.get("status") == status]
    return list(_AGENTS)


def get_agent(agent_id: str) -> Optional[dict]:
    """按 ID 获取单个 Agent 的完整元数据。

    Args:
        agent_id: "claude_code" / "codex" / "orchestrator" / "custom"

    Returns:
        dict | None: Agent 元数据，不存在返回 None
    """
    for agent in _AGENTS:
        if agent.get("id") == agent_id:
            return agent
    return None


def agent_exists(agent_id: str) -> bool:
    """检查指定 Agent 是否已注册。"""
    return any(a.get("id") == agent_id for a in _AGENTS)
