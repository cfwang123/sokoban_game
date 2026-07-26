@echo off
setlocal
cd /d "%~dp0"

echo [Sokoban PSP] Build via WSL Ubuntu + ~/pspdev ...

rem Convert this directory to a WSL path (no hardcoded host path)
for /f "usebackq delims=" %%i in (`wsl -d Ubuntu wslpath -a "%CD%"`) do set "WSL_DIR=%%i"
if not defined WSL_DIR (
  echo Failed to resolve WSL path for: %CD%
  echo Is WSL Ubuntu installed?
  exit /b 1
)

wsl -d Ubuntu -- bash -lc "set -e; export PSPDEV=\"$HOME/pspdev\"; export PATH=\"$PSPDEV/bin:$PATH\"; cd \"%WSL_DIR%\"; if [ ! -x \"$PSPDEV/bin/psp-gcc\" ]; then echo \"Missing $PSPDEV/bin/psp-gcc — extract pspdev to ~/pspdev\"; exit 1; fi; bash ./build.sh"
if errorlevel 1 (
  echo Build failed.
  exit /b 1
)

if exist "%~dp0EBOOT.PBP" (
  echo.
  echo OK: %~dp0EBOOT.PBP
  dir "%~dp0EBOOT.PBP"
) else (
  echo EBOOT.PBP not found
  exit /b 1
)
endlocal
