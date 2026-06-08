"""
AgentHub — Orchestrator 多 Agent 任务编排器

采用 Claude Code 作为编排大脑：分析用户意图 → 输出 JSON 执行计划 →
按顺序调用子 Agent → 流式返回结果。

编排流程：
    用户消息 → Orchestrator._plan() → Claude 输出 JSON 计划
    → 按计划逐步骤调用子 Agent
    → 每步发送 agent_switch 事件通知前端切换头像
    → 汇总流式返回

参考：agent_collaboration/Orchestrator 调度器设计方案文档.md §2 方案B
"""

import json
import re
from typing import AsyncGenerator

from adapters.adapter_factory import AdapterFactory
from prompts.system_prompts import SYSTEM_PROMPTS


# Orchestrator 专用的计划生成提示词（在通用提示词之后追加）
_PLAN_INSTRUCTION = """
## 你的工作方式

当收到用户请求后，你必须按以下格式输出一个 JSON 执行计划（仅 JSON，不要其他文字）：

```json
{
  "analysis": "一句话分析用户需求",
  "steps": [
    {"agent": "claude_code", "task": "具体的任务描述，包含所有必要上下文"},
    {"agent": "codex", "task": "具体的任务描述"}
  ]
}
```

规则：
- `agent` 必须是 "claude_code"（全栈工程师，擅长后端/架构/审查）或 "codex"（前端专家，擅长组件/样式/交互）
- 简单任务用 1 个 Agent，跨领域任务用 2 个 Agent
- 每个 `task` 必须自包含（包含足够的上下文让子 Agent 独立完成）
- 如果用户请求模糊，输出空 steps 数组并追问
"""


class Orchestrator:
    """LLM 驱动的多 Agent 任务编排器。"""

    def __init__(self):
        self.factory = AdapterFactory

    async def _plan(self, message: str, working_directory: str) -> dict:
        """调用 Claude Code 分析任务，输出 JSON 执行计划。"""
        orchestrator_prompt = SYSTEM_PROMPTS.get("orchestrator", "") + _PLAN_INSTRUCTION

        adapter = self.factory.get_adapter("claude_code")
        full_output = ""

        async for chunk in adapter.chat_stream(
            message=message,
            system_prompt=orchestrator_prompt,
            history=[],
            working_directory=working_directory,
        ):
            if chunk.get("type") == "msg_chunk":
                full_output += chunk.get("delta", "")

        return self._parse_plan(full_output)

    def _parse_plan(self, text: str) -> dict:
        """从 Claude 输出中提取 JSON 执行计划。"""
        # 尝试多种方式提取 JSON
        strategies = [
            # 1. 匹配 ```json ... ``` 代码块
            lambda t: re.search(r'```json\s*\n(.*?)\n\s*```', t, re.DOTALL),
            # 2. 匹配 ``` ... ``` 代码块
            lambda t: re.search(r'```\s*\n(\{.*?\})\s*\n\s*```', t, re.DOTALL),
            # 3. 匹配裸 JSON 对象
            lambda t: re.search(r'\{[^{}]*"steps"\s*:\s*\[.*?\][^{}]*\}', t, re.DOTALL),
        ]

        for strategy in strategies:
            match = strategy(text)
            if match:
                try:
                    return json.loads(match.group(1))
                except (json.JSONDecodeError, IndexError):
                    continue

        # 解析失败：返回空计划（由 Orchestrator 自行回答）
        return {"analysis": "无法解析计划", "steps": []}

    async def execute(
        self,
        message: str,
        working_directory: str,
        conversation_id: str = None,
    ) -> AsyncGenerator[dict, None]:
        """执行编排：分析 → 分派子 Agent → 汇总。

        Yields:
            {"type": "agent_switch", "agent_id": "agent_claude_code", "agent_name": "Claude Code"}
            {"type": "msg_chunk", "delta": "...", "agent_id": "..."}
            {"type": "msg_end", "message_id": "..."}
        """
        import uuid

        message_id = str(uuid.uuid4())

        # Step 1: 生成执行计划
        yield {
            "type": "msg_start",
            "message_id": message_id,
            "role": "assistant",
        }
        yield {
            "type": "agent_switch",
            "agent_id": "agent_system",
            "agent_name": "Orchestrator",
            "message": "正在分析任务...",
        }

        try:
            plan = await self._plan(message, working_directory)
        except Exception:
            plan = {"analysis": "计划生成失败", "steps": []}

        steps = plan.get("steps", [])

        if not steps:
            # 无有效计划：Orchestrator 自行简要回复
            yield {
                "type": "msg_chunk",
                "message_id": message_id,
                "delta": plan.get("analysis", "我需要更多信息来理解你的需求，能具体说说吗？"),
                "agent_id": "agent_system",
                "agent_name": "Orchestrator",
            }
            yield {"type": "msg_end", "message_id": message_id}
            return

        # Step 2: 按顺序执行每个子任务
        for i, step in enumerate(steps):
            agent_type = step.get("agent", "claude_code")
            task = step.get("task", message)
            is_last = (i == len(steps) - 1)

            # 获取 Agent 显示名称
            agent_display_names = {
                "claude_code": "Claude Code",
                "codex": "Codex",
                "custom": "Custom Agent",
            }
            agent_name = agent_display_names.get(agent_type, agent_type)
            agent_id = f"agent_{agent_type}"

            # 通知前端切换 Agent 头像
            yield {
                "type": "agent_switch",
                "agent_id": agent_id,
                "agent_name": agent_name,
                "message": f"正在调用 {agent_name} 处理: {task[:50]}...",
            }

            # 调用子 Agent（无状态执行，不传 is_first_message）
            try:
                adapter = self.factory.get_adapter(agent_type)
            except ValueError:
                yield {
                    "type": "msg_chunk",
                    "message_id": message_id,
                    "delta": f"\n\n> ⚠️ Agent 类型 '{agent_type}' 不可用，跳过此步骤。\n\n",
                    "agent_id": "agent_system",
                    "agent_name": "Orchestrator",
                }
                continue

            # 子 Agent 的 system prompt（简短版，任务 prompt 已自包含）
            sub_prompt = SYSTEM_PROMPTS.get(agent_type, "")
            # 截取前 200 字作为角色提示，避免与 task 内容重复
            role_hint = sub_prompt.split("\n")[0] if sub_prompt else ""

            async for chunk in adapter.chat_stream(
                message=task,
                system_prompt=role_hint,
                history=[],
                working_directory=working_directory,
            ):
                chunk_type = chunk.get("type")
                if chunk_type == "msg_chunk":
                    yield {
                        "type": "msg_chunk",
                        "message_id": message_id,
                        "delta": chunk.get("delta", ""),
                        "agent_id": agent_id,
                        "agent_name": agent_name,
                    }
                elif chunk_type == "error":
                    yield {
                        "type": "msg_chunk",
                        "message_id": message_id,
                        "delta": f"\n\n> ⚠️ {agent_name} 出错: {chunk.get('message', '未知错误')}\n\n",
                        "agent_id": "agent_system",
                        "agent_name": "Orchestrator",
                    }

            # 步骤之间加分隔
            if not is_last:
                yield {
                    "type": "msg_chunk",
                    "message_id": message_id,
                    "delta": "\n\n---\n\n",
                    "agent_id": "agent_system",
                    "agent_name": "Orchestrator",
                }

        yield {"type": "msg_end", "message_id": message_id}
