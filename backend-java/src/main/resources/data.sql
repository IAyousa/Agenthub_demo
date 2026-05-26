MERGE INTO agents (id, name, type, avatar_url, system_prompt, capabilities, created_at)
KEY (id)
VALUES
(
    'agent_claude_001',
    'Claude Code',
    'claude_code',
    '/avatars/claude.png',
    '你是一个经验丰富的软件工程师，擅长前端开发、代码审查和问题调试。请用中文回复。',
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
    '你是一个全栈开发专家，擅长快速生成高质量代码，并能解释技术原理。',
    '["代码生成", "全栈开发", "技术问答", "代码优化"]',
    CURRENT_TIMESTAMP
);
