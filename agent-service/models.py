"""
AgentHub Agent Service — 数据模型定义

本文件定义了整个 Agent 服务的核心数据结构，使用 Pydantic 进行数据校验与序列化。
所有模型与 Java 后端 H2 数据库的表结构严格对齐，确保跨进程通信时数据一致。

模型分层关系：
    AgentBase  → AgentCreate / Agent         (Agent 的创建请求与完整实体)
    ConversationBase → ConversationCreate / Conversation
    MessageContent (嵌入式) → MessageBase → Message

注意事项：
    - capabilities 字段在数据库中以 JSON 字符串存储（与 Java 端 Agent.java 一致）
    - Pydantic 的 `from_attributes=True` 允许直接从 ORM 对象或字典构造
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Union, Literal
from datetime import datetime


# ============================================================
# Agent 相关模型
# ============================================================

class AgentBase(BaseModel):
    """Agent 基础字段，作为创建请求和响应实体的公共基类。

    与 Java 端 com.agenthub.model.Agent 实体及 H2 数据库 agents 表对齐：
      - name          → agents.name          (VARCHAR 100, NOT NULL)
      - type          → agents.type          (VARCHAR 50, NOT NULL)  如 claude_code / codex / custom
      - avatar_url    → agents.avatar_url    (VARCHAR 500)
      - system_prompt → agents.system_prompt (TEXT)
      - capabilities  → agents.capabilities  (TEXT, JSON 数组字符串)
    """
    name: str                                       # Agent 显示名称
    type: str = "custom"                            # Agent 类型：claude_code / codex / custom
    avatar_url: Optional[str] = None                # 头像 URL 路径
    description: Optional[str] = None               # 简短描述文本（API 展示用，不存入 DB）
    system_prompt: Optional[str] = None             # 系统提示词（自定义 Agent 的核心配置）
    tools: List[str] = []                           # 工具列表（如 web_search, calculator，API 展示用）
    capabilities: List[str] = []                    # 能力标签列表（如 代码生成、代码审查）


class AgentCreate(AgentBase):
    """创建 Agent 的请求体模型，继承 AgentBase 的所有字段。"""
    pass


class Agent(AgentBase):
    """Agent 完整实体模型，在 AgentBase 基础上增加 ID 和时间戳。

    作为 GET/POST 接口的响应体，由 app.db.repository 从 H2 数据库查询行数据构造。
    """
    id: str                                         # UUID 主键，与 agents.id 对齐
    created_by: Optional[str] = None                # 创建者用户 ID（自定义 Agent 时填充）
    created_at: Optional[datetime] = None            # 创建时间

    class Config:
        from_attributes = True                      # 允许从 ORM 对象 / dict 构建


# ============================================================
# Conversation 会话模型
# ============================================================

class ConversationBase(BaseModel):
    """会话基础字段。

    与 Java 端 conversations 表对齐。
    """
    title: str                                      # 会话标题（最大 200 字符）
    type: Literal["direct", "group"]                # 会话类型：direct 单聊 / group 群聊
    participant_ids: List[str]                      # 参与者 ID 列表（用户 ID + Agent ID）


class ConversationCreate(ConversationBase):
    """创建会话的请求体模型。"""
    pass


class Conversation(ConversationBase):
    """会话完整实体模型。"""
    id: str                                         # UUID 主键
    last_message_at: datetime                       # 最后消息时间
    created_at: datetime                            # 创建时间

    class Config:
        from_attributes = True


# ============================================================
# Message 消息模型
# ============================================================

class CodeBlock(BaseModel):
    """代码块结构，嵌入在 MessageContent 中，表示 Agent 生成的代码片段。"""
    language: str                                   # 编程语言（如 javascript, python）
    code: str                                       # 代码内容
    filename: Optional[str] = None                  # 文件名（如 App.jsx）


class DiffBlock(BaseModel):
    """Diff 块结构，嵌入在 MessageContent 中，表示代码修改前后的对比。"""
    original: str                                   # 原始代码
    modified: str                                   # 修改后代码


class MessageContent(BaseModel):
    """消息内容，支持多种类型：
    - text            ：纯文本消息
    - code            ：代码消息（携带 CodeBlock）
    - diff            ：代码 Diff 消息（携带 DiffBlock）
    - artifact_preview：产物预览卡片（携带 artifact_id 关联产物）
    """
    type: Literal["text", "code", "diff", "artifact_preview"]   # 消息内容类型
    text: Optional[str] = None                                  # 文本内容（type=text 时填充）
    code_block: Optional[CodeBlock] = None                      # 代码块（type=code 时填充）
    diff: Optional[DiffBlock] = None                            # Diff 块（type=diff 时填充）
    artifact_id: Optional[str] = None                           # 关联产物 ID（type=artifact_preview 时填充）


class MessageBase(BaseModel):
    """消息基础字段。

    与 Java 端 messages 表对齐。
    """
    conversation_id: str                            # 所属会话 ID
    sender_id: str                                  # 发送者 ID（用户或 Agent）
    sender_type: Literal["user", "agent"]           # 发送者类型
    content: MessageContent                          # 结构化消息内容


class Message(MessageBase):
    """消息完整实体模型。"""
    id: str                                         # UUID 主键
    is_pinned: bool = False                         # 是否被用户置顶
    created_at: datetime                            # 发送时间

    class Config:
        from_attributes = True


# ============================================================
# Chat 请求模型
# ============================================================

class ChatHistoryItem(BaseModel):
    """对话历史中的单条记录。"""
    role: str                                       # user 或 assistant
    content: str                                    # 消息内容


class ChatRequest(BaseModel):
    """发送给 Agent 的聊天请求体。

    POST /api/v1/messages/chat/stream 的请求模型。
    定义此模型后 Swagger UI 会自动生成可编辑的表单。
    """
    message: str                                    # 用户消息文本
    agent_type: str = "deepseek_v4_pro"             # Agent 类型
    system_prompt: str = "请用中文回复"               # 系统提示词
    history: List[ChatHistoryItem] = []              # 对话历史
