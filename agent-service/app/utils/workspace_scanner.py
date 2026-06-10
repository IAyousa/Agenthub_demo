"""
AgentHub Agent Service — 工作区文件扫描器

Agent 任务完成后扫描工作目录变更文件，将所有生成的文件上传到 Java 后端。

流程：
    messages.py (msg_end 后)
        → snapshot_workspace(workspace_path)
        → diff_snapshots(prev, current) — 增量检测
        → upload_files_batch(每个新增/修改文件) × N
        → 保存本轮快照
        → 汇总推送给 Java /internal/artifacts/batch
"""

import os
import hashlib
from pathlib import Path
from typing import Dict, List, Optional

import httpx

from config import settings

# 默认忽略目录
_DEFAULT_IGNORE = {
    ".claude", ".codex", ".git", "node_modules",
    "__pycache__", ".venv", "venv", "dist", "build", ".DS_Store", ".turbo",
}

# 二进制扩展名（跳过）
_BINARY_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".webp",
    ".woff", ".woff2", ".ttf", ".eot", ".otf",
    ".pdf", ".zip", ".tar", ".gz", ".rar", ".7z",
}

# 扩展名 → MIME
_LANGUAGE_MAP = {
    "html": "text/html", "htm": "text/html", "css": "text/css",
    "js": "application/javascript", "ts": "text/typescript",
    "tsx": "text/typescript", "jsx": "text/javascript",
    "py": "text/x-python", "java": "text/x-java",
    "json": "application/json", "xml": "application/xml",
    "yaml": "text/yaml", "yml": "text/yaml",
    "md": "text/markdown", "sql": "text/x-sql",
    "sh": "text/x-sh", "go": "text/x-go", "rs": "text/x-rust",
}

# 全局快照存储
_workspace_snapshots: Dict[str, Dict[str, str]] = {}
def _java_batch_url() -> str:
    """Java 批量上传端点 URL，从全局配置读取后端地址。"""
    from config import settings
    return f"{settings.BACKEND_URL}/internal/artifacts/batch"


def _ext(filename: str) -> str:
    return Path(filename).suffix.lower()


def _mime_type(filename: str) -> str:
    lang = _ext(filename).lstrip(".")
    return _LANGUAGE_MAP.get(lang, "text/plain")


def snapshot_workspace(root: str) -> Dict[str, str]:
    """扫描工作目录，返回 文件路径 → SHA256 哈希。"""
    result: Dict[str, str] = {}
    if not root or not os.path.isdir(root):
        return result

    ignore = _DEFAULT_IGNORE
    cfg_ignore = getattr(settings, "AGENT_WORKSPACE_IGNORE", None)
    if cfg_ignore:
        ignore = ignore | set(cfg_ignore)

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in ignore]
        for filename in filenames:
            if _ext(filename) in _BINARY_EXTENSIONS:
                continue
            filepath = os.path.join(dirpath, filename)
            try:
                if os.path.getsize(filepath) > 500 * 1024:
                    continue
                with open(filepath, "rb") as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()
            except (IOError, PermissionError, OSError):
                continue
            relpath = os.path.relpath(filepath, root).replace("\\", "/")
            result[relpath] = file_hash
    return result


def diff_snapshots(prev: Dict[str, str], current: Dict[str, str]) -> List[str]:
    """对比两轮快照，返回新增/修改的文件列表。"""
    changed = []
    for path, cur_hash in current.items():
        if path not in prev or prev[path] != cur_hash:
            changed.append(path)
    return changed


async def upload_files_batch(
    conversation_id: str, message_id: str,
    files: List[str], workspace_root: str,
) -> List[dict]:
    """批量上传工作目录中的文件到 Java 后端。"""
    if not files or not conversation_id:
        return []

    batch_payload = []
    for relpath in files:
        fullpath = os.path.join(workspace_root, relpath)
        if not os.path.isfile(fullpath):
            continue
        try:
            with open(fullpath, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except (IOError, PermissionError, OSError):
            continue
        if not content.strip():
            continue
        batch_payload.append({
            "conversationId": conversation_id,
            "messageId": message_id,
            "filename": relpath,
            "content": content,
            "contentType": _mime_type(relpath),
        })

    if not batch_payload:
        return []

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(_java_batch_url(), json=batch_payload)
        if resp.status_code in (200, 201):
            result = resp.json()
            # Java 返回 {"files": [...], "total": N}，提取 files 数组
            if isinstance(result, dict):
                files_list = result.get("files", [])
                print(f"[workspace_scanner] Uploaded {len(files_list)}/{len(batch_payload)} files", flush=True)
                return files_list
            return result if isinstance(result, list) else []
        else:
            print(f"[workspace_scanner] Upload failed: HTTP {resp.status_code}", flush=True)
            return []
    except Exception as e:
        print(f"[workspace_scanner] Upload error: {e}", flush=True)
        return []


async def scan_and_upload(
    conversation_id: str, message_id: str, workspace_path: str,
) -> list:
    """扫描工作目录，对比快照，增量上传变更文件。返回上传成功的文件列表。"""
    print(f"[workspace_scanner] scan_and_upload called: conv={conversation_id}, "
          f"msg={message_id}, path={workspace_path}", flush=True)
    if not conversation_id or not message_id or not workspace_path:
        print(f"[workspace_scanner] Abort: missing required param", flush=True)
        return []
    if not os.path.isdir(workspace_path):
        print(f"[workspace_scanner] Abort: workspace path not found: {workspace_path}", flush=True)
        return []

    prev = _workspace_snapshots.get(conversation_id, {})
    current = snapshot_workspace(workspace_path)
    print(f"[workspace_scanner] Snapshot: {len(prev)} prev files, {len(current)} current files", flush=True)
    changed = diff_snapshots(prev, current)
    print(f"[workspace_scanner] Changed files: {len(changed)} -> {changed[:10]}", flush=True)

    all_uploaded = []
    if changed:
        max_per_batch = 50
        for i in range(0, len(changed), max_per_batch):
            batch = changed[i:i + max_per_batch]
            result = await upload_files_batch(conversation_id, message_id, batch, workspace_path)
            print(f"[workspace_scanner] Batch upload result: {result}", flush=True)
            if result:
                all_uploaded.extend(result)

    _workspace_snapshots[conversation_id] = current
    return all_uploaded
