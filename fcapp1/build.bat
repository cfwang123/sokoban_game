@echo off
setlocal
set ROOT=%~dp0
rem cc65: set CC65_HOME, or put tools under fcapp1/tools/cc65, or on PATH
if defined CC65_HOME (
  set "CC65=%CC65_HOME%\bin"
  set "CC65_LIB=%CC65_HOME%\lib"
) else if exist "%ROOT%tools\cc65\bin\cc65.exe" (
  set "CC65=%ROOT%tools\cc65\bin"
  set "CC65_LIB=%ROOT%tools\cc65\lib"
) else (
  set "CC65="
  set "CC65_LIB="
)
if defined CC65 set "PATH=%CC65%;%PATH%"
set BUILD=%ROOT%build
set SRC=%ROOT%src
if not exist "%BUILD%" mkdir "%BUILD%"

where cc65 >nul 2>&1
if errorlevel 1 (
  echo cc65 not found. Install cc65 and either:
  echo   - add bin to PATH, or
  echo   - set CC65_HOME to the cc65 root, or
  echo   - place tools under fcapp1\tools\cc65\
  exit /b 1
)

if defined CC65_LIB (
  set "NONE_LIB=%CC65_LIB%\none.lib"
) else (
  set "NONE_LIB=none.lib"
)

echo [1/5] CHR tiles...
python -X utf8 "%ROOT%tools\make_chr.py"
if errorlevel 1 exit /b 1

echo [2/5] Generate levels...
python -X utf8 "%ROOT%tools\gen_levels.py"
if errorlevel 1 exit /b 1

echo [3/5] Compile C...
cc65 -O -Cl -t none -I "%SRC%" -o "%BUILD%\main.s"   "%SRC%\main.c"
if errorlevel 1 exit /b 1
cc65 -O -Cl -t none -I "%SRC%" -o "%BUILD%\music.s"  "%SRC%\music.c"
if errorlevel 1 exit /b 1
cc65 -O -Cl -t none -I "%SRC%" -o "%BUILD%\levels.s" "%SRC%\levels.c"
if errorlevel 1 exit /b 1

echo [4/5] Assemble...
ca65 -g -I "%SRC%" -o "%BUILD%\main.o"   "%BUILD%\main.s"
if errorlevel 1 exit /b 1
ca65 -g -I "%SRC%" -o "%BUILD%\music.o"  "%BUILD%\music.s"
if errorlevel 1 exit /b 1
ca65 -g -I "%SRC%" -o "%BUILD%\levels.o" "%BUILD%\levels.s"
if errorlevel 1 exit /b 1
ca65 -g -I "%SRC%" -o "%BUILD%\header.o" "%SRC%\header.s"
if errorlevel 1 exit /b 1
ca65 -g -I "%SRC%" -o "%BUILD%\reset.o"  "%SRC%\reset.s"
if errorlevel 1 exit /b 1
ca65 -g -I "%SRC%" -o "%BUILD%\nmi.o"    "%SRC%\nmi.s"
if errorlevel 1 exit /b 1
ca65 -g -o "%BUILD%\chr.o" "%SRC%\chr.s" --bin-include-dir "%ROOT%"
if errorlevel 1 exit /b 1

echo [5/5] Link...
ld65 -C "%ROOT%nrom256.cfg" -o "%ROOT%sokoban.nes" ^
  "%BUILD%\header.o" "%BUILD%\reset.o" "%BUILD%\nmi.o" ^
  "%BUILD%\main.o" "%BUILD%\music.o" "%BUILD%\levels.o" "%BUILD%\chr.o" ^
  "%NONE_LIB%" ^
  -m "%BUILD%\map.txt"
if errorlevel 1 exit /b 1

echo Built %ROOT%sokoban.nes
dir "%ROOT%sokoban.nes"
endlocal
