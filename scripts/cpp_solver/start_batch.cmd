@echo off
cd /d "%~dp0\..\.."
echo Starting batch at %date% %time%
echo PID will be in scripts\cpp_solver\batch_continue.pid
start /B "" cmd /c "node scripts\cpp_solver\batch_continue.js > scripts\cpp_solver\batch_continue_stdout.txt 2> scripts\cpp_solver\batch_continue_stderr.txt"
timeout /t 2 /nobreak >nul
echo Batch launched. Check:
echo   type scripts\cpp_solver\batch_continue_log.txt
echo   node -e "console.log(require('./levels.json').filter(l=^>!l.solution).length)"
