"""
AgentHub — Codex 本地 CLI 适配器

本模块封装了对本机安装的 OpenAI Codex CLI 的调用。
CodexAdapter 通过 asyncio.subprocess 启动 codex 命令行工具，
将用户提示词传入，并以流式方式读取 stdout 输出。

OpenAI Codex CLI 参考：https://github.com/openai/codex

数据流：
    messages.py 端点
        → CodexAdapter.chat_stream()
        → asyncio.create_subprocess_exec("codex", "exec", prompt)
        → 异步逐行读取 stdout
        → yield {"type": "msg_chunk", "delta": "输出文本"}

环境要求：
    - 安装 OpenAI Codex CLI：npm install -g @openai/codex
    - 设置环境变量 OPENAI_API_KEY
"""

import asyncio
import os
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

    使用方式：
        adapter = CodexAdapter()
        async for chunk in adapter.chat_stream(
            "帮我写一个 Python 脚本",
            system_prompt="你是Python专家",
            working_directory="/path/to/project"
        ):
            print(chunk)  # {"type": "msg_chunk", "delta": "好的..."}
    """

    def __init__(self):
        self.cli_command = settings.CODEX_CLI_COMMAND
        self.cli_args = list(settings.CODEX_CLI_ARGS)
        self.default_cwd = settings.AGENT_WORKING_DIRECTORY
        self.timeout = settings.AGENT_TIMEOUT

    async def chat_stream(
        self,
        message: str,
        system_prompt: str = "",
        history: List[dict] = None,
        **kwargs
    ) -> AsyncGenerator[dict, None]:
        """调用本地 OpenAI Codex CLI 进行流式对话。

        通过 asyncio 子进程启动 codex exec <prompt>，逐行读取 stdout
        并封装为 SSE 消息块流式返回。

        Args:
            message: 用户消息
            system_prompt: 系统提示词
            history: 对话历史
            **kwargs:
                working_directory: 可选，覆盖默认工作目录

        Yields:
            {"type": "msg_start", "message_id": "..."}
            {"type": "msg_chunk", "message_id": "...", "delta": "..."}
            {"type": "msg_end", "message_id": "..."}
            {"type": "error", "message": "..."}
        """
        message_id = str(uuid.uuid4())
        wd = kwargs.get("working_directory")
        if not wd or not os.path.isdir(wd):
            wd = self.default_cwd
        working_directory = wd
        full_prompt = BaseAdapter.build_prompt(message, system_prompt, history)

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

        cli_args = [resolved_command, "exec"] + self.cli_args + [full_prompt]

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

        async def read_stderr():
            """后台读取 stderr，避免管道阻塞。"""
            if process.stderr:
                await process.stderr.read()

        stderr_task = asyncio.ensure_future(read_stderr())

        try:
            if process.stdout:
                async for line in process.stdout:
                    text = line.decode("utf-8", errors="replace")
                    clean = BaseAdapter.strip_ansi(text)
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
                stderr_output = b""
                if process.stderr:
                    try:
                        stderr_output = await process.stderr.read()
                    except Exception:
                        pass
                stderr_text = stderr_output.decode("utf-8", errors="replace")[-500:]
                yield {
                    "type": "error",
                    "message": f"OpenAI Codex CLI 异常退出（code={returncode}）: {stderr_text}",
                    "message_id": message_id,
                }
        finally:
            stderr_task.cancel()
            try:
                await stderr_task
            except asyncio.CancelledError:
                pass

        if not has_error:
            yield {
                "type": "msg_end",
                "message_id": message_id,
            }
