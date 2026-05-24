@echo off
setlocal
cd /d %~dp0 || goto :error
if not exist venv\ (
  python -m venv venv || goto :error
)
call venv\Scripts\activate.bat || goto :error
pip install -r requirements.txt --quiet || goto :error
start /B ngrok http --domain=nintendo-corncob-animal.ngrok-free.dev 8000 || goto :error
timeout /t 3 /nobreak >nul || goto :error
python server\src\main.py || goto :error
exit /b 0
:error
echo Failed to start System Agent MCP.
pause
exit /b 1
