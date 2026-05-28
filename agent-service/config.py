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
  - LLM API 配置：Claude / Codex / DeepSeek 的 Key 和 URL
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

    # ========== Claude API 配置 ==========
    # 调用 Anthropic Claude API 所需的凭证和端点
    CLAUDE_API_KEY: str = os.getenv("CLAUDE_API_KEY", "your-api-key-here")   # 从环境变量读取，避免硬编码
    CLAUDE_API_URL: str = "https://api.anthropic.com/v1/messages"             # Anthropic Messages API 端点
    CLAUDE_MODEL: str = "claude-3-5-sonnet-20241022"                          # 默认模型

    # ========== Codex API 配置 ==========
    # Codex 调用 OpenAI 兼容接口
    CODEX_API_KEY: str = os.getenv("CODEX_API_KEY", "your-api-key-here")      # 从环境变量读取
    CODEX_API_URL: str = "https://api.openai.com/v1/chat/completions"         # OpenAI Chat Completions 端点
    CODEX_MODEL: str = "gpt-4o"                                                # 默认模型

    # ========== DeepSeek API 配置 ==========
    # DeepSeek 使用 OpenAI 兼容接口，API 文档：https://platform.deepseek.com/api-docs
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "your-api-key-here")
    DEEPSEEK_API_URL: str = "https://api.deepseek.com/v1/chat/completions"
    DEEPSEEK_PRO_MODEL: str = "deepseek-v4-pro"      # DeepSeek V4 Pro
    DEEPSEEK_FLASH_MODEL: str = "deepseek-v4-flash"  # DeepSeek V4 Flash

    # ========== Agent 调用参数 ==========
    # 控制 LLM 调用的行为
    AGENT_TIMEOUT: int = 120                         # 单次 LLM 请求超时（秒）
    AGENT_MAX_TOKENS: int = 4096                     # LLM 回复的最大 Token 数

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
        env_file = ".env"                              # 自动加载 agent-service/.env 中的环境变量


# 模块级单例：其他模块通过 `from config import settings` 直接使用
settings = Settings()
