# 推箱子核心逻辑（PowerShell 教学）

function Get-CellKey([int]$x, [int]$y) { return "$x,$y" }

function New-GameFromRows([string[]]$rows, [int]$index = 0) {
    $walls = @{}
    $goals = @{}
    $boxes = @{}
    $px = 0; $py = 0
    $maxX = 0; $maxY = 0
    for ($y = 0; $y -lt $rows.Count; $y++) {
        $maxY = $y
        $row = $rows[$y]
        for ($x = 0; $x -lt $row.Length; $x++) {
            if ($x -gt $maxX) { $maxX = $x }
            $ch = $row[$x]
            $k = Get-CellKey $x $y
            switch ($ch) {
                '#' { $walls[$k] = $true }
                '.' { $goals[$k] = $true }
                '$' { $boxes[$k] = $true }
                '*' { $boxes[$k] = $true; $goals[$k] = $true }
                '@' { $px = $x; $py = $y }
                '+' { $px = $x; $py = $y; $goals[$k] = $true }
            }
        }
    }
    return [pscustomobject]@{
        Walls = $walls; Goals = $goals; Boxes = $boxes
        PlayerX = $px; PlayerY = $py
        Moves = 0; Won = $false
        Width = $maxX + 1; Height = $maxY + 1
        LevelIndex = $index; Hist = [System.Collections.ArrayList]@()
    }
}

function Test-GameWin($s) {
    foreach ($b in @($s.Boxes.Keys)) {
        if (-not $s.Goals.ContainsKey($b)) { $s.Won = $false; return }
    }
    $s.Won = $true
}

function Invoke-GameMove($s, [int]$dx, [int]$dy) {
    if ($s.Won) { return $false }
    $nx = $s.PlayerX + $dx
    $ny = $s.PlayerY + $dy
    $nk = Get-CellKey $nx $ny
    if ($s.Walls.ContainsKey($nk)) { return $false }
    if ($s.Boxes.ContainsKey($nk)) {
        $bx = $nx + $dx; $by = $ny + $dy
        $bk = Get-CellKey $bx $by
        if ($s.Walls.ContainsKey($bk) -or $s.Boxes.ContainsKey($bk)) { return $false }
        [void]$s.Hist.Add(@{ PX = $s.PlayerX; PY = $s.PlayerY; BoxFrom = $nk; BoxTo = $bk })
        $s.Boxes.Remove($nk)
        $s.Boxes[$bk] = $true
        $s.PlayerX = $nx; $s.PlayerY = $ny
        $s.Moves++
        Test-GameWin $s
        return $true
    }
    [void]$s.Hist.Add(@{ PX = $s.PlayerX; PY = $s.PlayerY; BoxFrom = $null; BoxTo = $null })
    $s.PlayerX = $nx; $s.PlayerY = $ny
    return $true
}

function Undo-Game($s) {
    if ($s.Won -or $s.Hist.Count -eq 0) { return $false }
    while ($s.Hist.Count -gt 0) {
        $e = $s.Hist[$s.Hist.Count - 1]
        $s.Hist.RemoveAt($s.Hist.Count - 1)
        if ($null -ne $e.BoxFrom) {
            $s.PlayerX = $e.PX; $s.PlayerY = $e.PY
            $s.Boxes.Remove($e.BoxTo)
            $s.Boxes[$e.BoxFrom] = $true
            if ($s.Moves -gt 0) { $s.Moves-- }
            $s.Won = $false
            return $true
        }
        $s.PlayerX = $e.PX; $s.PlayerY = $e.PY
    }
    return $true
}

function Show-GameAscii($s) {
    $sb = New-Object System.Text.StringBuilder
    for ($y = 0; $y -lt $s.Height; $y++) {
        for ($x = 0; $x -lt $s.Width; $x++) {
            $k = Get-CellKey $x $y
            if ($s.PlayerX -eq $x -and $s.PlayerY -eq $y) {
                [void]$sb.Append($(if ($s.Goals.ContainsKey($k)) { '+' } else { '@' }))
            } elseif ($s.Boxes.ContainsKey($k)) {
                [void]$sb.Append($(if ($s.Goals.ContainsKey($k)) { '*' } else { '$' }))
            } elseif ($s.Walls.ContainsKey($k)) {
                [void]$sb.Append('#')
            } elseif ($s.Goals.ContainsKey($k)) {
                [void]$sb.Append('.')
            } else {
                [void]$sb.Append(' ')
            }
        }
        [void]$sb.AppendLine()
    }
    return $sb.ToString()
}
