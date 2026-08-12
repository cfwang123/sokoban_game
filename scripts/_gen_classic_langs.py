#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate remaining multi-language Sokoban teaching CLIs."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEVEL_ROWS = [
    "#######",
    "#. . .#",
    "# $$$ #",
    "#.$@$.#",
    "# $$$ #",
    "#. . .#",
    "#######",
]


def write(rel: str, content: str) -> None:
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    print("wrote", rel)


def changelog(lang: str) -> str:
    return f"""# Changelog

## 1.0.0 — 2026-08-10

- 初版 {lang} 核心逻辑 + 终端 main
"""


def readme(title: str, need: str, run: str) -> str:
    return f"""# {title}

{need}

```bash
{run}
```

键位：WASD 移动，z 撤销，r 重置，q 退出。
"""


def gen_powershell() -> None:
    write(
        "powershellapp1/Game.ps1",
        r"""# 推箱子核心逻辑（PowerShell 教学）

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
""",
    )
    write(
        "powershellapp1/main.ps1",
        r"""# powershellapp1 — PowerShell 推箱子终端版（教学）
# 运行: pwsh -File main.ps1

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
Write-Host 'sokoban_powershell — wasd 移动, z 撤销, r 重置, q 退出'

while ($true) {
    Write-Host ''
    Write-Host -NoNewline (Show-GameAscii $state)
    $flag = if ($state.Won) { ' WIN!' } else { '' }
    Write-Host ("moves=$($state.Moves)$flag")
    Write-Host -NoNewline '> '
    $line = Read-Host
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
""",
    )
    write(
        "powershellapp1/readme.md",
        readme(
            "powershellapp1 — PowerShell 推箱子（教学）",
            "需要 PowerShell 5+ 或 PowerShell 7（`pwsh`）。",
            "cd powershellapp1\npwsh -File main.ps1",
        ),
    )
    write("powershellapp1/CHANGELOG.md", changelog("PowerShell"))


def gen_bash() -> None:
    write(
        "bashapp1/game.sh",
        r"""# 推箱子核心逻辑（Bash 教学）
# shellcheck shell=bash

game_key() { echo "$1,$2"; }

game_from_rows() {
  # sets globals: G_WALLS G_GOALS G_BOXES G_PX G_PY G_MOVES G_WON G_W G_H G_HIST
  declare -gA G_WALLS G_GOALS G_BOXES
  G_WALLS=(); G_GOALS=(); G_BOXES=()
  G_PX=0; G_PY=0; G_MOVES=0; G_WON=0
  G_W=0; G_H=0
  G_HIST=()
  local y=0 row x ch k maxx=0
  for row in "$@"; do
    for ((x=0; x<${#row}; x++)); do
      (( x > maxx )) && maxx=$x
      ch=${row:x:1}
      k=$(game_key "$x" "$y")
      case "$ch" in
        \#) G_WALLS[$k]=1 ;;
        .) G_GOALS[$k]=1 ;;
        \$) G_BOXES[$k]=1 ;;
        \*) G_BOXES[$k]=1; G_GOALS[$k]=1 ;;
        @) G_PX=$x; G_PY=$y ;;
        +) G_PX=$x; G_PY=$y; G_GOALS[$k]=1 ;;
      esac
    done
    ((y++))
  done
  G_W=$((maxx + 1))
  G_H=$y
}

game_check_win() {
  local b
  for b in "${!G_BOXES[@]}"; do
    [[ -z ${G_GOALS[$b]+x} ]] && { G_WON=0; return; }
  done
  G_WON=1
}

game_try_move() {
  local dx=$1 dy=$2
  (( G_WON )) && return 1
  local nx=$((G_PX + dx)) ny=$((G_PY + dy))
  local nk bx by bk
  nk=$(game_key "$nx" "$ny")
  [[ -n ${G_WALLS[$nk]+x} ]] && return 1
  if [[ -n ${G_BOXES[$nk]+x} ]]; then
    bx=$((nx + dx)); by=$((ny + dy))
    bk=$(game_key "$bx" "$by")
    [[ -n ${G_WALLS[$bk]+x} || -n ${G_BOXES[$bk]+x} ]] && return 1
    G_HIST+=("$G_PX $G_PY $nk $bk")
    unset "G_BOXES[$nk]"
    G_BOXES[$bk]=1
    G_PX=$nx; G_PY=$ny
    ((G_MOVES++))
    game_check_win
    return 0
  fi
  G_HIST+=("$G_PX $G_PY - -")
  G_PX=$nx; G_PY=$ny
  return 0
}

game_undo() {
  (( G_WON || ${#G_HIST[@]} == 0 )) && return 1
  local entry hx hy bf bt
  while (( ${#G_HIST[@]} > 0 )); do
    entry=${G_HIST[-1]}
    unset 'G_HIST[-1]'
    read -r hx hy bf bt <<<"$entry"
    if [[ $bf != - ]]; then
      G_PX=$hx; G_PY=$hy
      unset "G_BOXES[$bt]"
      G_BOXES[$bf]=1
      (( G_MOVES > 0 )) && ((G_MOVES--))
      G_WON=0
      return 0
    fi
    G_PX=$hx; G_PY=$hy
  done
  return 0
}

game_render() {
  local y x k
  for ((y=0; y<G_H; y++)); do
    for ((x=0; x<G_W; x++)); do
      k=$(game_key "$x" "$y")
      if (( x == G_PX && y == G_PY )); then
        [[ -n ${G_GOALS[$k]+x} ]] && printf '+' || printf '@'
      elif [[ -n ${G_BOXES[$k]+x} ]]; then
        [[ -n ${G_GOALS[$k]+x} ]] && printf '*' || printf '$'
      elif [[ -n ${G_WALLS[$k]+x} ]]; then
        printf '#'
      elif [[ -n ${G_GOALS[$k]+x} ]]; then
        printf '.'
      else
        printf ' '
      fi
    done
    printf '\n'
  done
}
""",
    )
    write(
        "bashapp1/main.sh",
        r"""#!/usr/bin/env bash
# bashapp1 — Bash 推箱子终端版（教学）
set -euo pipefail
DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
# shellcheck source=game.sh
source "$DIR/game.sh"

LEVEL=(
  '#######'
  '#. . .#'
  '# $$$ #'
  '#.$@$.#'
  '# $$$ #'
  '#. . .#'
  '#######'
)

game_from_rows "${LEVEL[@]}"
echo "sokoban_bash — wasd 移动, z 撤销, r 重置, q 退出"

while true; do
  echo
  game_render
  flag=""; (( G_WON )) && flag=" WIN!"
  echo "moves=${G_MOVES}${flag}"
  printf '> '
  if ! IFS= read -r line; then break; fi
  line=${line//[[:space:]]/}
  [[ -z $line ]] && continue
  ch=${line:0:1}
  ch=${ch,,}
  case $ch in
    w) game_try_move 0 -1 || true ;;
    s) game_try_move 0 1 || true ;;
    a) game_try_move -1 0 || true ;;
    d) game_try_move 1 0 || true ;;
    z) game_undo || true ;;
    r) game_from_rows "${LEVEL[@]}" ;;
    q) break ;;
  esac
  (( G_WON )) && echo "Level clear!"
done
""",
    )
    write(
        "bashapp1/readme.md",
        readme(
            "bashapp1 — Bash 推箱子（教学）",
            "需要 Bash 4+（关联数组）。Git Bash / WSL / Linux / macOS。",
            "cd bashapp1\nbash main.sh",
        ),
    )
    write("bashapp1/CHANGELOG.md", changelog("Bash"))


def gen_julia() -> None:
    write(
        "juliaapp1/game.jl",
        r"""# 推箱子核心逻辑（Julia 教学）

const Cell = String

mutable struct Hist
    player::Tuple{Int,Int}
    box_from::Union{Nothing,Cell}
    box_to::Union{Nothing,Cell}
end

mutable struct GameState
    walls::Set{Cell}
    goals::Set{Cell}
    boxes::Set{Cell}
    player::Tuple{Int,Int}
    moves::Int
    won::Bool
    width::Int
    height::Int
    hist::Vector{Hist}
end

cell_key(x::Int, y::Int) = string(x, ",", y)

function from_rows(rows::Vector{String}, index::Int=0)::GameState
    walls = Set{Cell}()
    goals = Set{Cell}()
    boxes = Set{Cell}()
    px, py = 0, 0
    max_x, max_y = 0, 0
    for (y, row) in enumerate(rows)
        max_y = y - 1
        for (x0, ch) in enumerate(row)
            x = x0 - 1
            max_x = max(max_x, x)
            k = cell_key(x, y - 1)
            if ch == '#'
                push!(walls, k)
            elseif ch == '.'
                push!(goals, k)
            elseif ch == '$'
                push!(boxes, k)
            elseif ch == '*'
                push!(boxes, k); push!(goals, k)
            elseif ch == '@'
                px, py = x, y - 1
            elseif ch == '+'
                px, py = x, y - 1
                push!(goals, k)
            end
        end
    end
    GameState(walls, goals, boxes, (px, py), 0, false, max_x + 1, max_y + 1, Hist[])
end

function check_win!(s::GameState)
    s.won = all(b -> b in s.goals, s.boxes)
end

function try_move!(s::GameState, dx::Int, dy::Int)::Bool
    s.won && return false
    px, py = s.player
    nx, ny = px + dx, py + dy
    nk = cell_key(nx, ny)
    nk in s.walls && return false
    if nk in s.boxes
        bx, by = nx + dx, ny + dy
        bk = cell_key(bx, by)
        (bk in s.walls || bk in s.boxes) && return false
        push!(s.hist, Hist(s.player, nk, bk))
        delete!(s.boxes, nk)
        push!(s.boxes, bk)
        s.player = (nx, ny)
        s.moves += 1
        check_win!(s)
        return true
    end
    push!(s.hist, Hist(s.player, nothing, nothing))
    s.player = (nx, ny)
    true
end

function undo!(s::GameState)::Bool
    (s.won || isempty(s.hist)) && return false
    while !isempty(s.hist)
        e = pop!(s.hist)
        if e.box_from !== nothing
            s.player = e.player
            delete!(s.boxes, e.box_to)
            push!(s.boxes, e.box_from)
            s.moves > 0 && (s.moves -= 1)
            s.won = false
            return true
        end
        s.player = e.player
    end
    true
end

function render_ascii(s::GameState)::String
    io = IOBuffer()
    for y in 0:s.height-1
        for x in 0:s.width-1
            k = cell_key(x, y)
            if s.player == (x, y)
                print(io, k in s.goals ? '+' : '@')
            elseif k in s.boxes
                print(io, k in s.goals ? '*' : '$')
            elseif k in s.walls
                print(io, '#')
            elseif k in s.goals
                print(io, '.')
            else
                print(io, ' ')
            end
        end
        print(io, '\n')
    end
    String(take!(io))
end
""",
    )
    write(
        "juliaapp1/main.jl",
        r"""#!/usr/bin/env julia
# juliaapp1 — Julia 推箱子终端版（教学）

include(joinpath(@__DIR__, "game.jl"))

const LEVEL = [
    "#######",
    "#. . .#",
    "# $$$ #",
    "#.$@$.#",
    "# $$$ #",
    "#. . .#",
    "#######",
]

function main()
    state = from_rows(LEVEL, 0)
    println("sokoban_julia — wasd 移动, z 撤销, r 重置, q 退出")
    while true
        println()
        print(render_ascii(state))
        flag = state.won ? " WIN!" : ""
        print("moves=$(state.moves)$flag\n> ")
        line = try
            readline()
        catch
            break
        end
        isempty(line) && continue
        ch = lowercase(line[1])
        if ch == 'w'
            try_move!(state, 0, -1)
        elseif ch == 's'
            try_move!(state, 0, 1)
        elseif ch == 'a'
            try_move!(state, -1, 0)
        elseif ch == 'd'
            try_move!(state, 1, 0)
        elseif ch == 'z'
            undo!(state)
        elseif ch == 'r'
            state = from_rows(LEVEL, 0)
        elseif ch == 'q'
            break
        end
        state.won && println("Level clear!")
    end
end

main()
""",
    )
    write(
        "juliaapp1/readme.md",
        readme(
            "juliaapp1 — Julia 推箱子（教学）",
            "需要 [Julia](https://julialang.org/)。",
            "cd juliaapp1\njulia main.jl",
        ),
    )
    write("juliaapp1/CHANGELOG.md", changelog("Julia"))


def gen_groovy() -> None:
    write(
        "groovyapp1/Game.groovy",
        r"""// 推箱子核心逻辑（Groovy 教学）

class Hist {
    int px, py
    String boxFrom, boxTo
    Hist(int px, int py, String boxFrom = null, String boxTo = null) {
        this.px = px; this.py = py; this.boxFrom = boxFrom; this.boxTo = boxTo
    }
}

class GameState {
    Set<String> walls = [] as Set
    Set<String> goals = [] as Set
    Set<String> boxes = [] as Set
    int px = 0, py = 0
    int moves = 0
    boolean won = false
    int width = 0, height = 0
    List<Hist> hist = []

    static String key(int x, int y) { "$x,$y" }

    static GameState fromRows(List<String> rows, int index = 0) {
        def s = new GameState()
        int maxX = 0, maxY = 0
        rows.eachWithIndex { row, y ->
            maxY = y
            row.eachWithIndex { ch, x ->
                if (x > maxX) maxX = x
                def k = key(x, y)
                switch (ch) {
                    case '#': s.walls << k; break
                    case '.': s.goals << k; break
                    case '$': s.boxes << k; break
                    case '*': s.boxes << k; s.goals << k; break
                    case '@': s.px = x; s.py = y; break
                    case '+': s.px = x; s.py = y; s.goals << k; break
                }
            }
        }
        s.width = maxX + 1
        s.height = maxY + 1
        s
    }

    void checkWin() {
        won = boxes.every { goals.contains(it) }
    }

    boolean tryMove(int dx, int dy) {
        if (won) return false
        int nx = px + dx, ny = py + dy
        def nk = key(nx, ny)
        if (walls.contains(nk)) return false
        if (boxes.contains(nk)) {
            int bx = nx + dx, by = ny + dy
            def bk = key(bx, by)
            if (walls.contains(bk) || boxes.contains(bk)) return false
            hist << new Hist(px, py, nk, bk)
            boxes.remove(nk)
            boxes << bk
            px = nx; py = ny
            moves++
            checkWin()
            return true
        }
        hist << new Hist(px, py)
        px = nx; py = ny
        true
    }

    boolean undo() {
        if (won || hist.isEmpty()) return false
        Hist entry = null
        while (!hist.isEmpty()) {
            entry = hist.remove(hist.size() - 1)
            if (entry.boxFrom != null) break
            px = entry.px; py = entry.py
        }
        if (entry == null || entry.boxFrom == null) return true
        px = entry.px; py = entry.py
        boxes.remove(entry.boxTo)
        boxes << entry.boxFrom
        if (moves > 0) moves--
        won = false
        true
    }

    String renderAscii() {
        def sb = new StringBuilder()
        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                def k = key(x, y)
                if (px == x && py == y) sb << (goals.contains(k) ? '+' : '@')
                else if (boxes.contains(k)) sb << (goals.contains(k) ? '*' : '$')
                else if (walls.contains(k)) sb << '#'
                else if (goals.contains(k)) sb << '.'
                else sb << ' '
            }
            sb << '\n'
        }
        sb.toString()
    }
}
""",
    )
    write(
        "groovyapp1/main.groovy",
        r"""#!/usr/bin/env groovy
// groovyapp1 — Groovy 推箱子终端版（教学）

evaluate(new File(new File(getClass().protectionDomain.codeSource.location.path).parentFile ?: new File('.'), 'Game.groovy').text)
// simpler load:
def scriptDir = new File(getClass().protectionDomain?.codeSource?.location?.toURI()?.path ?: '.').parentFile
if (scriptDir == null) scriptDir = new File('.')
// Use relative include via GroovyShell:
def base = new File(System.getProperty('user.dir'))
// When run as `groovy main.groovy` cwd is groovyapp1
evaluate(new File('Game.groovy').text)

def LEVEL = [
    '#######',
    '#. . .#',
    '# $$$ #',
    '#.$@$.#',
    '# $$$ #',
    '#. . .#',
    '#######',
]

def state = GameState.fromRows(LEVEL, 0)
println 'sokoban_groovy — wasd 移动, z 撤销, r 重置, q 退出'
def reader = System.in.newReader()

while (true) {
    println()
    print state.renderAscii()
    def flag = state.won ? ' WIN!' : ''
    print "moves=${state.moves}${flag}\n> "
    def line = reader.readLine()
    if (line == null) break
    line = line.trim()
    if (!line) continue
    def ch = line[0].toLowerCase()
    switch (ch) {
        case 'w': state.tryMove(0, -1); break
        case 's': state.tryMove(0, 1); break
        case 'a': state.tryMove(-1, 0); break
        case 'd': state.tryMove(1, 0); break
        case 'z': state.undo(); break
        case 'r': state = GameState.fromRows(LEVEL, 0); break
        case 'q': return
    }
    if (state.won) println 'Level clear!'
}
""",
    )
    write(
        "groovyapp1/readme.md",
        readme(
            "groovyapp1 — Groovy 推箱子（教学）",
            "需要 [Groovy](https://groovy-lang.org/)（`groovy`）。",
            "cd groovyapp1\ngroovy main.groovy",
        ),
    )
    write("groovyapp1/CHANGELOG.md", changelog("Groovy"))


def gen_cpp() -> None:
    write(
        "cppapp1/game.hpp",
        r"""// 推箱子核心逻辑（C++ 教学）
#pragma once
#include <string>
#include <unordered_set>
#include <vector>
#include <utility>

struct Hist {
    int px, py;
    std::string boxFrom, boxTo; // empty boxFrom => walk only
    bool isPush = false;
};

struct GameState {
    std::unordered_set<std::string> walls, goals, boxes;
    int px = 0, py = 0;
    int moves = 0;
    bool won = false;
    int width = 0, height = 0;
    std::vector<Hist> hist;

    static std::string key(int x, int y) {
        return std::to_string(x) + "," + std::to_string(y);
    }

    static GameState fromRows(const std::vector<std::string>& rows, int index = 0) {
        GameState s;
        int maxX = 0, maxY = 0;
        for (int y = 0; y < (int)rows.size(); ++y) {
            maxY = y;
            const auto& row = rows[y];
            for (int x = 0; x < (int)row.size(); ++x) {
                if (x > maxX) maxX = x;
                char ch = row[x];
                auto k = key(x, y);
                switch (ch) {
                case '#': s.walls.insert(k); break;
                case '.': s.goals.insert(k); break;
                case '$': s.boxes.insert(k); break;
                case '*': s.boxes.insert(k); s.goals.insert(k); break;
                case '@': s.px = x; s.py = y; break;
                case '+': s.px = x; s.py = y; s.goals.insert(k); break;
                default: break;
                }
            }
        }
        s.width = maxX + 1;
        s.height = maxY + 1;
        (void)index;
        return s;
    }

    void checkWin() {
        for (const auto& b : boxes) {
            if (!goals.count(b)) { won = false; return; }
        }
        won = true;
    }

    bool tryMove(int dx, int dy) {
        if (won) return false;
        int nx = px + dx, ny = py + dy;
        auto nk = key(nx, ny);
        if (walls.count(nk)) return false;
        if (boxes.count(nk)) {
            int bx = nx + dx, by = ny + dy;
            auto bk = key(bx, by);
            if (walls.count(bk) || boxes.count(bk)) return false;
            hist.push_back(Hist{px, py, nk, bk, true});
            boxes.erase(nk);
            boxes.insert(bk);
            px = nx; py = ny;
            ++moves;
            checkWin();
            return true;
        }
        hist.push_back(Hist{px, py, "", "", false});
        px = nx; py = ny;
        return true;
    }

    bool undo() {
        if (won || hist.empty()) return false;
        while (!hist.empty()) {
            Hist e = hist.back();
            hist.pop_back();
            if (e.isPush) {
                px = e.px; py = e.py;
                boxes.erase(e.boxTo);
                boxes.insert(e.boxFrom);
                if (moves > 0) --moves;
                won = false;
                return true;
            }
            px = e.px; py = e.py;
        }
        return true;
    }

    std::string renderAscii() const {
        std::string out;
        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                auto k = key(x, y);
                if (px == x && py == y) out += goals.count(k) ? '+' : '@';
                else if (boxes.count(k)) out += goals.count(k) ? '*' : '$';
                else if (walls.count(k)) out += '#';
                else if (goals.count(k)) out += '.';
                else out += ' ';
            }
            out += '\n';
        }
        return out;
    }
};
""",
    )
    write(
        "cppapp1/main.cpp",
        r"""// cppapp1 — C++ 推箱子终端版（教学）
// 编译: g++ -std=c++17 -O2 main.cpp -o sokoban
#include "game.hpp"
#include <iostream>
#include <string>
#include <cctype>

int main() {
    const std::vector<std::string> LEVEL = {
        "#######",
        "#. . .#",
        "# $$$ #",
        "#.$@$.#",
        "# $$$ #",
        "#. . .#",
        "#######",
    };
    auto state = GameState::fromRows(LEVEL, 0);
    std::cout << "sokoban_cpp — wasd 移动, z 撤销, r 重置, q 退出\n";
    while (true) {
        std::cout << "\n" << state.renderAscii();
        std::cout << "moves=" << state.moves << (state.won ? " WIN!" : "") << "\n> ";
        std::string line;
        if (!std::getline(std::cin, line)) break;
        if (line.empty()) continue;
        char ch = static_cast<char>(std::tolower(static_cast<unsigned char>(line[0])));
        if (ch == 'w') state.tryMove(0, -1);
        else if (ch == 's') state.tryMove(0, 1);
        else if (ch == 'a') state.tryMove(-1, 0);
        else if (ch == 'd') state.tryMove(1, 0);
        else if (ch == 'z') state.undo();
        else if (ch == 'r') state = GameState::fromRows(LEVEL, 0);
        else if (ch == 'q') break;
        if (state.won) std::cout << "Level clear!\n";
    }
    return 0;
}
""",
    )
    write(
        "cppapp1/readme.md",
        readme(
            "cppapp1 — C++ 推箱子（教学）",
            "需要 C++17 编译器（g++ / clang++ / MSVC）。",
            "cd cppapp1\ng++ -std=c++17 -O2 main.cpp -o sokoban\n./sokoban",
        ),
    )
    write("cppapp1/CHANGELOG.md", changelog("C++"))


def gen_nim() -> None:
    write(
        "nimapp1/game.nim",
        r"""# 推箱子核心逻辑（Nim 教学）

import std/[sets, strutils, sequtils]

type
  Hist = object
    px, py: int
    boxFrom, boxTo: string
    isPush: bool
  GameState* = object
    walls, goals, boxes: HashSet[string]
    px*, py*: int
    moves*: int
    won*: bool
    width*, height*: int
    hist: seq[Hist]

proc key(x, y: int): string = $x & "," & $y

proc fromRows*(rows: openArray[string], index = 0): GameState =
  var s: GameState
  var maxX, maxY = 0
  for y, row in rows:
    maxY = y
    for x, ch in row:
      if x > maxX: maxX = x
      let k = key(x, y)
      case ch
      of '#': s.walls.incl k
      of '.': s.goals.incl k
      of '$': s.boxes.incl k
      of '*':
        s.boxes.incl k
        s.goals.incl k
      of '@':
        s.px = x; s.py = y
      of '+':
        s.px = x; s.py = y
        s.goals.incl k
      else: discard
  s.width = maxX + 1
  s.height = maxY + 1
  result = s

proc checkWin(s: var GameState) =
  s.won = true
  for b in s.boxes:
    if b notin s.goals:
      s.won = false
      return

proc tryMove*(s: var GameState, dx, dy: int): bool =
  if s.won: return false
  let nx = s.px + dx
  let ny = s.py + dy
  let nk = key(nx, ny)
  if nk in s.walls: return false
  if nk in s.boxes:
    let bx = nx + dx
    let by = ny + dy
    let bk = key(bx, by)
    if bk in s.walls or bk in s.boxes: return false
    s.hist.add Hist(px: s.px, py: s.py, boxFrom: nk, boxTo: bk, isPush: true)
    s.boxes.excl nk
    s.boxes.incl bk
    s.px = nx; s.py = ny
    inc s.moves
    s.checkWin()
    return true
  s.hist.add Hist(px: s.px, py: s.py, isPush: false)
  s.px = nx; s.py = ny
  true

proc undo*(s: var GameState): bool =
  if s.won or s.hist.len == 0: return false
  while s.hist.len > 0:
    let e = s.hist.pop()
    if e.isPush:
      s.px = e.px; s.py = e.py
      s.boxes.excl e.boxTo
      s.boxes.incl e.boxFrom
      if s.moves > 0: dec s.moves
      s.won = false
      return true
    s.px = e.px; s.py = e.py
  true

proc renderAscii*(s: GameState): string =
  for y in 0 ..< s.height:
    for x in 0 ..< s.width:
      let k = key(x, y)
      if s.px == x and s.py == y:
        result.add(if k in s.goals: '+' else: '@')
      elif k in s.boxes:
        result.add(if k in s.goals: '*' else: '$')
      elif k in s.walls:
        result.add '#'
      elif k in s.goals:
        result.add '.'
      else:
        result.add ' '
    result.add '\n'
""",
    )
    write(
        "nimapp1/main.nim",
        r"""# nimapp1 — Nim 推箱子终端版（教学）
# 编译: nim c -d:release main.nim

import std/strutils
import game

const Level = [
  "#######",
  "#. . .#",
  "# $$$ #",
  "#.$@$.#",
  "# $$$ #",
  "#. . .#",
  "#######",
]

var state = fromRows(Level, 0)
echo "sokoban_nim — wasd 移动, z 撤销, r 重置, q 退出"

while true:
  echo()
  stdout.write renderAscii(state)
  let flag = if state.won: " WIN!" else: ""
  stdout.write "moves=" & $state.moves & flag & "\n> "
  stdout.flushFile()
  var line: string
  try:
    line = stdin.readLine()
  except EOFError:
    break
  line = line.strip()
  if line.len == 0: continue
  let ch = line[0].toLowerAscii()
  case ch
  of 'w': discard tryMove(state, 0, -1)
  of 's': discard tryMove(state, 0, 1)
  of 'a': discard tryMove(state, -1, 0)
  of 'd': discard tryMove(state, 1, 0)
  of 'z': discard undo(state)
  of 'r': state = fromRows(Level, 0)
  of 'q': break
  else: discard
  if state.won: echo "Level clear!"
""",
    )
    write(
        "nimapp1/readme.md",
        readme(
            "nimapp1 — Nim 推箱子（教学）",
            "需要 [Nim](https://nim-lang.org/)（`nim`）。",
            "cd nimapp1\nnim c -r -d:release main.nim",
        ),
    )
    write("nimapp1/CHANGELOG.md", changelog("Nim"))


def gen_dart() -> None:
    write(
        "dartapp1/game.dart",
        r"""// 推箱子核心逻辑（Dart 教学）

class Hist {
  final int px, py;
  final String? boxFrom, boxTo;
  Hist(this.px, this.py, [this.boxFrom, this.boxTo]);
}

class GameState {
  final Set<String> walls = {};
  final Set<String> goals = {};
  final Set<String> boxes = {};
  int px = 0, py = 0;
  int moves = 0;
  bool won = false;
  int width = 0, height = 0;
  final List<Hist> hist = [];

  static String key(int x, int y) => '$x,$y';

  static GameState fromRows(List<String> rows, [int index = 0]) {
    final s = GameState();
    var maxX = 0, maxY = 0;
    for (var y = 0; y < rows.length; y++) {
      maxY = y;
      final row = rows[y];
      for (var x = 0; x < row.length; x++) {
        if (x > maxX) maxX = x;
        final ch = row[x];
        final k = key(x, y);
        switch (ch) {
          case '#':
            s.walls.add(k);
            break;
          case '.':
            s.goals.add(k);
            break;
          case r'$':
            s.boxes.add(k);
            break;
          case '*':
            s.boxes.add(k);
            s.goals.add(k);
            break;
          case '@':
            s.px = x;
            s.py = y;
            break;
          case '+':
            s.px = x;
            s.py = y;
            s.goals.add(k);
            break;
        }
      }
    }
    s.width = maxX + 1;
    s.height = maxY + 1;
    return s;
  }

  void checkWin() {
    won = boxes.every((b) => goals.contains(b));
  }

  bool tryMove(int dx, int dy) {
    if (won) return false;
    final nx = px + dx, ny = py + dy;
    final nk = key(nx, ny);
    if (walls.contains(nk)) return false;
    if (boxes.contains(nk)) {
      final bx = nx + dx, by = ny + dy;
      final bk = key(bx, by);
      if (walls.contains(bk) || boxes.contains(bk)) return false;
      hist.add(Hist(px, py, nk, bk));
      boxes.remove(nk);
      boxes.add(bk);
      px = nx;
      py = ny;
      moves++;
      checkWin();
      return true;
    }
    hist.add(Hist(px, py));
    px = nx;
    py = ny;
    return true;
  }

  bool undo() {
    if (won || hist.isEmpty) return false;
    Hist? entry;
    while (hist.isNotEmpty) {
      entry = hist.removeLast();
      if (entry.boxFrom != null) break;
      px = entry.px;
      py = entry.py;
    }
    if (entry == null || entry.boxFrom == null) return true;
    px = entry.px;
    py = entry.py;
    boxes.remove(entry.boxTo);
    boxes.add(entry.boxFrom!);
    if (moves > 0) moves--;
    won = false;
    return true;
  }

  String renderAscii() {
    final sb = StringBuffer();
    for (var y = 0; y < height; y++) {
      for (var x = 0; x < width; x++) {
        final k = key(x, y);
        if (px == x && py == y) {
          sb.write(goals.contains(k) ? '+' : '@');
        } else if (boxes.contains(k)) {
          sb.write(goals.contains(k) ? '*' : r'$');
        } else if (walls.contains(k)) {
          sb.write('#');
        } else if (goals.contains(k)) {
          sb.write('.');
        } else {
          sb.write(' ');
        }
      }
      sb.writeln();
    }
    return sb.toString();
  }
}
""",
    )
    write(
        "dartapp1/main.dart",
        r"""// dartapp1 — Dart 推箱子终端版（教学）
// 运行: dart run main.dart

import 'dart:io';
import 'game.dart';

const level = [
  '#######',
  '#. . .#',
  '# $$$ #',
  '#.$@$.#',
  '# $$$ #',
  '#. . .#',
  '#######',
];

void main() {
  var state = GameState.fromRows(level, 0);
  stdout.writeln('sokoban_dart — wasd 移动, z 撤销, r 重置, q 退出');
  while (true) {
    stdout.writeln();
    stdout.write(state.renderAscii());
    final flag = state.won ? ' WIN!' : '';
    stdout.write('moves=${state.moves}$flag\n> ');
    final line = stdin.readLineSync();
    if (line == null) break;
    final t = line.trim();
    if (t.isEmpty) continue;
    final ch = t[0].toLowerCase();
    switch (ch) {
      case 'w':
        state.tryMove(0, -1);
        break;
      case 's':
        state.tryMove(0, 1);
        break;
      case 'a':
        state.tryMove(-1, 0);
        break;
      case 'd':
        state.tryMove(1, 0);
        break;
      case 'z':
        state.undo();
        break;
      case 'r':
        state = GameState.fromRows(level, 0);
        break;
      case 'q':
        return;
    }
    if (state.won) stdout.writeln('Level clear!');
  }
}
""",
    )
    write(
        "dartapp1/readme.md",
        readme(
            "dartapp1 — Dart 推箱子（教学）",
            "需要 [Dart SDK](https://dart.dev/)（与 Flutter 独立，纯 CLI）。",
            "cd dartapp1\ndart run main.dart",
        ),
    )
    write("dartapp1/CHANGELOG.md", changelog("Dart"))


def main() -> None:
    gen_powershell()
    gen_bash()
    gen_julia()
    gen_groovy()
    gen_cpp()
    gen_nim()
    gen_dart()
    print("done batch A")


if __name__ == "__main__":
    main()
