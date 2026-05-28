"""
AgentHub Agent Service — Agent 管理 API 端点

本模块提供 Agent 的 CRUD REST 接口，供 Java 后端（Spring Boot）通过 WebClient 调用。

路由前缀：/api/v1/agents（由 main.py 中的 app.include_router 注册）

调用链路：
    Java AgentGatewayService (WebClient)
        │  GET/POST http://localhost:8000/api/v1/agents/...
        ▼
    agents.py（本文件，FastAPI 路由处理器）
        │  参数校验 + 响应序列化
        ▼
    app.db.repository（数据访问层）
        │  JDBC 查询
        ▼
    H2 共享数据库文件（shared-data/agenthub.mv.db）

接口列表：
    GET  /api/v1/agents/          — 获取所有 Agent 列表
    GET  /api/v1/agents/{id}      — 获取单个 Agent 详情
    POST /api/v1/agents/          — 创建自定义 Agent
"""

from fastapi import APIRouter, HTTPException
from typing import List
from models import Agent, AgentCreate
from app.db.repository import get_all_agents, get_agent_by_id, create_agent

# 创建路由模块实例
# 路由前缀 /api/v1/agents 由 main.py 在注册时统一指定
router = APIRouter()


@router.get("/", response_model=List[Agent])
async def list_agents():
    """获取所有可用 Agent 列表。

    调用方：Java 后端 AgentGatewayService.getAgents()
    数据库：查询 H2 共享数据库中 agents 表的所有记录，按 created_at 升序

    响应示例（HTTP 200）：
        [
            {
                "id": "agent_claude_001",
                "name": "Claude Code",
                "type": "claude_code",
                "avatar_url": "/avatars/claude.png",
                "system_prompt": "你是一个经验丰富的软件工程师...",
                "capabilities": ["代码生成", "代码审查", "Debug"]
            },
            {
                "id": "agent_codex_001",
                "name": "Codex",
                "type": "codex",
                "avatar_url": "/avatars/codex.png",
                "system_prompt": "你是一个全栈开发专家...",
                "capabilities": ["代码生成", "全栈开发", "技术问答"]
            }
        ]

    Returns:
        List[Agent]: Agent 实体列表，无数据时返回空列表 []
    """
    return get_all_agents()


@router.get("/{agent_id}", response_model=Agent)
async def get_agent(agent_id: str):
    """根据 Agent ID 获取单个 Agent 详情。

    调用方：Java 后端 AgentGatewayService.getAgentDetail(agentId)
    数据库：参数化查询 WHERE id = ?

    Args:
        agent_id: Agent 的 UUID 主键（路径参数），如 agent_claude_001

    Returns:
        Agent: 完整的 Agent 实体对象

    Raises:
        HTTPException(404): 当指定 ID 的 Agent 不存在时
    """
    agent = get_agent_by_id(agent_id)
    if not agent:
        # 资源不存在时返回 404，符合 RESTful 规范
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    return agent


@router.post("/", response_model=Agent, status_code=201)
async def create_new_agent(data: AgentCreate):
    """创建新的自定义 Agent。

    调用方：Java 后端 AgentGatewayService.createAgent(data)
    数据库：INSERT INTO agents ...

    请求体示例（JSON）：
        {
            "name": "我的前端助手",
            "type": "custom",
            "system_prompt": "你是一个 React 前端专家...",
            "capabilities": ["React 开发", "组件设计"]
        }

    Args:
        data: Agent 创建请求体（Pydantic 自动校验必填字段）

    Returns:
        Agent: 新创建的 Agent 实体（HTTP 201 Created）
              包含自动生成的 UUID 和时间戳
    """
    return create_agent(data)
