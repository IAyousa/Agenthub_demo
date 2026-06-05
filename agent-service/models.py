"""
AgentHub Agent Service — 数据模型定义

本文件定义 Agent 服务的内部请求/响应数据结构，使用 Pydantic 进行校验与序列化。
所有模型均对齐 API 契约文档第 4 节规范。
"""

from typing import Optional
from pydantic import BaseModel, Field


class AgentChatRequest(BaseModel):
    """Spring Boot → FastAPI 内部 Agent 调用请求。

    POST /api/agent/chat 的请求模型，严格对齐 API 契约文档第 4.2 节。
    字段使用 camelCase 命名，与 Java 后端 AgentGatewayService 序列化格式一致。
    """
    agentType: str = Field(
        default="claude_code",
        description="Agent 类型，可选值：claude_code / codex / custom",
        examples=["claude_code"],
    )
    systemPrompt: str = Field(
        default="",
        description="系统提示词，覆盖 Agent 数据库中的默认 system_prompt",
        examples=["你是一个前端开发专家，擅长 React。"],
    )
    context: str = Field(
        default="",
        description="格式化后的聊天历史上下文，由 Java 后端组装",
        examples=["用户：帮我写一个 React 组件\n"],
    )
    stream: bool = Field(
        default=False,
        description="是否流式返回。false=收集完整后返回 JSON（Swagger 直接可见），true=SSE 逐 token 推送（Java 后端调用时使用）",
    )
    workingDirectory: Optional[str] = Field(
        default=None,
        description="本地 CLI Agent 执行任务的工作目录。仅在 claude_code / codex 类型下有效，不传则使用默认工作目录",
        examples=["/path/to/project"],
    )
    availableAgents: list = Field(
        default_factory=list,
        description="P2预留：Java传入的可用Agent列表，用于Orchestrator做调度决策。"
                    "MVP阶段为空列表，Python使用config.py的AGENT_REGISTRY作为fallback。"
                    "P1阶段由Java从DB查询后通过此字段传入，P1末期迁至Redis共享缓存。",
    )


class AgentChatResponse(BaseModel):
    """非流式（stream=false）对话响应，对齐 API 契约文档第 4.2 节。"""
    content: str = Field(
        description="Agent 生成的完整回复内容",
    )
    messageId: str = Field(
        description="消息唯一标识符",
    )


class HealthResponse(BaseModel):
    """健康检查响应，对齐 API 契约文档第 4.3 节。"""
    status: str = Field(
        description="服务状态，正常返回 'ok'",
        examples=["ok"],
    )
    version: str = Field(
        description="Agent 服务版本号",
    )
    uptime: int = Field(
        description="服务运行时长（秒）",
        examples=[3600],
    )


class ErrorResponse(BaseModel):
    """统一错误响应，对齐 API 契约文档第 5.1 节。"""
    error: str = Field(
        description="错误码：VALIDATION_ERROR / NOT_FOUND / INTERNAL_ERROR / AGENT_ERROR / AGENT_TIMEOUT",
        examples=["VALIDATION_ERROR"],
    )
    message: str = Field(
        description="人类可读的错误描述",
        examples=["context 字段不能为空"],
    )
    timestamp: str = Field(
        description="错误发生的 UTC 时间戳",
        examples=["2026-05-25T10:30:00"],
    )
    path: str = Field(
        description="触发错误的请求路径",
        examples=["/api/agent/chat"],
    )
