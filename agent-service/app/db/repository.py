"""
AgentHub Agent Service — 数据访问层（Repository）

本模块封装了所有对 H2 共享数据库的操作，提供干净的 Pythonic 接口。
上层 API 端点（agents.py 等）不直接接触 JDBC 连接，而是调用本模块的函数。

数据映射约定：
    - agents 表的 capabilities 字段在数据库中存储为 JSON 数组字符串
      （如 '["代码生成","代码审查"]'），读取时解析为 Python List[str]，
      写入时序列化为 JSON 字符串。这与 Java 端 Agent.java 的存储格式一致。
    - 数据库字段名使用下划线命名（snake_case），Pydantic 模型使用小驼峰（camelCase），
      但 Pydantic 通过 alias 自动转换。

安全说明：
    - 所有 SQL 查询使用参数化查询（? 占位符），防止 SQL 注入。
    - 每个函数自行管理连接的打开与关闭（try-finally 保证关闭）。
"""

import json
from typing import List, Optional
from datetime import datetime
from models import Agent, AgentCreate
from .connection import get_connection


def _parse_capabilities(raw: Optional[str]) -> List[str]:
    """将数据库中存储的 JSON 字符串解析为 Python 列表。

    数据库中 capabilities 字段格式：
        '["代码生成", "代码审查", "Debug"]'  →  ["代码生成", "代码审查", "Debug"]

    Args:
        raw: 数据库原始值（JSON 字符串或 None/空字符串）

    Returns:
        List[str]: 解析后的能力标签列表，解析失败或为空时返回空列表
    """
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return parsed
    except (json.JSONDecodeError, TypeError):
        pass
    return []


def _row_to_agent(row) -> Agent:
    """将 JDBC 查询返回的元组行转换为 Agent Pydantic 模型。

    行字段顺序（与 SQL SELECT 顺序严格对应）：
        row[0] = id            (VARCHAR 36)
        row[1] = name          (VARCHAR 100)
        row[2] = type          (VARCHAR 50)
        row[3] = avatar_url    (VARCHAR 500)
        row[4] = system_prompt (TEXT)
        row[5] = capabilities  (TEXT, JSON 字符串)
        row[6] = created_by    (VARCHAR 36)
        row[7] = created_at    (TIMESTAMP)

    Args:
        row: JDBC 游标 fetchone/fetchall 返回的元组

    Returns:
        Agent: 填充完毕的 Agent 实体对象
    """
    return Agent(
        id=row[0],
        name=row[1] or "",
        type=row[2] or "custom",                # 数据库有 NOT NULL 约束，但做防御性处理
        avatar_url=row[3],
        system_prompt=row[4],
        capabilities=_parse_capabilities(row[5]),   # JSON 字符串 → Python 列表
        created_by=row[6],
        description=None,                            # description 不存储在 DB，API 展示字段
        tools=[],                                    # tools 不存储在 DB，API 展示字段
        created_at=row[7] if row[7] else None,
    )


def get_all_agents() -> List[Agent]:
    """查询所有 Agent，按创建时间升序排列。

    对应 API：GET /api/v1/agents/

    数据库查询：
        SELECT id, name, type, avatar_url, system_prompt, capabilities, created_by, created_at
        FROM agents ORDER BY created_at

    Returns:
        List[Agent]: Agent 实体列表，若无数据则返回空列表
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, type, avatar_url, system_prompt, capabilities, created_by, created_at "
            "FROM agents ORDER BY created_at"
        )
        rows = cursor.fetchall()
        return [_row_to_agent(row) for row in rows]
    finally:
        conn.close()                                # 确保连接在任何情况下都被关闭


def get_agent_by_id(agent_id: str) -> Optional[Agent]:
    """根据 Agent ID 查询单个 Agent。

    对应 API：GET /api/v1/agents/{agent_id}

    数据库查询：
        SELECT ... FROM agents WHERE id = ?

    Args:
        agent_id: Agent 的 UUID 主键（如 agent_claude_001）

    Returns:
        Optional[Agent]: 找到则返回 Agent 对象，未找到返回 None
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # 参数化查询，? 占位符防止 SQL 注入
        cursor.execute(
            "SELECT id, name, type, avatar_url, system_prompt, capabilities, created_by, created_at "
            "FROM agents WHERE id = ?",
            (agent_id,)
        )
        row = cursor.fetchone()
        if row:
            return _row_to_agent(row)
        return None
    finally:
        conn.close()


def create_agent(data: AgentCreate) -> Agent:
    """创建新的自定义 Agent 并写入数据库。

    对应 API：POST /api/v1/agents/

    数据库操作：
        INSERT INTO agents (id, name, type, avatar_url, system_prompt, capabilities, created_by, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)

    Args:
        data: 前端或 Java 后端传来的 Agent 创建请求体

    Returns:
        Agent: 新创建的 Agent 完整实体（含自动生成的 UUID 和时间戳）
    """
    import uuid

    # 生成 UUID 主键（与 Java 端 Agent.java 的 @PrePersist 逻辑一致）
    agent_id = str(uuid.uuid4())
    now = datetime.utcnow()

    # 将 Python 列表序列化为 JSON 字符串存入数据库
    capabilities_json = json.dumps(data.capabilities, ensure_ascii=False)

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO agents (id, name, type, avatar_url, system_prompt, capabilities, created_by, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (agent_id, data.name, data.type or "custom", data.avatar_url,
             data.system_prompt, capabilities_json, None, now)
        )
        conn.commit()                               # 提交事务，确保持久化
    finally:
        conn.close()

    # 返回构造的 Agent 对象（无需再次查询数据库）
    return Agent(
        id=agent_id,
        name=data.name,
        type=data.type or "custom",
        avatar_url=data.avatar_url,
        system_prompt=data.system_prompt,
        capabilities=data.capabilities,
        description=data.description,
        tools=data.tools,
        created_by=None,
        created_at=now,
    )
