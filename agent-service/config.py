import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # ========== 服务配置 ==========
    APP_TITLE: str = "AgentHub Agent Service"
    APP_VERSION: str = "1.0.0"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # ========== Claude API 配置 ==========
    CLAUDE_API_KEY: str = os.getenv("CLAUDE_API_KEY", "your-api-key-here")
    CLAUDE_API_URL: str = "https://api.anthropic.com/v1/messages"
    CLAUDE_MODEL: str = "claude-3-5-sonnet-20241022"

    # ========== Codex API 配置 ==========
    CODEX_API_KEY: str = os.getenv("CODEX_API_KEY", "your-api-key-here")
    CODEX_API_URL: str = "https://api.openai.com/v1/chat/completions"
    CODEX_MODEL: str = "gpt-4o"

    # ========== Agent 调用参数 ==========
    AGENT_TIMEOUT: int = 120               # 超时（秒）
    AGENT_MAX_TOKENS: int = 4096           # 最大输出 token 数

    # ========== 安全配置 ==========
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",      # Vue 开发服务器
        "http://localhost:8080",      # Spring Boot
    ]

    class Config:
        env_file = ".env"

settings = Settings()
