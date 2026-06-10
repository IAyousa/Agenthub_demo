"""
AgentHub — Claude Code 本地 CLI 适配器

本模块封装了对本机安装的 Claude Code CLI 的调用。
ClaudeAdapter 通过 asyncio.subprocess 启动 claude 命令行工具，
使用 --output-format=stream-json 实现逐 token 实时流式输出。

Claude Code CLI 参考：https://docs.anthropic.com/en/docs/claude-code

数据流（stream-json 模式）：
    messages.py 端点
        → ClaudeAdapter.chat_stream()
        → asyncio.create_subprocess_exec("claude", "-p", "--output-format", "stream-json", ...)
        → 逐行读取 stdout JSON Lines（每行一个事件，实时到达）
        → 解析 stream_event.content_block_delta.text_delta
        → yield {"type": "msg_chunk", "delta": "输出文本"}

环境要求：
    - 安装 Claude Code CLI：npm install -g @anthropic-ai/claude-code
    - 设置环境变量 ANTHROPIC_API_KEY
"""

import asyncio
import json
import os
import shutil
import uuid
from typing import AsyncGenerator, List, Optional

from config import settings
from .base_adapter import BaseAdapter


class ClaudeAdapter(BaseAdapter):
    """Claude Code 本地 CLI 适配器。

    通过在本机启动 claude CLI 子进程来完成 Agent 任务。
    Claude Code 是一个完整的 Agent 工具，可以读写文件、执行 shell 命令、
    搜索代码库等，功能远超纯文本 API 调用。

    流式输出：
        使用 --output-format=stream-json + --include-partial-messages + --verbose
        实现逐 token 实时输出。stdout 每行为一个 JSON 事件：
        - stream_event.message_start → msg_start
        - stream_event.content_block_delta.text_delta → msg_chunk（逐 token）
        - stream_event.content_block_delta.thinking_delta → 跳过（内部推理过程）
        - assistant → msg_end

    使用方式：
        adapter = ClaudeAdapter()
        async for chunk in adapter.chat_stream(
            "帮我重构这个模块",
            system_prompt="你是资深Python工程师",
            working_directory="/path/to/project"
        ):
            print(chunk)  # {"type": "msg_chunk", "message_id": "...", "delta": "..."}
    """

    def __init__(self):
        self.cli_command = settings.CLAUDE_CLI_COMMAND
        self.cli_args = list(settings.CLAUDE_CLI_ARGS)
        self.stream_args = list(settings.CLAUDE_STREAM_ARGS)
        self.default_cwd = settings.AGENT_WORKING_DIRECTORY
        self.timeout = settings.AGENT_TIMEOUT

    async def chat_stream(
        self,
        message: str,
        system_prompt: str = "",
        history: List[dict] = None,
        **kwargs
    ) -> AsyncGenerator[dict, None]:
        """调用本地 Claude Code CLI 进行流式对话。

        通过 asyncio 子进程启动 claude -p --output-format stream-json ...，
        逐行读取 stdout JSON Lines 并解析 stream_event 事件，提取 text_delta
        增量文本作为 msg_chunk 流式返回。

        Args:
            message: 用户消息
            system_prompt: 系统提示词
            history: 对话历史
            **kwargs:
                working_directory: 可选，覆盖默认工作目录
                is_first_message: 是否为首轮消息（决定是否使用 --continue）

        Yields:
            {"type": "msg_start", "message_id": "..."}
            {"type": "msg_chunk", "message_id": "...", "delta": "..."}
            {"type": "session_created", "message_id": "...", "session_id": "..."}
            {"type": "msg_end", "message_id": "..."}
            {"type": "error", "message": "..."}
        """
        message_id = str(uuid.uuid4())
        wd = kwargs.get("working_directory")
        if not wd or not os.path.isdir(wd):
            wd = self.default_cwd
        working_directory = wd

        is_first_message = kwargs.get("is_first_message", True)

        # 提前发出 msg_start，即使后续 CLI 启动失败也保证契约完整
        yield {
            "type": "msg_start",
            "message_id": message_id,
            "role": "assistant",
        }

        # Build prompt: first message injects system_prompt; subsequent rely on --continue
        if not is_first_message:
            full_prompt = message
        else:
            if system_prompt:
                full_prompt = f"{message}\n\n---\n\n{system_prompt}"
            else:
                full_prompt = message

        resolved_command = shutil.which(self.cli_command)
        if resolved_command is None:
            yield {
                "type": "error",
                "message": (
                    f"未找到 Claude Code CLI 命令 '{self.cli_command}'。"
                    f"请确认已安装：npm install -g @anthropic-ai/claude-code"
                ),
                "message_id": message_id,
            }
            return

        # Build CLI args: claude ...stream_args... (-p prompt)
        cli_args = [resolved_command] + self.cli_args + self.stream_args

        if not is_first_message:
            cli_args.append("--continue")

        cli_args.extend(["-p", full_prompt])

        try:
            process = await asyncio.create_subprocess_exec(
                *cli_args,
                stdin=asyncio.subprocess.DEVNULL,   # 跳过 stdin（prompt 由 -p 参数传入）
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=working_directory,
            )
        except FileNotFoundError:
            yield {
                "type": "error",
                "message": (
                    f"Claude Code CLI 可执行文件无法启动 '{self.cli_command}'。"
                ),
                "message_id": message_id,
            }
            return

        # Track state across stream-json events
        claude_message_id: Optional[str] = None
        claude_session_id: Optional[str] = None
        has_error = False
        msg_ended = False  # 是否已发送 msg_end

        async def read_stderr():
            """后台读取 stderr，避免管道阻塞，并记录日志。"""
            if process.stderr:
                data = await process.stderr.read()
                if data:
                    print(f"[ClaudeAdapter] stderr: {data.decode('utf-8', errors='replace')[-500:]}", flush=True)

        stderr_task = asyncio.ensure_future(read_stderr())

        try:
            if process.stdout:
                async for line in process.stdout:
                    raw_text = line.decode("utf-8", errors="replace").strip()
                    if not raw_text:
                        continue

                    # stream-json 每行是一个 JSON 事件
                    try:
                        event = json.loads(raw_text)
                    except json.JSONDecodeError:
                        # 非 JSON 行（可能是 warning 或 ANSI 转义残骸），跳过
                        print(f"[ClaudeAdapter] Skipping non-JSON line: {raw_text[:200]}", flush=True)
                        continue

                    event_type = event.get("type")
                    subtype = event.get("subtype")

                    # ============================================================
                    # system.init — 会话初始化元数据，提取 session_id
                    # ============================================================
                    if event_type == "system" and subtype == "init":
                        claude_session_id = event.get("session_id")
                        if claude_session_id:
                            yield {
                                "type": "session_created",
                                "message_id": message_id,
                                "session_id": claude_session_id,
                            }

                    # ============================================================
                    # stream_event — 实时流事件
                    # ============================================================
                    elif event_type == "stream_event":
                        stream_event = event.get("event", {})
                        stream_event_type = stream_event.get("type")

                        if stream_event_type == "message_start":
                            # 消息开始：记录 Claude 侧 message_id
                            msg_obj = stream_event.get("message", {})
                            claude_message_id = msg_obj.get("id", claude_message_id)

                        elif stream_event_type == "content_block_start":
                            # 内容块开始（thinking 或 text）— 无需行动
                            pass

                        elif stream_event_type == "content_block_delta":
                            delta = stream_event.get("delta", {})
                            delta_type = delta.get("type")

                            if delta_type == "text_delta":
                                # 逐 token 文本增量 → msg_chunk
                                text = delta.get("text", "")
                                if text:
                                    yield {
                                        "type": "msg_chunk",
                                        "message_id": message_id,
                                        "delta": text,
                                    }
                            # thinking_delta / signature_delta: 跳过，不推送给用户

                        elif stream_event_type == "message_delta":
                            # 消息级 delta：包含 stop_reason 和 usage
                            # message_stop 紧随其后，那里触发 msg_end
                            pass

                        elif stream_event_type == "message_stop":
                            # 消息流结束 — 触发 msg_end
                            yield {
                                "type": "msg_end",
                                "message_id": message_id,
                            }
                            msg_ended = True

                    # ============================================================
                    # assistant — 中间消息汇总事件（thinking/text block 结束后发送）
                    # 注意：此事件 stop_reason 通常为 null，不是流结束信号
                    # 真正的流结束信号是 stream_event.message_stop
                    # ============================================================
                    elif event_type == "assistant":
                        msg_obj = event.get("message", {})
                        claude_message_id = msg_obj.get("id", claude_message_id)
                        # 兜底：如果 message_stop 因某些原因未触发，检查 stop_reason
                        stop_reason = msg_obj.get("stop_reason")
                        if stop_reason and not msg_ended:
                            yield {
                                "type": "msg_end",
                                "message_id": message_id,
                            }
                            msg_ended = True

        except asyncio.CancelledError:
            process.kill()
            raise

        try:
            returncode = await asyncio.wait_for(process.wait(), timeout=self.timeout)
        except asyncio.TimeoutError:
            process.kill()
            has_error = True
            yield {
                "type": "error",
                "message": f"Claude Code CLI 执行超时（{self.timeout}s）",
                "message_id": message_id,
            }
        else:
            if returncode != 0:
                has_error = True
                stderr_output = b""
                if process.stderr:
                    try:
                        stderr_output = await process.stderr.read()
                    except Exception:
                        pass
                stderr_text = stderr_output.decode("utf-8", errors="replace")[-500:]
                yield {
                    "type": "error",
                    "message": f"Claude Code CLI 异常退出（code={returncode}）: {stderr_text}",
                    "message_id": message_id,
                }
        finally:
            stderr_task.cancel()
            try:
                await stderr_task
            except asyncio.CancelledError:
                pass

        # 如果流没有正常关闭（没收到 assistant 事件），补发 msg_end
        if not has_error and not msg_ended:
            yield {
                "type": "msg_end",
                "message_id": message_id,
            }
