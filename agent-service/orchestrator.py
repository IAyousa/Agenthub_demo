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
    {"agent": "claude_code", "task": "具体的任务描述"},
    {"agent": "codex", "task": "具体的任务描述"}
  ]
}
```

规则：
- `agent`: "claude_code"（全栈工程师，首选，可处理所有任务）或 "codex"（前端专家，仅在前端任务明确且复杂时使用）
- **重要**: 绝大多数任务用 1 个 Agent 即可。只有明确需要两个不同领域专家时才用 2 个
- **优先选 claude_code**：除非任务是纯前端（HTML/CSS/JS组件），否则都用 claude_code
- 对话/聊天/问候/简单问答：用 claude_code，1 个步骤
- 每个 `task` 必须自包含且**只描述要做什么，绝对不要提及 Agent 名称**
- 输出必须是纯 JSON，不要任何解释文字"""


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

        print(f"[Orchestrator] 开始分析任务: {message[:80]}...", flush=True)
        try:
            plan = await self._plan(message, working_directory)
        except Exception as e:
            print(f"[Orchestrator] 计划生成异常: {e}", flush=True)
            plan = {"analysis": "计划生成失败", "steps": []}

        steps = plan.get("steps", [])
        print(f"[Orchestrator] 执行计划: {len(steps)} 个步骤, analysis={plan.get('analysis', 'N/A')}", flush=True)

        if not steps:
            # 无有效计划：退化为单 Agent 模式，直接交给 Claude Code 处理
            print(f"[Orchestrator] 计划为空，退化为单Agent模式", flush=True)
            fallback_adapter = self.factory.get_adapter("claude_code")
            async for chunk in fallback_adapter.chat_stream(
                message=message,
                system_prompt=SYSTEM_PROMPTS.get("claude_code", ""),
                history=[],
                working_directory=working_directory,
            ):
                if chunk.get("type") == "msg_chunk":
                    yield {
                        "type": "msg_chunk",
                        "message_id": message_id,
                        "delta": chunk.get("delta", ""),
                        "agent_id": "agent_claude_code",
                        "agent_name": "Claude Code",
                    }
            yield {"type": "msg_end", "message_id": message_id}
            return

        # Step 2: 按顺序执行每个子任务
        had_error = False
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

            print(f"[Orchestrator] 步骤 {i+1}/{len(steps)}: 调度 {agent_name} → {task[:60]}...", flush=True)

            # 子 Agent 使用完整 system prompt
            sub_prompt = SYSTEM_PROMPTS.get(agent_type, "")
            # 注入工作区隔离指令
            if working_directory and working_directory != ".":
                sub_prompt += (
                    f"\n\n## 工作区隔离规则（必须严格遵守）\n"
                    f"- 你的工作目录是: `{working_directory}`\n"
                    f"- 你只能在工作目录内读写文件，严禁访问外部目录\n"
                    f"- 严禁使用 cd .. 或绝对路径访问工作目录外的内容\n"
                    f"- 所有文件操作必须在工作目录内进行"
                )

            async for chunk in adapter.chat_stream(
                message=task,
                system_prompt=sub_prompt,
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
                    had_error = True

            # 降级：子 Agent 失败且非 Claude Code → 自动用 Claude 重试
            if had_error and agent_type != "claude_code":
                print(f"[Orchestrator] {agent_name} 失败，降级到 Claude Code", flush=True)
                yield {
                    "type": "agent_switch",
                    "agent_id": "agent_claude_code",
                    "agent_name": "Claude Code (降级)",
                }
                fallback = self.factory.get_adapter("claude_code")
                fallback_prompt = SYSTEM_PROMPTS.get("claude_code", "")
                if working_directory and working_directory != ".":
                    fallback_prompt += (
                        f"\n\n## 工作区隔离规则（必须严格遵守）\n"
                        f"- 你的工作目录是: `{working_directory}`\n"
                        f"- 你只能在工作目录内读写文件，严禁访问外部目录\n"
                        f"- 严禁使用 cd .. 或绝对路径访问工作目录外的内容\n"
                        f"- 所有文件操作必须在工作目录内进行"
                    )
                async for chunk in fallback.chat_stream(
                    message=task,
                    system_prompt=fallback_prompt,
                    history=[],
                    working_directory=working_directory,
                ):
                    if chunk.get("type") == "msg_chunk":
                        yield {
                            "type": "msg_chunk",
                            "message_id": message_id,
                            "delta": chunk.get("delta", ""),
                            "agent_id": "agent_claude_code",
                            "agent_name": "Claude Code (降级)",
                        }
            elif had_error:
                yield {
                    "type": "msg_chunk",
                    "message_id": message_id,
                    "delta": "\n\n> ⚠️ Claude Code 执行失败，请稍后重试。\n\n",
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

        print(f"[Orchestrator] 全部 {len(steps)} 个步骤执行完成", flush=True)
        yield {"type": "msg_end", "message_id": message_id}
