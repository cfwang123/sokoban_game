@echo off
setlocal EnableExtensions EnableDelayedExpansion
title Sokoban CMD

rem cmdapp1 - Windows CMD batch Sokoban (teaching)
rem MAP 49 chars: # . B * -    (B=box, *=box on goal, -=floor)
rem keys: wasd move, z undo, r reset, q quit

call :reset
echo sokoban_cmd - wasd move, z undo, r reset, q quit
echo (Windows cmd.exe / batch teaching)

:loop
echo.
call :draw
if "!WON!"=="1" (echo moves=!MOVES! WIN!) else (echo moves=!MOVES!)
set "IN="
set /p "IN=> " || goto :eof
if not defined IN goto :loop
set "IN=!IN: =!"
if "!IN!"=="" goto :loop
set "K=!IN:~0,1!"
if /i "!K!"=="w" call :move 0 -1
if /i "!K!"=="s" call :move 0 1
if /i "!K!"=="a" call :move -1 0
if /i "!K!"=="d" call :move 1 0
if /i "!K!"=="z" call :undo
if /i "!K!"=="r" call :reset
if /i "!K!"=="q" goto :eof
if "!WON!"=="1" echo Level clear!
goto :loop

:reset
set "MAP=#######"
set "MAP=!MAP!#.-.-.#"
set "MAP=!MAP!#-BBB-#"
set "MAP=!MAP!#.B-B.#"
set "MAP=!MAP!#-BBB-#"
set "MAP=!MAP!#.-.-.#"
set "MAP=!MAP!#######"
set /a PX=3
set /a PY=3
set /a MOVES=0
set "WON=0"
set /a HN=0
exit /b 0

:draw
set "ROW=!MAP:~0,7!"
call :show 0
set "ROW=!MAP:~7,7!"
call :show 1
set "ROW=!MAP:~14,7!"
call :show 2
set "ROW=!MAP:~21,7!"
call :show 3
set "ROW=!MAP:~28,7!"
call :show 4
set "ROW=!MAP:~35,7!"
call :show 5
set "ROW=!MAP:~42,7!"
call :show 6
exit /b 0

:show
rem show ROW with player if PY==%~1
set /a RY=%~1
set "S=!ROW:-= !"
set "S=!S:B=$!"
if not !RY! equ !PY! (
  echo(!S!
  exit /b 0
)
rem rebuild with player
set "A=!S:~0,1!"
set "B=!S:~1,1!"
set "C=!S:~2,1!"
set "D=!S:~3,1!"
set "E=!S:~4,1!"
set "F=!S:~5,1!"
set "G=!S:~6,1!"
if !PX! equ 0 if "!A!"=="." (set "A=+") else (set "A=@")
if !PX! equ 1 if "!B!"=="." (set "B=+") else (set "B=@")
if !PX! equ 2 if "!C!"=="." (set "C=+") else (set "C=@")
if !PX! equ 3 if "!D!"=="." (set "D=+") else (set "D=@")
if !PX! equ 4 if "!E!"=="." (set "E=+") else (set "E=@")
if !PX! equ 5 if "!F!"=="." (set "F=+") else (set "F=@")
if !PX! equ 6 if "!G!"=="." (set "G=+") else (set "G=@")
echo(!A!!B!!C!!D!!E!!F!!G!
exit /b 0

:get
set /a II=%~2*7+%~1
for %%I in (!II!) do set "CH=!MAP:~%%I,1!"
exit /b 0

:put
set /a II=%~2*7+%~1
set /a JJ=II+1
set "NC=%~3"
if !II! equ 0 (
  set "MAP=!NC!!MAP:~1!"
) else (
  for %%I in (!II!) do set "LE=!MAP:~0,%%I!"
  for %%J in (!JJ!) do set "RI=!MAP:~%%J!"
  set "MAP=!LE!!NC!!RI!"
)
exit /b 0

:check_win
echo !MAP!| find "B" >nul
if errorlevel 1 (set "WON=1") else (set "WON=0")
exit /b 0

:move
if "!WON!"=="1" exit /b 1
set /a DX=%~1
set /a DY=%~2
set /a NX=PX+DX
set /a NY=PY+DY
if !NX! lss 0 exit /b 1
if !NY! lss 0 exit /b 1
if !NX! geq 7 exit /b 1
if !NY! geq 7 exit /b 1
call :get !NX! !NY!
if "!CH!"=="#" exit /b 1
if "!CH!"=="B" goto :push
if "!CH!"=="*" goto :push
set /a HN+=1
set "H!HN!=!PX! !PY! n n n n 0"
set /a PX=NX
set /a PY=NY
exit /b 0

:push
set /a BX=NX+DX
set /a BY=NY+DY
if !BX! lss 0 exit /b 1
if !BY! lss 0 exit /b 1
if !BX! geq 7 exit /b 1
if !BY! geq 7 exit /b 1
call :get !BX! !BY!
if "!CH!"=="#" exit /b 1
if "!CH!"=="B" exit /b 1
if "!CH!"=="*" exit /b 1
set /a HN+=1
set "H!HN!=!PX! !PY! !NX! !NY! !BX! !BY! 1"
call :get !NX! !NY!
if "!CH!"=="*" (call :put !NX! !NY! .) else (call :put !NX! !NY! -)
call :get !BX! !BY!
if "!CH!"=="." (call :put !BX! !BY! *) else (call :put !BX! !BY! B)
set /a PX=NX
set /a PY=NY
set /a MOVES+=1
call :check_win
exit /b 0

:undo
if "!WON!"=="1" exit /b 1
if !HN! leq 0 exit /b 1
:ul
if !HN! leq 0 exit /b 0
call set "REC=%%H!HN!%%"
set /a HN-=1
for /f "tokens=1-7" %%a in ("!REC!") do (
  set "OPX=%%a" & set "OPY=%%b" & set "AFX=%%c" & set "AFY=%%d"
  set "ATX=%%e" & set "ATY=%%f" & set "PS=%%g"
)
if not "!PS!"=="1" (
  set /a PX=OPX & set /a PY=OPY
  goto :ul
)
set /a PX=OPX & set /a PY=OPY
call :get !ATX! !ATY!
if "!CH!"=="*" (call :put !ATX! !ATY! .) else (call :put !ATX! !ATY! -)
call :get !AFX! !AFY!
if "!CH!"=="." (call :put !AFX! !AFY! *) else (call :put !AFX! !AFY! B)
if !MOVES! gtr 0 set /a MOVES-=1
set "WON=0"
exit /b 0
