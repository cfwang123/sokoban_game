# C++ vs PHP+JIT 对比
# 用法: .\scripts\bench_cpp_php.ps1

$ErrorActionPreference = "Continue"
$root = Split-Path $PSScriptRoot -Parent
Set-Location $root

$exe = "scripts\cpp_solver\sokosolve.exe"
if (-not (Test-Path $exe)) {
  Write-Host "Building C++..."
  g++ -O3 -std=c++17 -march=native -o $exe scripts\cpp_solver\solver.cpp
}

$jit = @(
  "-d", "opcache.enable_cli=1",
  "-d", "opcache.jit=tracing",
  "-d", "opcache.jit_buffer_size=256M",
  "-d", "opcache.jit_hot_func=1",
  "-d", "opcache.jit_hot_loop=1"
)

$cases = @(
  @{ id = -1; ms = 3000; name = "Classic Star" },
  @{ id = 75; ms = 3000; name = "38 R" },
  @{ id = 128; ms = 3000; name = "65 L (hard)" }
)

Write-Host "========================================"
Write-Host " C++ vs PHP+JIT Sokoban Solver Benchmark"
Write-Host "========================================"

foreach ($c in $cases) {
  Write-Host "`n--- $($c.name) id=$($c.id) limit=$($c.ms)ms ---"
  Write-Host "[C++]"
  & $exe $c.id $c.ms bf
  Write-Host "[PHP+JIT]"
  & php @jit scripts\solver_opt.php $c.id $c.ms bf
}
