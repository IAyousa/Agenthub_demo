"""
AgentHub Agent Service — 产物检测与上传

在 Agent 流式回复结束后，检测输出中的 Markdown 代码块，
提取文件内容，批量上传到 Java 后端的 /internal/artifacts/batch 端点。

流程：
    messages.py (msg_end 后)
        → detect_code_blocks(full_response)
        → upload_blocks_batch(blocks)
        → Java POST /internal/artifacts/batch
        → Java 存文件 + WebSocket push project_bundle 到前端
"""

from __future__ import annotations

import os
import re
from pathlib import Path

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


def _ext(filename: str) -> str:
    """提取文件扩展名（小写，含点号）。"""
    return Path(filename).suffix.lower()


_CODE_BLOCK_RE = re.compile(r"```(\w*)\n(.*?)```", re.DOTALL)

# 文件名推断正则：从代码块前的文本中匹配文件名
# 模式覆盖:
#   **filename.ext** / `filename.ext`
#   ### filename.ext（Markdown 标题）
#   创建/新建/写入 filename.ext（中文语境）
#   文件 filename.ext / File: filename.ext
_FILENAME_HINT_RE = re.compile(
    r"(?:\*\*|`|###\s+|(?:(?:创建|新建|写入|文件|File|文件路径|保存为)[:：]?\s*))"
    r"([a-zA-Z0-9_\-./]+\.(?:html?|css|jsx?|tsx?|py|java|json|xml|ya?ml|md|sql|sh|go|rs|txt))",
    re.IGNORECASE,
)

def _java_batch_url() -> str:
    """Java 批量上传端点 URL，从全局配置读取后端地址。"""
    from config import settings
    return f"{settings.BACKEND_URL}/internal/artifacts/batch"


_PREVIEW_LOOKBACK_CHARS = 300  # 在代码块前查找文件名提示的字符数


def _infer_filename(text_before_block: str, ext: str, index: int) -> str:
    """从代码块前的文本中推断真实文件名，失败则回退到 artifact_NNN.ext。

    Args:
        text_before_block: 代码块前的文本（最多 _PREVIEW_LOOKBACK_CHARS 字符）
        ext: 文件扩展名（含点号，如 ".html"）
        index: 代码块序号（用于 fallback）

    Returns:
        推断的文件名
    """
    if not text_before_block:
        return f"artifact_{index + 1:03d}{ext}"
    # 在代码块前的文本中搜索文件名提示
    for match in _FILENAME_HINT_RE.finditer(text_before_block):
        filename = match.group(1).strip()
        f_ext = _ext(filename)
        # 扩展名匹配或同为文本类文件
        if f_ext == ext or (
            f_ext in (".txt",) and ext in (".txt", ".md", ".json", ".xml")
        ):
            return filename
    return f"artifact_{index + 1:03d}{ext}"


def detect_code_blocks(text: str) -> list[dict]:
    """从文本中检测所有 Markdown 代码块，并尝试推断真实文件名。

    Args:
        text: Agent 完整回复文本

    Returns:
        [{"language": "html", "content": "...", "ext": ".html",
          "content_type": "text/html", "filename": "index.html"}, ...]
    """
    blocks = []
    seen = set()

    for idx, match in enumerate(_CODE_BLOCK_RE.finditer(text)):
        lang = match.group(1).strip().lower() if match.group(1) else ""
        content = match.group(2).strip()

        if not content:
            continue
        content_hash = hash(content)
        if content_hash in seen:
            continue
        seen.add(content_hash)

        ext, content_type = _LANGUAGE_MAP.get(lang, (".txt", "text/plain"))

        # 从代码块前的文本中推断真实文件名
        lookback_start = max(0, match.start() - _PREVIEW_LOOKBACK_CHARS)
        text_before = text[lookback_start:match.start()]
        filename = _infer_filename(text_before, ext, idx)

        blocks.append({
            "language": lang or "plaintext",
            "content": content,
            "ext": ext,
            "content_type": content_type,
            "filename": filename,
        })

    return blocks


async def write_blocks_to_workspace(
    blocks: list[dict], workspace_path: str,
) -> list[str]:
    """将检测到的代码块写入工作目录磁盘。

    写入前检查：若同名文件已存在则跳过（保护 Agent 通过 Write 工具创建的文件）。

    Args:
        blocks: detect_code_blocks() 返回的代码块列表
        workspace_path: 工作目录绝对路径

    Returns:
        成功写入的文件相对路径列表
    """
    written = []
    if not workspace_path or not os.path.isdir(workspace_path):
        return written

    for block in blocks:
        filename = block.get("filename", "")
        if not filename:
            continue
        filepath = os.path.join(workspace_path, filename)
        # 若文件已存在则跳过（保护 Agent 实际写入的文件）
        if os.path.exists(filepath):
            continue
        try:
            os.makedirs(os.path.dirname(filepath) or workspace_path, exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(block["content"])
            rel = os.path.relpath(filepath, workspace_path).replace("\\", "/")
            written.append(rel)
            print(f"[artifact_uploader] Wrote block to workspace: {rel}", flush=True)
        except (IOError, OSError) as e:
            print(f"[artifact_uploader] Failed to write {filename}: {e}", flush=True)

    return written


async def detect_and_upload(
    full_response: str,
    conversation_id: str,
    message_id: str,
) -> list[dict]:
    """检测代码块并批量上传到 Java 后端。

    这是外部调用的主入口。从 Agent 完整回复中检测所有 Markdown 代码块，
    通过 /internal/artifacts/batch 批量上传，Java 侧推一条 project_bundle
    WebSocket 消息（而非每个文件一条 preview_card）。

    Args:
        full_response: Agent 完整回复文本
        conversation_id: 会话 ID
        message_id: 消息 ID

    Returns:
        上传成功的 artifact 列表
    """
    if not conversation_id:
        return []

    blocks = detect_code_blocks(full_response)
    if not blocks:
        return []

    # 组装批量请求 — 使用推断出的真实文件名
    batch_payload = []
    for block in blocks:
        batch_payload.append({
            "conversationId": conversation_id,
            "messageId": message_id,
            "filename": block["filename"],
            "content": block["content"],
            "contentType": block["content_type"],
        })

    if not batch_payload:
        return []

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(_java_batch_url(), json=batch_payload)
        if resp.status_code in (200, 201):
            result = resp.json()
            if isinstance(result, dict):
                files = result.get("files", [])
                filenames = [f.get("filename", "?") for f in files]
                print(f"[artifact_uploader] Batch uploaded {len(files)}/{len(batch_payload)} files → project_bundle: {filenames}",
                      flush=True)
                return files
            return result if isinstance(result, list) else []
        else:
            print(f"[artifact_uploader] Batch upload failed: HTTP {resp.status_code}", flush=True)
            return []
    except Exception as e:
        print(f"[artifact_uploader] Batch upload error: {e}", flush=True)
        return []
