import json
import subprocess
import time


def register_apps_tools(mcp):
    @mcp.tool(name="app_open", annotations={"readOnlyHint": False, "openWorldHint": True})
    def app_open(app_name: str) -> dict:
        """Use this when you need to launch a Windows application by name."""
        subprocess.Popen(["start", app_name], shell=True)
        time.sleep(1)
        return {"ok": True, "app_name": app_name}

    @mcp.tool(name="app_focus", annotations={"readOnlyHint": False})
    def app_focus(window_title: str) -> dict:
        """Use this when you need to focus a window by partial title match."""
        script = rf"""
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class W {{
 [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
}}
"@
$p = Get-Process | Where-Object {{$_.MainWindowTitle -like "*{window_title}*"}} | Select-Object -First 1
if ($p) {{ [W]::SetForegroundWindow($p.MainWindowHandle) | Out-Null; Write-Output "true" }} else {{ Write-Output "false" }}
"""
        result = subprocess.run(["powershell", "-NoProfile", "-Command", script], capture_output=True, text=True)
        return {"focused": result.stdout.strip().lower() == "true", "window_title": window_title}

    @mcp.tool(name="app_list_windows", annotations={"readOnlyHint": True})
    def app_list_windows() -> dict:
        """Use this when you need a list of current top-level windows from running processes."""
        cmd = "Get-Process | Where-Object {$_.MainWindowTitle} | Select-Object ProcessName,Id,MainWindowTitle | ConvertTo-Json -Depth 3"
        result = subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True, text=True)
        try:
            parsed = json.loads(result.stdout) if result.stdout.strip() else []
        except json.JSONDecodeError:
            parsed = []
        return {"windows": parsed}

    @mcp.tool(name="app_close", annotations={"readOnlyHint": False, "destructiveHint": True})
    def app_close(process_name: str) -> dict:
        """Use this when you need to force-close a Windows process by name."""
        exe = process_name if process_name.lower().endswith(".exe") else f"{process_name}.exe"
        result = subprocess.run(["taskkill", "/IM", exe, "/F"], capture_output=True, text=True)
        return {"ok": result.returncode == 0, "stdout": result.stdout, "stderr": result.stderr}
