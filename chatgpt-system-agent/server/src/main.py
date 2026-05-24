import asyncio
import json
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from fastmcp import FastMCP

from config import DASHBOARD_PORT, KALI_DISTRO, NGROK_DOMAIN
from tools.apps import register_apps_tools
from tools.browser import get_browser_screenshot_bytes, register_browser_tools
from tools.filesystem import register_filesystem_tools
from tools.opendesk_alt import register_opendesk_alt_tools
from tools.screen import get_desktop_screenshot_bytes, register_screen_tools
from tools.terminal import register_terminal_tools

mcp = FastMCP("System Agent")
register_browser_tools(mcp)
register_screen_tools(mcp)
register_terminal_tools(mcp)
register_filesystem_tools(mcp)
register_apps_tools(mcp)
register_opendesk_alt_tools(mcp)

TOOL_GROUPS = {
    "browser": ["browser_navigate", "browser_screenshot", "browser_click", "browser_type", "browser_get_content", "browser_execute_js", "browser_press_key", "browser_close"],
    "screen": ["screen_capture", "mouse_position", "mouse_move", "mouse_click", "mouse_double_click", "keyboard_type", "keyboard_press", "scroll"],
    "terminal": ["terminal_execute", "terminal_get_working_dir", "terminal_set_working_dir"],
    "filesystem": ["file_read", "file_write", "file_delete", "file_list", "file_search", "file_move", "file_mkdir"],
    "apps": ["app_open", "app_focus", "app_list_windows", "app_close"],
    "opendesk_alt": ["screenshot_with_marks", "click_element", "ocr_screen", "clipboard_get", "clipboard_set", "record_workflow", "replay_workflow"],
}

DASHBOARD_HTML = f"""<!doctype html><html><head><meta charset='utf-8'><title>System Agent Dashboard</title>
<style>body{{margin:0;font-family:Segoe UI,Arial,sans-serif;background:#0e1116;color:#e5e7eb}}.wrap{{display:flex;height:100vh}}.left{{flex:2;padding:16px}}.right{{flex:1;border-left:1px solid #1f2937;padding:16px;overflow:auto}}button{{background:#1f2937;color:#e5e7eb;border:1px solid #374151;padding:8px 12px;border-radius:8px;margin-right:8px;cursor:pointer;transition:all .2s}}button.active{{background:#2563eb}}img{{width:100%;height:calc(100% - 60px);object-fit:contain;background:#000;border-radius:10px;margin-top:12px}}a{{color:#60a5fa}}</style></head>
<body><div class='wrap'><div class='left'><div><button id='btn-browser' class='active'>Browser View</button><button id='btn-desktop'>Desktop View</button></div><img id='live-view' alt='live view'/></div>
<div class='right'><h2>Status</h2><p>Public MCP: <a href='https://{NGROK_DOMAIN}/mcp' target='_blank'>https://{NGROK_DOMAIN}/mcp</a></p><p>Kali Linux: <span id='kali'>checking...</span></p><h3>Tools</h3><div id='tools'></div></div></div>
<script>
const groups={json.dumps(TOOL_GROUPS)};document.getElementById('tools').innerHTML=Object.entries(groups).map(([k,v])=>`<h4>${{k}}</h4><ul>${{v.map(t=>`<li>${{t}}</li>`).join('')}}</ul>`).join('');
let mode='browser',prevUrl=null;const img=document.getElementById('live-view');
function setMode(m){{mode=m;document.getElementById('btn-browser').classList.toggle('active',m==='browser');document.getElementById('btn-desktop').classList.toggle('active',m==='desktop');}}
document.getElementById('btn-browser').onclick=()=>setMode('browser');document.getElementById('btn-desktop').onclick=()=>setMode('desktop');
async function tick(){{const ep=mode==='browser'?'/screenshot':'/desktop';const r=await fetch(ep);const b=await r.blob();const u=URL.createObjectURL(b);img.src=u;if(prevUrl) URL.revokeObjectURL(prevUrl);prevUrl=u;}}
setInterval(tick,2000);tick();fetch('/kali-ping').then(r=>r.json()).then(d=>{{document.getElementById('kali').textContent=d.reachable?'✓ reachable':'✗ unreachable';document.getElementById('kali').style.color=d.reachable?'#22c55e':'#ef4444';}});
</script></body></html>"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            data = DASHBOARD_HTML.encode("utf-8")
            self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data); return
        if self.path == "/screenshot":
            data = asyncio.run(get_browser_screenshot_bytes())
            self.send_response(200); self.send_header("Content-Type", "image/png"); self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data); return
        if self.path == "/desktop":
            data = get_desktop_screenshot_bytes()
            self.send_response(200); self.send_header("Content-Type", "image/png"); self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data); return
        if self.path == "/kali-ping":
            r = subprocess.run(["wsl", "-d", KALI_DISTRO, "echo", "ok"], capture_output=True, text=True)
            payload = json.dumps({"reachable": r.returncode == 0 and r.stdout.strip() == "ok"}).encode("utf-8")
            self.send_response(200); self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(payload))); self.end_headers(); self.wfile.write(payload); return
        self.send_response(404); self.end_headers()


def _run_dashboard():
    server = ThreadingHTTPServer(("127.0.0.1", DASHBOARD_PORT), Handler)
    server.serve_forever()


if __name__ == "__main__":
    threading.Thread(target=_run_dashboard, daemon=True).start()
    print(f"MCP endpoint : https://{NGROK_DOMAIN}/mcp")
    print(f"Dashboard    : http://localhost:{DASHBOARD_PORT}")
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
