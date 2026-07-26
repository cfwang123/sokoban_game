@echo off
setlocal enabledelayedexpansion

set JSON=..\..\levels.json
set SOLVER=.\sokosolve.exe
set TIMELIMIT=10000

echo Batch solving classic levels with original solver...
echo Time limit: %TIMELIMIT%ms per level
echo.

for /l %%i in (0,1,95) do (
    echo [%%i/95] Solving level %%i...
    %SOLVER% %%i %TIMELIMIT% auto --write
    echo.
)
echo Done!