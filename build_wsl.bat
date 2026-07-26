@echo off
setlocal
rem Convenience wrapper: PSP build via WSL (no hardcoded host paths)
cd /d "%~dp0pspapp1"
call build_wsl.bat
exit /b %ERRORLEVEL%
