@echo off
setlocal
cd /d "%~dp0"

set IMAGE=ghcr.io/pspdev/pspdev:latest
set OUTDIR=%cd%\build

echo [Sokoban PSP] Generate levels...
python -X utf8 tools\gen_levels.py
if errorlevel 1 exit /b 1

echo [Sokoban PSP] Pulling pspdev image (first time may take a while)...
docker pull %IMAGE%
if errorlevel 1 (
  echo Docker pull failed. Is Docker Desktop running?
  exit /b 1
)

if not exist "%OUTDIR%" mkdir "%OUTDIR%"

echo [Sokoban PSP] Building with Docker + psp-cmake...
docker run --rm -v "%cd%:/src" -w /src %IMAGE% bash -lc "python3 tools/gen_levels.py && rm -rf build && mkdir -p build && cd build && psp-cmake .. && make -j$(nproc) && ls -la"

if errorlevel 1 (
  echo Build failed.
  exit /b 1
)

if exist "%OUTDIR%\EBOOT.PBP" (
  copy /Y "%OUTDIR%\EBOOT.PBP" "%cd%\EBOOT.PBP" >nul
  echo.
  echo OK: EBOOT.PBP ready
  echo   - %cd%\EBOOT.PBP
  echo   - %OUTDIR%\EBOOT.PBP
  echo Open with PPSSPP, or copy to ms0:/PSP/GAME/Sokoban/
) else (
  echo EBOOT.PBP not found in build\
  exit /b 1
)

endlocal
