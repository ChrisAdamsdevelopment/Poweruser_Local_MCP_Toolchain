import os
import shlex
import subprocess
from pathlib import PureWindowsPath

from config import ALLOWED_SHELLS

_CURRENT_WORKING_DIR = os.getcwd()


def _windows_to_wsl(path: str) -> str:
    if not path:
        return path
    if path.startswith("/"):
        return path
    p = PureWindowsPath(path)
    drive = (p.drive or "").replace(":", "").lower()
    if drive:
        rel = "/".join(p.parts[1:])
        return f"/mnt/{drive}/{rel}"
    return path.replace("\\", "/")


def register_terminal_tools(mcp):
    @mcp.tool(name="terminal_execute", annotations={"readOnlyHint": False, "openWorldHint": True})
    def terminal_execute(command: str, shell: str = "powershell", working_dir: str | None = None) -> dict:
        """Use this when you need to run a shell command in PowerShell/CMD/WSL/Kali and capture output."""
        global _CURRENT_WORKING_DIR
        if shell not in ALLOWED_SHELLS:
            return {
                "exit_code": -1,
                "stdout": "",
                "stderr": f"Unknown shell '{shell}'. Allowed: {', '.join(ALLOWED_SHELLS.keys())}",
                "shell_used": shell,
                "working_directory": working_dir or _CURRENT_WORKING_DIR,
            }

        wd = working_dir or _CURRENT_WORKING_DIR
        shell_cmd = ALLOWED_SHELLS[shell]

        if shell in {"kali", "wsl"}:
            translated = _windows_to_wsl(wd)
            full_cmd = f'{shell_cmd} bash -lc "cd {shlex.quote(translated)} && {command}"'
            run_cwd = None
            wd_return = translated
        else:
            full_cmd = f'{shell_cmd} "{command}"'
            run_cwd = wd
            wd_return = wd

        try:
            result = subprocess.run(
                full_cmd,
                shell=True,
                capture_output=True,
                text=True,
                cwd=run_cwd,
                timeout=120,
            )
            return {
                "exit_code": result.returncode,
                "stdout": (result.stdout or "")[:5000],
                "stderr": (result.stderr or "")[:2000],
                "shell_used": shell,
                "working_directory": wd_return,
            }
        except subprocess.TimeoutExpired:
            return {
                "exit_code": -1,
                "stdout": "",
                "stderr": "Command timed out after 120 seconds",
                "shell_used": shell,
                "working_directory": wd_return,
            }

    @mcp.tool(name="terminal_get_working_dir", annotations={"readOnlyHint": True})
    def terminal_get_working_dir() -> dict:
        """Use this when you need the current default working directory for terminal commands."""
        return {"working_directory": _CURRENT_WORKING_DIR}

    @mcp.tool(name="terminal_set_working_dir", annotations={"readOnlyHint": False})
    def terminal_set_working_dir(path: str) -> dict:
        """Use this when you need to change the default working directory for terminal commands."""
        global _CURRENT_WORKING_DIR
        if not os.path.isdir(path):
            return {"ok": False, "error": f"Directory does not exist: {path}"}
        _CURRENT_WORKING_DIR = os.path.abspath(path)
        return {"ok": True, "working_directory": _CURRENT_WORKING_DIR}
