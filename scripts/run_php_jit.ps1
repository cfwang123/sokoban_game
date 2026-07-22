# PHP 8 + OPcache JIT 运行求解器
# 用法: .\scripts\run_php_jit.ps1 [levelId] [timeMs] [mode]
# mode: dfs | bf | auto

param(
  [int]$LevelId = 128,
  [int]$TimeMs = 5000,
  [string]$Mode = "bf"
)

$args_php = @(
  "-d", "opcache.enable_cli=1",
  "-d", "opcache.jit=tracing",
  "-d", "opcache.jit_buffer_size=256M",
  "-d", "opcache.jit_hot_func=1",
  "-d", "opcache.jit_hot_loop=1",
  "-d", "opcache.jit_hot_return=1",
  "-d", "opcache.jit_hot_side_exit=1",
  "scripts/solver_opt.php",
  "$LevelId",
  "$TimeMs",
  $Mode
)

& php @args_php
