"""
AgentHub Agent Service — 产物检测与上传

在 Agent 流式回复结束后，检测输出中的 Markdown 代码块，
提取文件内容，上传到 Java 后端的 /internal/artifacts 端点。

流程：
    messages.py (SSE 结束后)
        → detect_code_blocks(full_response)
        → upload_artifact(block) × N
        → Java POST /internal/artifacts
        → Java 存文件 + WebSocket push preview_card 到前端
"""

import re
import httpx

# ==========================================================================
# 语言 → 文件扩展名 + MIME 类型映射
# ==========================================================================
_LANGUAGE_MAP = {
    "html":       (".html", "text/html"),
    "htm":        (".html", "text/html"),
    "css":        (".css",  "text/css"),
    "javascript": (".js",   "application/javascript"),
    "js":         (".js",   "application/javascript"),
    "typescript": (".ts",   "text/typescript"),
    "ts":         (".ts",   "text/typescript"),
    "python":     (".py",   "text/x-python"),
    "py":         (".py",   "text/x-python"),
    "java":       (".java", "text/x-java"),
    "json":       (".json", "application/json"),
    "xml":        (".xml",  "application/xml"),
    "yaml":       (".yaml", "text/yaml"),
    "yml":        (".yml",  "text/yaml"),
    "markdown":   (".md",   "text/markdown"),
    "md":         (".md",   "text/markdown"),
    "sql":        (".sql",  "text/x-sql"),
    "shell":      (".sh",   "text/x-sh"),
    "bash":       (".sh",   "text/x-sh"),
    "sh":         (".sh",   "text/x-sh"),
}

_CODE_BLOCK_RE = re.compile(r"```(\w*)\n(.*?)```", re.DOTALL)

_JAVA_ARTIFACT_URL = "http://localhost:8080/internal/artifacts"


def detect_code_blocks(text: str) -> list[dict]:
    """从文本中检测所有 Markdown 代码块。

    Args:
        text: Agent 完整回复文本

    Returns:
        [{"language": "html", "content": "<h1>Hello</h1>", "ext": ".html", "content_type": "text/html"}, ...]
    """
    blocks = []
    seen = set()  # 去重：相同内容的代码块只保留一份

    for match in _CODE_BLOCK_RE.finditer(text):
        lang = match.group(1).strip().lower() if match.group(1) else ""
        content = match.group(2).strip()

        if not content:
            continue
        content_hash = hash(content)
        if content_hash in seen:
            continue
        seen.add(content_hash)

        ext, content_type = _LANGUAGE_MAP.get(lang, (".txt", "text/plain"))
        blocks.append({
            "language": lang or "plaintext",
            "content": content,
            "ext": ext,
            "content_type": content_type,
        })

    return blocks


async def upload_artifact(
    conversation_id: str,
    message_id: str,
    filename: str,
    content: str,
    content_type: str,
) -> dict | None:
    """上传单个产物到 Java 后端。

    Args:
        conversation_id: 会话 ID
        message_id: 消息 ID
        filename: 文件名（如 "index.html"）
        content: 文件文本内容
        content_type: MIME 类型（如 "text/html"）

    Returns:
        成功返回 {"id": "...", "filename": "..."}，失败返回 None
    """
    payload = {
        "conversationId": conversation_id,
        "messageId": message_id,
        "filename": filename,
        "content": content,
        "contentType": content_type,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(_JAVA_ARTIFACT_URL, json=payload)
        if resp.status_code in (200, 201):
            return resp.json()
        else:
            print(f"[artifact_uploader] Upload failed: HTTP {resp.status_code} {resp.text[:200]}",
                  flush=True)
            return None
    except Exception as e:
        print(f"[artifact_uploader] Upload error: {e}", flush=True)
        return None


async def detect_and_upload(
    full_response: str,
    conversation_id: str,
    message_id: str,
) -> list[dict]:
    """检测代码块并上传到 Java 后端。

    这是外部调用的主入口。从 Agent 完整回复中检测所有 Markdown 代码块，
    逐个上传到 Java 的 /internal/artifacts 端点。

    Args:
        full_response: Agent 完整回复文本
        conversation_id: 会话 ID
        message_id: 消息 ID（Java 保存 assistant 消息后返回的 ID）

    Returns:
        上传成功的 artifact 列表
    """
    if not conversation_id:
        return []

    blocks = detect_code_blocks(full_response)
    if not blocks:
        return []

    results = []
    for i, block in enumerate(blocks):
        # 按序号命名：artifact_001.html, artifact_002.css, ...
        filename = f"artifact_{i + 1:03d}{block['ext']}"
        result = await upload_artifact(
            conversation_id=conversation_id,
            message_id=message_id,
            filename=filename,
            content=block["content"],
            content_type=block["content_type"],
        )
        if result:
            results.append(result)

    return results
