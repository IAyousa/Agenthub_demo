"""
AgentHub Agent Service — 全局配置

基于 pydantic-settings 的 BaseSettings，自动从以下来源加载配置（优先级从高到低）：
  1. 命令行环境变量
  2. agent-service/.env 文件
  3. 代码中的默认值

使用方式：
    from config import settings
    print(settings.PORT)  # 8000

配置分区：
  - 服务配置：FastAPI 监听地址、端口、标题
  - 本地 CLI Agent 配置：Claude Code / Codex CLI 路径与参数
  - Agent 调用参数：超时、最大 Token 数
  - 安全配置：CORS 允许的前端与 Java 后端地址
  - H2 共享数据库配置：与 Java 后端共享 H2 文件数据库的路径
"""

import os
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """应用全局配置单例，通过 Settings() 实例化后自动加载 .env 文件。"""

    # ========== 服务配置 ==========
    # FastAPI 启动参数，uvicorn 读取 HOST/PORT 决定监听地址
    APP_TITLE: str = "AgentHub Agent Service"       # OpenAPI 文档标题
    APP_VERSION: str = "1.0.0"                      # 服务版本号
    HOST: str = "0.0.0.0"                           # 监听地址（0.0.0.0 表示接受所有来源连接）
    PORT: int = 8000                                 # 监听端口（与 Java 端 agent.service.url 对齐）

    # ========== Claude Code 本地 CLI 配置 ==========
    # Claude Code 是 Anthropic 官方提供的本地 CLI Agent 工具
    # 安装方式：npm install -g @anthropic-ai/claude-code
    # 使用方式：claude -p "你的提示词"（非交互模式，输出到 stdout）
    # 环境要求：需要设置 ANTHROPIC_API_KEY 环境变量
    CLAUDE_CLI_COMMAND: str = "claude"               # Claude Code CLI 命令名或绝对路径
    CLAUDE_CLI_ARGS: List[str] = []                  # 额外的 CLI 参数（如 ["--model", "claude-sonnet-4-20250514"]）

    # ========== Codex 本地 CLI 配置 ==========
    # OpenAI Codex CLI 是 OpenAI 官方提供的本地 CLI Agent 工具
    # 安装方式：npm install -g @openai/codex
    # 使用方式：codex exec "你的提示词"（在执行模式下运行任务）
    # 环境要求：需要设置 OPENAI_API_KEY 环境变量
    CODEX_CLI_COMMAND: str = "codex"                 # Codex CLI 命令名或绝对路径
    CODEX_CLI_ARGS: List[str] = []                   # 额外的 CLI 参数（如 ["--model", "gpt-5"]）

    # ========== Agent 调用参数 ==========
    # 控制 Agent 调用的行为
    AGENT_TIMEOUT: int = 300                          # 单次 Agent 任务超时（秒），CLI 可能执行文件操作等耗时任务
    AGENT_MAX_TOKENS: int = 4096                      # 回复的最大 Token 数
    AGENT_WORKING_DIRECTORY: str = "."                # Agent CLI 执行任务的工作目录，默认当前目录

    # ========== 安全配置 ==========
    # CORS 白名单：仅允许以下来源跨域访问 FastAPI
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",                     # Vue 前端开发服务器
        "http://localhost:8080",                     # Spring Boot Java 后端
    ]

    # ========== H2 共享数据库配置 ==========
    # Python 通过 JPype + jaydebeapi JDBC 桥接访问 Java 端的 H2 文件数据库
    H2_JAR_PATH: str = os.getenv("H2_JAR_PATH", "")                       # H2 JDBC 驱动 jar 文件路径，为空时自动搜索
    H2_DB_PATH: str = os.getenv("H2_DB_PATH", "../shared-data/agenthub")  # H2 数据库文件路径（相对于 agent-service/）

    class Config:
        env_file = ".env"
        extra = "ignore"  # 忽略 .env 中未在当前 Settings 定义的旧字段


# 模块级单例：其他模块通过 `from config import settings` 直接使用
settings = Settings()
