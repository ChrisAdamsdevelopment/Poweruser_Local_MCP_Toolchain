"""Configuration constants for the System Agent MCP server."""

NGROK_DOMAIN = "nintendo-corncob-animal.ngrok-free.dev"
NGROK_TUNNEL_ID = "rd_3E7SQ1RhcgZxoY7fx7QlXYHmOuC"
KALI_DISTRO = "kali-linux"
DASHBOARD_PORT = 7999

ALLOWED_SHELLS = {
    "powershell": "powershell -NoProfile -Command",
    "cmd": "cmd /c",
    "kali": "wsl -d kali-linux",  # PRIMARY — default user, never root
    "wsl": "wsl",
    "bash": "bash -c",
    "gitbash": '"C:\\Program Files\\Git\\bin\\bash.exe" -c',
}

ALLOWED_ROOTS = [
    r"C:\Users\<YourName>",
    r"D:\\",
    r"\\wsl$\kali-linux\home\<user>",
    "/mnt/c/Users/<YourName>",
]
