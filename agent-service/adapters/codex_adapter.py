"""
AgentHub — Codex 本地 CLI 适配器

本模块封装了对本机安装的 OpenAI Codex CLI 的调用。
CodexAdapter 通过 asyncio.subprocess 启动 codex 命令行工具，
将用户提示词传入，并以流式方式读取 stdout 输出。

OpenAI Codex CLI 参考：https://github.com/openai/codex

会话记忆机制（对齐 CLI 原生记忆设计方案 v3.1 阶段 2）：
    - 首轮消息：codex exec "{system_prompt}\n\n---\n\n{message}"（创建新会话，注入角色指令）
    - 后续消息：codex exec resume --last "{message}"（在当前工作目录下恢复最近会话，仅传当前消息）
    - Session ID 从 Codex 输出/错误流中提取并回传 session_created 事件，供调试和后续演进使用
    - 每会话使用独立 working_directory，确保 --last 的 cwd 过滤能正确隔离不同会话

数据流：
    messages.py 端点
        → CodexAdapter.chat_stream(is_first_message, session_id)
        → 首轮：codex exec "prompt" → 解析 session ID → session_created 事件
        → 后续：codex exec resume --last "prompt" → 复用当前工作区的最近会话上下文
        → 异步逐行读取 stdout
        → yield {"type": "msg_chunk", "delta": "输出文本"}

环境要求：
    - 安装 OpenAI Codex CLI：npm install -g @openai/codex
    - 设置环境变量 OPENAI_API_KEY
"""

import asyncio
import os
import re
import shutil
import uuid
from typing import AsyncGenerator, List, Optional

from config import settings
from .base_adapter import BaseAdapter


class CodexAdapter(BaseAdapter):
    """OpenAI Codex 本地 CLI 适配器。

    通过在本机启动 codex CLI 子进程来完成 Agent 任务。
    OpenAI Codex CLI 是一个本地 Agent 工具，可以读写文件、执行 shell 命令、
    搜索代码库等，与 Claude Code CLI 类似。

    会话管理：
        首轮执行后从 Codex stdout/stderr 提取 session UUID，后续轮次通过
        'codex exec resume --last' 恢复当前工作区的最近会话上下文，
        避免每轮重新发送历史消息和 system_prompt。

        session_id 当前通过 _session_tracker 存储但不直接传给 CLI（因为
        Codex 的显式 session resume 在某些版本下会报 "no rollout found"），
        --last 基于 cwd 恢复，配合每会话独立 workspace 达到等价隔离效果。
        session_id 保留用于调试日志和未来 Codex 版本升级后的显式恢复。

    使用方式：
        adapter = CodexAdapter()
        async for chunk in adapter.chat_stream(
            "帮我写一个 Python 脚本",
            system_prompt="你是Python专家",
            working_directory="/path/to/project",
            is_first_message=True,
        ):
            print(chunk)  # {"type": "msg_chunk", "delta": "好的..."}
    """

    # Codex 输出中 session UUID 的正则模式
    # 主模式：匹配 "Session ID: a1b2c3d4-..." 或 "Session ID  a1b2c3d4-..."
    SESSION_ID_PATTERN = re.compile(
        r'Session\s*ID[:\s]+([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})',
        re.IGNORECASE,
    )
    # 备选模式：匹配独立行的 UUID（覆盖 Codex 元数据中不以 "Session ID:" 标识的 UUID）
    SESSION_UUID_PATTERN = re.compile(
        r'\b([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})\b',
        re.IGNORECASE,
    )

    def __init__(self):
        self.cli_command = settings.CODEX_CLI_COMMAND
        self.cli_args = list(settings.CODEX_CLI_ARGS)
        self.default_cwd = settings.AGENT_WORKING_DIRECTORY
        self.timeout = settings.AGENT_TIMEOUT

    def _extract_session_id(self, text: str) -> Optional[str]:
        """从 Codex 输出文本中提取 session UUID。

        按优先级尝试两种模式：
        1. 显式 "Session ID: <uuid>" — 标准 Codex 元数据输出
        2. 任意 UUID 格式 — 兜底匹配（排除非 session 的 UUID）
        """
        sid_match = self.SESSION_ID_PATTERN.search(text)
        if sid_match:
            return sid_match.group(1)
        sid_match = self.SESSION_UUID_PATTERN.search(text)
        if sid_match:
            return sid_match.group(1)
        return None

    async def chat_stream(
        self,
        message: str,
        system_prompt: str = "",
        history: List[dict] = None,
        **kwargs
    ) -> AsyncGenerator[dict, None]:
        """调用本地 OpenAI Codex CLI 进行流式对话。

        根据 is_first_message 决定使用 codex exec（首轮）还是
        codex exec resume --last（后续）。首轮从输出中解析 session ID
        并通过 session_created 事件回传，供 messages.py 存入 _session_tracker。

        Args:
            message: 用户消息
            system_prompt: 系统提示词
            history: 对话历史（当前未使用，CLI 自身管理上下文）
            **kwargs:
                working_directory: 可选，覆盖默认工作目录
                is_first_message: 是否为首轮消息（默认 True）
                session_id: 已有会话的 UUID（来自 _session_tracker，当前仅用于日志，
                           实际会话恢复通过 --last + cwd 隔离实现）

        Yields:
            {"type": "msg_start", "message_id": "..."}
            {"type": "msg_chunk", "message_id": "...", "delta": "..."}
            {"type": "session_created", "message_id": "...", "session_id": "uuid"}
            {"type": "msg_end", "message_id": "..."}
            {"type": "error", "message": "..."}
        """
        message_id = str(uuid.uuid4())
        wd = kwargs.get("working_directory")
        if not wd or not os.path.isdir(wd):
            wd = self.default_cwd
        working_directory = wd

        # 从 tracker 读取的 session_id（当前仅用于日志，CLI 通过 --last 恢复）
        stored_session_id = kwargs.get("session_id")
        is_first_message = kwargs.get("is_first_message", True)

        # === 核心逻辑：首轮 vs 后续 ===
        if not is_first_message:
            full_prompt = message
            use_resume = True
            print(f"[CodexAdapter] 后续消息: 使用 exec resume --last 恢复会话"
                  f"（cwd={working_directory}, stored_session={stored_session_id}）", flush=True)
        else:
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n---\n\n{message}"
            else:
                full_prompt = message
            use_resume = False
            print(f"[CodexAdapter] 首轮消息: 创建新会话（cwd={working_directory}）", flush=True)

        yield {
            "type": "msg_start",
            "message_id": message_id,
            "role": "assistant",
        }

        resolved_command = shutil.which(self.cli_command)
        if resolved_command is None:
            yield {
                "type": "error",
                "message": (
                    f"未找到 OpenAI Codex CLI 命令 '{self.cli_command}'。"
                    f"请确认已安装：npm install -g @openai/codex"
                ),
                "message_id": message_id,
            }
            return

        # 构建 CLI 参数
        cli_args = [resolved_command, "exec"]

        if use_resume:
            # 使用 --last 而非显式 session_id 恢复会话：
            # Codex 当前版本下，显式 session resume 可能报 "no rollout found for
            # thread id" 错误。--last 基于工作目录过滤，配合每会话独立的
            # working_directory，能达到同等隔离效果。
            cli_args.extend(["resume", "--last"])

        # 基础 CLI 参数 + 跳过 Git 仓库检查（AgentHub workspace 不在 Git 中）
        if settings.CODEX_SKIP_GIT_CHECK:
            cli_args.append("--skip-git-repo-check")
        cli_args.extend(self.cli_args)
        cli_args.append(full_prompt)

        try:
            process = await asyncio.create_subprocess_exec(
                *cli_args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=working_directory,
            )
        except FileNotFoundError:
            yield {
                "type": "error",
                "message": (
                    f"OpenAI Codex CLI 可执行文件无法启动 '{self.cli_command}'。"
                ),
                "message_id": message_id,
            }
            yield {"type": "msg_end", "message_id": message_id}
            return

        has_error = False
        captured_session_id = None

        # 捕获 stderr 内容用于错误诊断和 session ID 提取
        stderr_buffer: list[bytes] = []

        async def read_stderr():
            """后台读取 stderr，避免管道阻塞，同时提取 session ID 并缓存诊断信息。"""
            nonlocal captured_session_id
            if process.stderr:
                data = await process.stderr.read()
                if data:
                    stderr_buffer.append(data)
                    clean_err = BaseAdapter.strip_ansi(
                        data.decode("utf-8", errors="replace"))
                    if not captured_session_id:
                        captured_session_id = self._extract_session_id(clean_err)

        stderr_task = asyncio.ensure_future(read_stderr())

        try:
            if process.stdout:
                async for line in process.stdout:
                    text = line.decode("utf-8", errors="replace")
                    clean = BaseAdapter.strip_ansi(text)

                    # 首轮执行时尝试从 stdout 中提取 session ID
                    if not use_resume and not captured_session_id:
                        captured_session_id = self._extract_session_id(clean)

                    if clean.strip():
                        yield {
                            "type": "msg_chunk",
                            "message_id": message_id,
                            "delta": clean,
                        }
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
                "message": f"OpenAI Codex CLI 执行超时（{self.timeout}s）",
                "message_id": message_id,
            }
        else:
            if returncode != 0:
                has_error = True
                if stderr_buffer:
                    err_text = b"".join(stderr_buffer).decode(
                        "utf-8", errors="replace")
                    err_snippet = err_text[-500:]
                else:
                    err_snippet = "(stderr 无输出)"
                yield {
                    "type": "error",
                    "message": (
                        f"OpenAI Codex CLI 异常退出（code={returncode}）: "
                        f"{err_snippet}"
                    ),
                    "message_id": message_id,
                }
                print(f"[CodexAdapter] 进程异常退出（code={returncode}）", flush=True)
        finally:
            # 安全等待 stderr 任务结束
            try:
                await asyncio.wait_for(stderr_task, timeout=1)
            except (asyncio.TimeoutError, asyncio.CancelledError):
                stderr_task.cancel()
                try:
                    await stderr_task
                except asyncio.CancelledError:
                    pass
            except Exception:
                pass

        # 首轮执行完成后，通过 session_created 事件回传 session ID
        if not has_error and captured_session_id:
            print(f"[CodexAdapter] 新会话建立: session_id={captured_session_id}",
                  flush=True)
            yield {
                "type": "session_created",
                "message_id": message_id,
                "session_id": captured_session_id,
            }

        if not has_error:
            yield {
                "type": "msg_end",
                "message_id": message_id,
            }
