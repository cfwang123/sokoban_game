# 依次用 C++ 求解所有无答案关卡（时间不限，每关独立进程）
# 用法: powershell -File scripts/cpp_solver/batch_all.ps1

$ErrorActionPreference = "Continue"
$root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $root

$exe = Join-Path $root "scripts\cpp_solver\sokosolve.exe"
$solverCpp = Join-Path $root "scripts\cpp_solver\solver.cpp"
if (-not (Test-Path $exe)) {
  Write-Host "Building..."
  & g++ -O3 -std=c++17 -march=native -o $exe $solverCpp
  if ($LASTEXITCODE -ne 0) { exit 1 }
}

# 进度日志（勿与 Start-Process RedirectStandardOutput 同一文件）
$log = Join-Path $root "scripts\cpp_solver\batch_progress.txt"
function Log([string]$msg) {
  $line = "$(Get-Date -Format 'HH:mm:ss') $msg"
  try { Add-Content -Path $log -Value $line -Encoding UTF8 -ErrorAction SilentlyContinue } catch {}
  Write-Host $line
}

Log "=== Batch start ==="

$listJs = Join-Path $root "scripts\cpp_solver\list_unsolved.js"
$idsJson = & node $listJs
$todo = $idsJson | ConvertFrom-Json
$total = @($todo).Count
Log "Unsolved: $total"

$solved = 0
$failed = 0
$i = 0
foreach ($item in $todo) {
  $i++
  Log ">>> [$i/$total] boxes=$($item.boxes) id=$($item.id) $($item.name)"

  # 0 = unlimited; auto; --write
  $outFile = Join-Path $root "scripts\cpp_solver\last_level_out.txt"
  & $exe $item.id 0 auto --write 2>&1 | Tee-Object -FilePath $outFile
  $out = Get-Content $outFile -Raw -ErrorAction SilentlyContinue
  if ($out -match "SOLVED") {
    $solved++
    Log "OK id=$($item.id)"
  } else {
    $failed++
    Log "FAIL id=$($item.id)"
  }

  if (($i % 5 -eq 0) -or ($i -eq $total)) {
    & node (Join-Path $root "scripts\gen_levels_js.js")
  }

  $left = & node -e "const L=require('./levels.json'); process.stdout.write(String(L.filter(l=>!l.solution).length))"
  Log "--- solved=$solved failed=$failed remaining=$left ---"
}

& node (Join-Path $root "scripts\gen_levels_js.js")
Log "=== Batch done solved=$solved failed=$failed ==="
Write-Host "Log: $log"
