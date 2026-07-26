@echo off
setlocal
cd /d "%~dp0"
set SCRIPT=%~dp0..\tmp\build_psp_wsl.sh

echo [Sokoban PSP] Build via WSL Ubuntu + ~/pspdev ...
wsl -d Ubuntu -- bash -lc "sed -i 's/\r$//' /mnt/d/VS_Projects/AIPrototype/Github共享/sokoban/tmp/build_psp_wsl.sh; bash /mnt/d/VS_Projects/AIPrototype/Github共享/sokoban/tmp/build_psp_wsl.sh"
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
