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
  - Agent 调用参数：超时、工作目录
  - 安全配置：CORS 允许的前端与 Java 后端地址
"""

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
    AGENT_WORKING_DIRECTORY: str = "."                # Agent CLI 执行任务的默认工作目录（fallback，不传 workingDirectory 时使用）
    AGENT_WORKSPACE_ROOT: str = "./agent_workspaces" # Agent 独立工作区根目录，每个会话一个子目录，与项目源码隔离

    # ========== Agent 注册表（Fallback 缓存） ==========
    # 这是 Python 端的 Agent 元数据缓存，用于以下场景：
    #   1. Java 未传 availableAgents 时的降级 fallback
    #   2. 本地开发时无需启动 Java 后端即可测试 Agent 服务
    #   3. 系统内置 Agent 的默认角色定义（promptKey → SYSTEM_PROMPTS）
    #
    # Java DB 的 agents 表是 Agent 元数据的唯一权威数据源。
    # 当 Java 通过 availableAgents[] 传入 Agent 列表时，以 Java 传入的为准。
    AGENT_REGISTRY: list = [
        {
            "id": "claude_code",
            "name": "Claude Code",
            "type": "claude_code",
            "description": "全栈工程师，擅长后端逻辑、代码审查、架构设计与重构优化",
            "promptKey": "claude_code",
            "capabilities": [
                "代码生成",
                "代码审查与 Bug 修复",
                "架构设计与技术选型",
                "重构与性能优化",
                "文件系统读写与 Shell 命令执行",
            ],
            "tags": ["全栈", "代码审查"],
            "status": "active",
        },
        {
            "id": "codex",
            "name": "Codex",
            "type": "codex",
            "description": "前端开发专家，擅长组件开发、UI 实现与前端交互逻辑",
            "promptKey": "codex",
            "capabilities": [
                "前端组件开发",
                "样式实现与响应式布局",
                "前端交互逻辑与状态管理",
                "文件系统读写与 Shell 命令执行",
            ],
            "tags": ["前端", "UI"],
            "status": "active",
        },
        {
            "id": "orchestrator",
            "name": "Orchestrator",
            "type": "custom",
            "description": "任务调度器，分析用户意图，将任务分派给最合适的 Agent",
            "promptKey": "orchestrator",
            "capabilities": [
                "用户意图分析与任务分类",
                "多 Agent 协作调度",
                "任务拆分与串行执行规划",
                "模糊需求澄清",
            ],
            "tags": ["调度", "多 Agent"],
            "status": "active",
        },
        {
            "id": "custom",
            "name": "Custom Agent",
            "type": "custom",
            "description": "用户自定义 Agent，默认使用 Claude Code 作为执行引擎",
            "promptKey": "custom",
            "capabilities": [
                "通用任务处理",
                "文件系统读写与 Shell 命令执行",
            ],
            "tags": ["通用", "自定义"],
            "status": "active",
        },
    ]

    # ========== 安全配置 ==========
    # CORS 白名单：仅允许以下来源跨域访问 FastAPI
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",                     # Vue 前端开发服务器
        "http://localhost:8080",                     # Spring Boot Java 后端
    ]

    class Config:
        env_file = ".env"
        extra = "ignore"  # 忽略 .env 中未在当前 Settings 定义的旧字段


# 模块级单例：其他模块通过 `from config import settings` 直接使用
settings = Settings()
