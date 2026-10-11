@echo off
set "CLAUDE_STATUSLINE_SRC=%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -Command "iex (Get-Content -Raw -Encoding UTF8 (Join-Path $env:CLAUDE_STATUSLINE_SRC 'install.ps1'))"
pause
