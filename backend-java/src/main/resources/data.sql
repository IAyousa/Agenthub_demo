MERGE INTO agents (id, name, type, avatar_url, system_prompt, capabilities, created_at)
KEY (id)
VALUES
(
    'agent_claude_001',
    'Claude Code',
    'claude_code',
    '/avatars/claude.png',
    '',  -- 内置 Agent 使用 Python 端 SYSTEM_PROMPTS 模板，DB 不存储重复内容
    '["代码生成", "代码审查", "Debug", "重构建议", "文档编写"]',
    CURRENT_TIMESTAMP
);

MERGE INTO agents (id, name, type, avatar_url, system_prompt, capabilities, created_at)
KEY (id)
VALUES
(
    'agent_codex_001',
    'Codex',
    'codex',
    '/avatars/codex.png',
    '',  -- 内置 Agent 使用 Python 端 SYSTEM_PROMPTS 模板
    '["代码生成", "全栈开发", "技术问答", "代码优化"]',
    CURRENT_TIMESTAMP
);
