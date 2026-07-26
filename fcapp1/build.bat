@echo off
setlocal
set ROOT=%~dp0
rem tools_cc65 lives under AIPrototype/game (three levels up from fcapp1)
set CC65=%ROOT%..\..\..\game\tools_cc65\bin
set CC65_LIB=%ROOT%..\..\..\game\tools_cc65\lib
set PATH=%CC65%;%PATH%
set BUILD=%ROOT%build
set SRC=%ROOT%src
if not exist "%BUILD%" mkdir "%BUILD%"

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
  "%CC65_LIB%\none.lib" ^
  -m "%BUILD%\map.txt"
if errorlevel 1 exit /b 1

echo Built %ROOT%sokoban.nes
dir "%ROOT%sokoban.nes"
endlocal
