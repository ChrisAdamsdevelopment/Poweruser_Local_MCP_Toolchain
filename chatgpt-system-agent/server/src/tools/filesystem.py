import fnmatch
import os
import shutil
from pathlib import Path, PureWindowsPath

from config import ALLOWED_ROOTS


def _normalize(path: str) -> str:
    if path.startswith("\\\\wsl$"):
        return os.path.normpath(path).lower()
    if ":" in path or path.startswith("\\\\"):
        return os.path.normpath(path).lower()
    return os.path.abspath(path)


def _is_allowed(path: str) -> bool:
    target = _normalize(path)
    for root in ALLOWED_ROOTS:
        root_norm = _normalize(root)
        if target == root_norm or target.startswith(root_norm.rstrip("\\/") + os.sep) or target.startswith(root_norm.rstrip("\\/") + "/"):
            return True
    return False


def _ensure_allowed(path: str):
    if not _is_allowed(path):
        raise PermissionError(f"Path is outside ALLOWED_ROOTS: {path}")


def register_filesystem_tools(mcp):
    @mcp.tool(name="file_read", annotations={"readOnlyHint": True})
    def file_read(path: str, lines: int | None = None) -> dict:
        """Use this when you need to read file contents from an allowed path."""
        _ensure_allowed(path)
        with open(path, "r", encoding="utf-8") as f:
            if lines is None:
                content = f.read()
            else:
                content = "".join(f.readlines()[:lines])
        return {"path": path, "content": content}

    @mcp.tool(name="file_write", annotations={"readOnlyHint": False, "destructiveHint": True})
    def file_write(path: str, content: str) -> dict:
        """Use this when you need to create or overwrite a file in an allowed path."""
        _ensure_allowed(path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return {"ok": True, "path": path, "bytes_written": len(content.encode("utf-8"))}

    @mcp.tool(name="file_delete", annotations={"readOnlyHint": False, "destructiveHint": True})
    def file_delete(path: str) -> dict:
        """Use this when you need to delete a file or directory from an allowed path."""
        _ensure_allowed(path)
        if os.path.isdir(path):
            shutil.rmtree(path)
        elif os.path.exists(path):
            os.remove(path)
        return {"ok": True, "path": path}

    @mcp.tool(name="file_list", annotations={"readOnlyHint": True})
    def file_list(path: str) -> dict:
        """Use this when you need to list files and folders under an allowed directory."""
        _ensure_allowed(path)
        entries = []
        for name in os.listdir(path):
            p = os.path.join(path, name)
            entries.append({"name": name, "is_dir": os.path.isdir(p), "size": os.path.getsize(p) if os.path.isfile(p) else None})
        return {"path": path, "entries": entries}

    @mcp.tool(name="file_search", annotations={"readOnlyHint": True})
    def file_search(directory: str, pattern: str) -> dict:
        """Use this when you need to search for files by glob pattern in an allowed directory."""
        _ensure_allowed(directory)
        results = []
        for root, _, files in os.walk(directory):
            for file in files:
                if fnmatch.fnmatch(file, pattern):
                    full = os.path.join(root, file)
                    if _is_allowed(full):
                        results.append(full)
                        if len(results) >= 100:
                            return {"directory": directory, "pattern": pattern, "results": results, "truncated": True}
        return {"directory": directory, "pattern": pattern, "results": results, "truncated": False}

    @mcp.tool(name="file_move", annotations={"readOnlyHint": False, "destructiveHint": True})
    def file_move(source: str, destination: str) -> dict:
        """Use this when you need to move or rename a file/directory between allowed paths."""
        _ensure_allowed(source)
        _ensure_allowed(destination)
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        shutil.move(source, destination)
        return {"ok": True, "source": source, "destination": destination}

    @mcp.tool(name="file_mkdir", annotations={"readOnlyHint": False})
    def file_mkdir(path: str) -> dict:
        """Use this when you need to create a directory tree in an allowed path."""
        _ensure_allowed(path)
        os.makedirs(path, exist_ok=True)
        return {"ok": True, "path": path}
