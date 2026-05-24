# Poweruser Local MCP Toolchain

A unified [FastMCP](https://github.com/jlowin/fastmcp) server that gives any MCP-compatible AI assistant (ChatGPT, Claude, or others) full OS-level control over a Windows machine — browser automation, desktop mouse/keyboard control, terminal access across PowerShell/CMD/WSL/Kali Linux, file system operations, and application management. Exposed securely over the internet via a stable ngrok tunnel.

---

## Requirements

- Windows 10 or 11
- Python 3.11+
- Git
- [ngrok](https://ngrok.com/) account with a **free static domain** claimed (Dashboard → Domains)
- WSL with Kali Linux installed *(optional but recommended for the `kali` shell tool)*

Node.js is not required.

---

## Installation

### 1. Clone the repo

```powershell
git clone https://github.com/ChrisAdamsdevelopment/Poweruser_Local_MCP_Toolchain.git
cd Poweruser_Local_MCP_Toolchain
```

### 2. Configure

Edit `chatgpt-system-agent/server/src/config.py` before running anything:

```python
NGROK_DOMAIN   = "your-static-domain.ngrok-free.app"   # your ngrok static domain
NGROK_TUNNEL_ID = "rd_..."                              # your ngrok tunnel ID
KALI_DISTRO    = "kali-linux"                           # WSL distro name — change if yours differs

ALLOWED_ROOTS = [
    r"C:\Users\YourName",          # replace YourName with your Windows username
    r"D:\\",
    r"\\wsl$\kali-linux\home\youruser",
    "/mnt/c/Users/YourName",
]
```

`ALLOWED_ROOTS` is an allowlist — the filesystem tools will refuse to read or write paths outside it.

### 3. Register the auto-start scheduled task

Open PowerShell **as your normal user** (not Administrator) and run:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
.\chatgpt-system-agent\setup_scheduler.ps1
```

This registers a Windows Scheduled Task (`SystemAgentMCP`) that fires `start_agent.bat` at every login. After this step, no further manual startup is required.

### 4. First launch

Either log out and back in, or start manually for the first time:

```bat
chatgpt-system-agent\start_agent.bat
```

`start_agent.bat` automatically:
1. Creates a Python virtual environment under `chatgpt-system-agent\venv\`
2. Runs `pip install -r requirements.txt`
3. Starts the ngrok tunnel on your configured domain
4. Launches the FastMCP server on port 8000

On first run, also install the Playwright browser:

```powershell
chatgpt-system-agent\venv\Scripts\python.exe -m playwright install chromium
```

---

## Connecting to an AI Assistant

Once the server is running, register the MCP endpoint in your AI client:

| Client | Where to add |
|--------|-------------|
| **ChatGPT** | Settings → Connectors → Add connector |
| **Claude Desktop** | `claude_desktop_config.json` → `mcpServers` |
| Any MCP client | Use the URL below |

**MCP endpoint URL:**
```
https://<your-ngrok-domain>/mcp
```

No authentication is required by default — restrict access via ngrok's dashboard if needed.

---

## Dashboard

A local monitoring dashboard runs at **http://localhost:7999** (never exposed publicly).

| Tab | What it shows |
|-----|--------------|
| **Browser View** | Live screenshot of whatever the AI is browsing (2-second refresh) |
| **Desktop View** | Live full-desktop screenshot |
| **Status panel** | Public MCP URL, Kali Linux reachability check, full tool list |

---

## Optional: opendesk Enhanced Desktop Control

The `opendesk_alt` tools (`click_element`, `ocr_screen`, workflow recording/replay) degrade gracefully if opendesk is not installed. To enable full functionality:

```powershell
.\venv\Scripts\pip.exe install "opendesk[core,mcp]"
.\venv\Scripts\opendesk.exe install
```

---

## Tool Reference

### browser

| Tool | Description |
|------|-------------|
| `browser_navigate` | Open a URL in the shared Chromium browser |
| `browser_screenshot` | Capture a PNG screenshot of the current browser page |
| `browser_click` | Click a page element by CSS selector |
| `browser_type` | Type text into a page element by CSS selector |
| `browser_get_content` | Get page text, button list, and input metadata |
| `browser_execute_js` | Run JavaScript in the active browser page context |
| `browser_press_key` | Send a keyboard key press to the browser page |
| `browser_close` | Close the shared browser instance and release resources |

### screen

| Tool | Description |
|------|-------------|
| `screen_capture` | Desktop screenshot of full screen or a pixel region |
| `mouse_position` | Get current mouse cursor coordinates |
| `mouse_move` | Move the mouse pointer to a screen coordinate |
| `mouse_click` | Click a screen coordinate (left/right/middle) |
| `mouse_double_click` | Double-click at a screen coordinate |
| `keyboard_type` | Type text into the active window |
| `keyboard_press` | Press a key or hotkey combination (e.g. `ctrl+c`) |
| `scroll` | Scroll vertically in the active window |

### terminal

| Tool | Description |
|------|-------------|
| `terminal_execute` | Run a command in powershell / cmd / wsl / kali / bash / gitbash |
| `terminal_get_working_dir` | Get the current default working directory |
| `terminal_set_working_dir` | Set the default working directory for subsequent commands |

### filesystem

| Tool | Description |
|------|-------------|
| `file_read` | Read file contents from an allowed path |
| `file_write` | Create or overwrite a file at an allowed path |
| `file_delete` | Delete a file or directory at an allowed path |
| `file_list` | List files and folders under an allowed directory |
| `file_search` | Search for files by glob pattern under an allowed directory |
| `file_move` | Move or rename a file/directory between allowed paths |
| `file_mkdir` | Create a directory tree at an allowed path |

### apps

| Tool | Description |
|------|-------------|
| `app_open` | Launch a Windows application by name |
| `app_focus` | Focus a window by partial title match |
| `app_list_windows` | List all top-level windows of running processes |
| `app_close` | Force-close a Windows process by name |

### opendesk_alt

| Tool | Description |
|------|-------------|
| `screenshot_with_marks` | Fallback screenshot for visual desktop analysis |
| `click_element` | Trigger a named desktop element (requires opendesk) |
| `ocr_screen` | OCR text extraction from the screen (requires opendesk) |
| `clipboard_get` | Read current clipboard text |
| `clipboard_set` | Write text to the system clipboard |
| `record_workflow` | Record a desktop workflow to a JSON file |
| `replay_workflow` | Replay a previously recorded workflow file |
