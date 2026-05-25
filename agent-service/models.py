from pydantic import BaseModel, Field
from typing import List, Optional, Union, Literal
from datetime import datetime

class AgentBase(BaseModel):
    name: str
    avatar: str
    description: str
    system_prompt: str
    tools: List[str] = []
    capabilities: List[str] = []

class AgentCreate(AgentBase):
    pass

class Agent(AgentBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True

class ConversationBase(BaseModel):
    title: str
    type: Literal["direct", "group"]
    participant_ids: List[str]

class ConversationCreate(ConversationBase):
    pass

class Conversation(ConversationBase):
    id: str
    last_message_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True

class CodeBlock(BaseModel):
    language: str
    code: str
    filename: Optional[str] = None

class DiffBlock(BaseModel):
    original: str
    modified: str

class MessageContent(BaseModel):
    type: Literal["text", "code", "diff", "artifact_preview"]
    text: Optional[str] = None
    code_block: Optional[CodeBlock] = None
    diff: Optional[DiffBlock] = None
    artifact_id: Optional[str] = None

class MessageBase(BaseModel):
    conversation_id: str
    sender_id: str
    sender_type: Literal["user", "agent"]
    content: MessageContent

class Message(MessageBase):
    id: str
    is_pinned: bool = False
    created_at: datetime

    class Config:
        from_attributes = True
