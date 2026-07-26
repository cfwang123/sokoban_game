@echo off
setlocal
cd /d "%~dp0"

where make >nul 2>&1
if errorlevel 1 (
  echo make not found, using direct gcc build...
  goto :direct
)

make
if errorlevel 1 exit /b 1
goto :eof

:direct
if not exist build mkdir build
rem Toolchain: set DEVKITARM or ARM_NONE_EABI_PREFIX, or put arm-none-eabi-* on PATH
if defined DEVKITARM (
  set "PREFIX=%DEVKITARM%\bin\arm-none-eabi-"
) else if defined ARM_NONE_EABI_PREFIX (
  set "PREFIX=%ARM_NONE_EABI_PREFIX%"
) else (
  set "PREFIX=arm-none-eabi-"
)
set CC=%PREFIX%gcc
set OBJCOPY=%PREFIX%objcopy
set ARCH=-mthumb -mthumb-interwork -mcpu=arm7tdmi
set CFLAGS=%ARCH% -O2 -fomit-frame-pointer -ffast-math -ffreestanding -fno-strict-aliasing -Wall -Iinclude

echo [1/3] Assets...
python -X utf8 tools\gen_tiles.py
if errorlevel 1 exit /b 1
python -X utf8 tools\gen_levels.py
if errorlevel 1 exit /b 1

echo [2/3] Compile...
for %%f in (src\*.c) do (
  %CC% %CFLAGS% -c %%f -o build\%%~nf.o
  if errorlevel 1 exit /b 1
)
%CC% %ARCH% -ffreestanding -c src\crt0.s -o build\crt0.o
if errorlevel 1 exit /b 1

echo [3/3] Link...
%CC% %ARCH% -nostdlib -T gba.ld -Wl,-Map,build\sokoban.map -o build\sokoban.elf build\*.o -lgcc
if errorlevel 1 exit /b 1
%OBJCOPY% -O binary build\sokoban.elf build\sokoban.bin
if errorlevel 1 exit /b 1
node tools\gbafix.js build\sokoban.bin SOKOBAN
if errorlevel 1 exit /b 1
copy /Y build\sokoban.bin sokoban.gba >nul
echo Built sokoban.gba
dir sokoban.gba
endlocal
