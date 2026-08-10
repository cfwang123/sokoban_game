# powershellapp1 - PowerShell Sokoban (teaching)
# run: powershell -NoProfile -ExecutionPolicy Bypass -File main.ps1
#  or: pwsh -NoProfile -File main.ps1

$ErrorActionPreference = 'Stop'
. "$PSScriptRoot/Game.ps1"

$LEVEL = @(
    '#######',
    '#. . .#',
    '# $$$ #',
    '#.$@$.#',
    '# $$$ #',
    '#. . .#',
    '#######'
)

$state = New-GameFromRows $LEVEL 0
Write-Host 'sokoban_powershell - wasd move, z undo, r reset, q quit'

while ($true) {
    Write-Host ''
    Write-Host -NoNewline (Show-GameAscii $state)
    $flag = if ($state.Won) { ' WIN!' } else { '' }
    Write-Host ("moves=$($state.Moves)$flag")
    Write-Host -NoNewline '> '
    try {
        $line = Read-Host
    } catch {
        break
    }
    if ($null -eq $line) { break }
    $line = $line.Trim()
    if ($line.Length -eq 0) { continue }
    $ch = $line.Substring(0, 1).ToLowerInvariant()
    switch ($ch) {
        'w' { Invoke-GameMove $state 0 -1 | Out-Null }
        's' { Invoke-GameMove $state 0 1 | Out-Null }
        'a' { Invoke-GameMove $state -1 0 | Out-Null }
        'd' { Invoke-GameMove $state 1 0 | Out-Null }
        'z' { Undo-Game $state | Out-Null }
        'r' { $state = New-GameFromRows $LEVEL 0 }
        'q' { break }
    }
    if ($state.Won) { Write-Host 'Level clear!' }
}
