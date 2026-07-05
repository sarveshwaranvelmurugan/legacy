@echo off
REM Legacy CLI launcher for Windows — run `legacy` from anywhere.
set "LEGACY_ROOT=%~dp0"
set "PYTHONPATH=%LEGACY_ROOT%backend"
"%LEGACY_ROOT%.venv\Scripts\python.exe" -m app.cli %*
