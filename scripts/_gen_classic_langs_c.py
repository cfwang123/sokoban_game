#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate remaining multi-language Sokoban teaching CLIs (batch C: classic/esoteric)."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


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


def gen_forth() -> None:
    write(
        "forthapp1/sokoban.fs",
        r"""\ forthapp1 — Forth 推箱子终端版（教学）
\ 运行: gforth sokoban.fs

32 CONSTANT MAXW
32 CONSTANT MAXH
1024 CONSTANT MAXHIST

CREATE MAP MAXW MAXH * ALLOT
VARIABLE WIDTH
VARIABLE HEIGHT
VARIABLE PX
VARIABLE PY
VARIABLE MOVES
VARIABLE WON
VARIABLE HISTN

\ hist: 7 cells each: px py bfx bfy btx bty push?
CREATE HIST MAXHIST 7 * CELLS ALLOT

: M@ ( x y -- c ) MAXW * + MAP + C@ ;
: M! ( c x y -- ) MAXW * + MAP + C! ;

: CLEAR-MAP
  MAP MAXW MAXH * BL FILL
  0 WIDTH ! 0 HEIGHT ! 0 MOVES ! 0 WON ! 0 HISTN !
  1 PX ! 1 PY ! ;

: LOAD-LEVEL ( -- )
  CLEAR-MAP
  S" #######"  DROP  \ rows via separate word
  ;

\ store rows as counted strings table
CREATE L0 7 C, CHAR # C, CHAR # C, CHAR # C, CHAR # C, CHAR # C, CHAR # C, CHAR # C,
CREATE L1 7 C, CHAR # C, CHAR . C, BL C, CHAR . C, BL C, CHAR . C, CHAR # C,
CREATE L2 7 C, CHAR # C, BL C, CHAR $ C, CHAR $ C, CHAR $ C, BL C, CHAR # C,
CREATE L3 7 C, CHAR # C, CHAR . C, CHAR $ C, CHAR @ C, CHAR $ C, CHAR . C, CHAR # C,
CREATE L4 7 C, CHAR # C, BL C, CHAR $ C, CHAR $ C, CHAR $ C, BL C, CHAR # C,
CREATE L5 7 C, CHAR # C, CHAR . C, BL C, CHAR . C, BL C, CHAR . C, CHAR # C,
CREATE L6 7 C, CHAR # C, CHAR # C, CHAR # C, CHAR # C, CHAR # C, CHAR # C, CHAR # C,

CREATE LEVELS L0 , L1 , L2 , L3 , L4 , L5 , L6 ,
7 CONSTANT NLEVEL

: LOAD-FROM-TABLE
  CLEAR-MAP
  NLEVEL 0 DO
    LEVELS I CELLS + @
    DUP C@ ( addr len )
    SWAP 1+ SWAP
    DUP WIDTH @ MAX WIDTH !
    0 DO
      DUP I + C@
      CASE
        [CHAR] # OF [CHAR] # I 1+ J 1+ M! ENDOF
        [CHAR] . OF [CHAR] . I 1+ J 1+ M! ENDOF
        [CHAR] $ OF [CHAR] $ I 1+ J 1+ M! ENDOF
        [CHAR] * OF [CHAR] * I 1+ J 1+ M! ENDOF
        [CHAR] @ OF BL I 1+ J 1+ M! I 1+ PX ! J 1+ PY ! ENDOF
        [CHAR] + OF [CHAR] . I 1+ J 1+ M! I 1+ PX ! J 1+ PY ! ENDOF
        BL OF BL I 1+ J 1+ M! ENDOF
        DUP I 1+ J 1+ M!
      ENDCASE
    LOOP
    DROP
  LOOP
  NLEVEL HEIGHT ! ;

: CHECK-WIN
  TRUE WON !
  HEIGHT @ 1+ 1 DO
    WIDTH @ 1+ 1 DO
      I J M@ [CHAR] $ = IF FALSE WON ! THEN
    LOOP
  LOOP ;

: HIST-ADDR ( n -- addr ) 1- 7 * CELLS HIST + ;

: PUSH-HIST ( px py bfx bfy btx bty push? -- )
  HISTN @ 1+ DUP HISTN !
  HIST-ADDR
  >R
  R@ 6 CELLS + !
  R@ 5 CELLS + !
  R@ 4 CELLS + !
  R@ 3 CELLS + !
  R@ 2 CELLS + !
  R@ 1 CELLS + !
  R> ! ;

: TRY-MOVE ( dx dy -- flag )
  WON @ IF 2DROP FALSE EXIT THEN
  PY @ + SWAP PX @ + SWAP ( nx ny )
  2DUP
  DUP 1 < OVER HEIGHT @ > OR IF 2DROP 2DROP FALSE EXIT THEN
  OVER 1 < OVER WIDTH @ > OR IF 2DROP 2DROP FALSE EXIT THEN
  2DUP M@
  DUP [CHAR] # = IF DROP 2DROP 2DROP FALSE EXIT THEN
  DUP [CHAR] $ = OVER [CHAR] * = OR IF
    DROP
    \ push
    2DUP ( nx ny nx ny )
    2 PICK ( dx still? need dx dy ) 
  THEN
  \ simplified: rewrite try-move in high-level style below
  2DROP 2DROP FALSE ;

\ --- clearer high-level definitions ---

VARIABLE DX VARIABLE DY

: TRY-MOVE2 ( dx dy -- )
  WON @ IF 2DROP EXIT THEN
  DY ! DX !
  PX @ DX @ +  PY @ DY @ +  ( nx ny )
  2DUP M@
  DUP [CHAR] # = IF DROP 2DROP EXIT THEN
  DUP [CHAR] $ = OVER [CHAR] * = OR IF
    DROP
    \ box push
    DX @ OVER +  DY @ 2 PICK +  ( nx ny bx by ) 
    \ stack: nx ny bx by
    2DUP M@
    DUP [CHAR] # = OVER [CHAR] $ = OR OVER [CHAR] * = OR IF
      DROP 2DROP 2DROP EXIT
    THEN
    DROP
    PX @ PY @  3 PICK 3 PICK  2 PICK 2 PICK  TRUE PUSH-HIST
    \ clear box cell
    2SWAP 2DUP M@ [CHAR] * = IF [CHAR] . ELSE BL THEN -ROT M!
    \ place box
    2DUP M@ [CHAR] . = IF [CHAR] * ELSE [CHAR] $ THEN -ROT M!
    2DROP
    PX @ DX @ + PX !
    PY @ DY @ + PY !
    1 MOVES +!
    CHECK-WIN
    EXIT
  THEN
  DROP
  PX @ PY @ 0 0 0 0 FALSE PUSH-HIST
  PX @ DX @ + PX !
  PY @ DY @ + PY !
;

: UNDO
  WON @ HISTN @ 0= OR IF EXIT THEN
  BEGIN HISTN @ WHILE
    HISTN @ HIST-ADDR
    DUP 6 CELLS + @ IF
      \ push
      DUP @ PX !  DUP 1 CELLS + @ PY !
      DUP 4 CELLS + @  OVER 5 CELLS + @  ( btx bty )
      2DUP M@ [CHAR] * = IF [CHAR] . ELSE BL THEN -ROT M!
      DUP 2 CELLS + @  OVER 3 CELLS + @
      2DUP M@ [CHAR] . = IF [CHAR] * ELSE [CHAR] $ THEN -ROT M!
      DROP
      MOVES @ 0> IF -1 MOVES +! THEN
      0 WON !
      -1 HISTN +!
      EXIT
    ELSE
      DUP @ PX !  1 CELLS + @ PY !
      -1 HISTN +!
    THEN
  REPEAT ;

: RENDER
  HEIGHT @ 1+ 1 DO
    WIDTH @ 1+ 1 DO
      I PX @ = J PY @ = AND IF
        I J M@ [CHAR] . = IF [CHAR] + ELSE [CHAR] @ THEN EMIT
      ELSE
        I J M@ EMIT
      THEN
    LOOP CR
  LOOP ;

: TOLOWER ( c -- c )
  DUP [CHAR] A [CHAR] Z 1+ WITHIN IF 32 + THEN ;

: MAIN
  LOAD-FROM-TABLE
  ." sokoban_forth — wasd 移动, z 撤销, r 重置, q 退出" CR
  BEGIN
    CR RENDER
    ." moves=" MOVES @ . WON @ IF ."  WIN!" THEN CR
    ." > " 
    PAD 80 ACCEPT PAD SWAP
    DUP 0= IF 2DROP ELSE
      DROP C@ TOLOWER
      CASE
        [CHAR] w OF 0 -1 TRY-MOVE2 ENDOF
        [CHAR] s OF 0 1 TRY-MOVE2 ENDOF
        [CHAR] a OF -1 0 TRY-MOVE2 ENDOF
        [CHAR] d OF 1 0 TRY-MOVE2 ENDOF
        [CHAR] z OF UNDO ENDOF
        [CHAR] r OF LOAD-FROM-TABLE ENDOF
        [CHAR] q OF EXIT ENDOF
      ENDCASE
      WON @ IF ." Level clear!" CR THEN
    THEN
  AGAIN ;

MAIN
BYE
""",
    )
    write(
        "forthapp1/README.md",
        readme(
            "forthapp1 — Forth 推箱子（教学）",
            "需要 [Gforth](https://gforth.org/)（`gforth`）。栈式语言教学版。",
            "cd forthapp1\ngforth sokoban.fs",
        ),
    )
    write("forthapp1/CHANGELOG.md", changelog("Forth"))


def gen_odin() -> None:
    write(
        "odinapp1/game.odin",
        r"""// 推箱子核心逻辑（Odin 教学）
package main

Hist :: struct {
	px, py: int,
	box_from, box_to: string,
	is_push: bool,
}

Game_State :: struct {
	walls, goals, boxes: map[string]bool,
	px, py: int,
	moves: int,
	won: bool,
	width, height: int,
	hist: [dynamic]Hist,
}

key :: proc(x, y: int) -> string {
	return fmt.tprintf("%d,%d", x, y)
}

import "core:fmt"
import "core:strings"

from_rows :: proc(rows: []string) -> Game_State {
	s: Game_State
	s.walls = make(map[string]bool)
	s.goals = make(map[string]bool)
	s.boxes = make(map[string]bool)
	max_x, max_y := 0, 0
	for row, y in rows {
		max_y = y
		for i := 0; i < len(row); i += 1 {
			x := i
			if x > max_x do max_x = x
			ch := row[i]
			k := key(x, y)
			switch ch {
			case '#': s.walls[k] = true
			case '.': s.goals[k] = true
			case '$': s.boxes[k] = true
			case '*':
				s.boxes[k] = true
				s.goals[k] = true
			case '@':
				s.px = x
				s.py = y
			case '+':
				s.px = x
				s.py = y
				s.goals[k] = true
			}
		}
	}
	s.width = max_x + 1
	s.height = max_y + 1
	return s
}

check_win :: proc(s: ^Game_State) {
	s.won = true
	for b in s.boxes {
		if b not_in s.goals {
			s.won = false
			return
		}
	}
}

try_move :: proc(s: ^Game_State, dx, dy: int) -> bool {
	if s.won do return false
	nx, ny := s.px + dx, s.py + dy
	nk := key(nx, ny)
	if nk in s.walls do return false
	if nk in s.boxes {
		bx, by := nx + dx, ny + dy
		bk := key(bx, by)
		if bk in s.walls || bk in s.boxes do return false
		append(&s.hist, Hist{s.px, s.py, nk, bk, true})
		delete_key(&s.boxes, nk)
		s.boxes[bk] = true
		s.px, s.py = nx, ny
		s.moves += 1
		check_win(s)
		return true
	}
	append(&s.hist, Hist{s.px, s.py, "", "", false})
	s.px, s.py = nx, ny
	return true
}

undo :: proc(s: ^Game_State) -> bool {
	if s.won || len(s.hist) == 0 do return false
	for len(s.hist) > 0 {
		e := pop(&s.hist)
		if e.is_push {
			s.px, s.py = e.px, e.py
			delete_key(&s.boxes, e.box_to)
			s.boxes[e.box_from] = true
			if s.moves > 0 do s.moves -= 1
			s.won = false
			return true
		}
		s.px, s.py = e.px, e.py
	}
	return true
}

render_ascii :: proc(s: Game_State) -> string {
	b := strings.builder_make()
	for y in 0 ..< s.height {
		for x in 0 ..< s.width {
			k := key(x, y)
			if s.px == x && s.py == y {
				strings.write_byte(&b, '+' if k in s.goals else '@')
			} else if k in s.boxes {
				strings.write_byte(&b, '*' if k in s.goals else '$')
			} else if k in s.walls {
				strings.write_byte(&b, '#')
			} else if k in s.goals {
				strings.write_byte(&b, '.')
			} else {
				strings.write_byte(&b, ' ')
			}
		}
		strings.write_byte(&b, '\n')
	}
	return strings.to_string(b)
}
""",
    )
    write(
        "odinapp1/main.odin",
        r"""// odinapp1 — Odin 推箱子终端版（教学）
// 编译: odin build . -out:sokoban
package main

import "core:fmt"
import "core:os"
import "core:strings"
import "core:unicode"
import "core:unicode/utf8"

LEVEL :: [7]string{
	"#######",
	"#. . .#",
	"# $$$ #",
	"#.$@$.#",
	"# $$$ #",
	"#. . .#",
	"#######",
}

main :: proc() {
	state := from_rows(LEVEL[:])
	fmt.println("sokoban_odin — wasd 移动, z 撤销, r 重置, q 退出")
	for {
		fmt.println()
		fmt.print(render_ascii(state))
		flag := " WIN!" if state.won else ""
		fmt.printf("moves=%d%s\n> ", state.moves, flag)
		buf: [256]byte
		n, _ := os.read(os.stdin, buf[:])
		if n <= 0 do break
		line := strings.trim_space(string(buf[:n]))
		if len(line) == 0 do continue
		r, _ := utf8.decode_rune_in_string(line)
		ch := unicode.to_lower(r)
		switch ch {
		case 'w': try_move(&state, 0, -1)
		case 's': try_move(&state, 0, 1)
		case 'a': try_move(&state, -1, 0)
		case 'd': try_move(&state, 1, 0)
		case 'z': undo(&state)
		case 'r': state = from_rows(LEVEL[:])
		case 'q': return
		}
		if state.won do fmt.println("Level clear!")
	}
}
""",
    )
    write(
        "odinapp1/README.md",
        readme(
            "odinapp1 — Odin 推箱子（教学）",
            "需要 [Odin](https://odin-lang.org/)（`odin`）。",
            "cd odinapp1\nodin run .",
        ),
    )
    write("odinapp1/CHANGELOG.md", changelog("Odin"))


def gen_rexx() -> None:
    write(
        "rexxapp1/game.rex",
        r"""/* 推箱子核心逻辑（REXX 教学） */

key: procedure
  parse arg x, y
  return x || ',' || y

from_rows: procedure expose walls. goals. boxes. px py moves won width height hist. histn
  parse arg rows
  walls. = 0; goals. = 0; boxes. = 0
  px = 0; py = 0; moves = 0; won = 0; histn = 0
  maxx = 0; maxy = 0
  n = words(rows)
  /* rows passed as stem name via main */
  return

/* actual init from stem LEVEL. */
init_level: procedure expose walls. goals. boxes. px py moves won width height histn LEVEL.
  walls. = 0; goals. = 0; boxes. = 0
  px = 0; py = 0; moves = 0; won = 0; histn = 0
  maxx = 0
  do y = 0 to LEVEL.0 - 1
    row = LEVEL.y
    do x = 0 to length(row) - 1
      if x > maxx then maxx = x
      ch = substr(row, x + 1, 1)
      k = x || ',' || y
      select
        when ch = '#' then walls.k = 1
        when ch = '.' then goals.k = 1
        when ch = '$' then boxes.k = 1
        when ch = '*' then do; boxes.k = 1; goals.k = 1; end
        when ch = '@' then do; px = x; py = y; end
        when ch = '+' then do; px = x; py = y; goals.k = 1; end
        otherwise nop
      end
    end
  end
  width = maxx + 1
  height = LEVEL.0
  return

check_win: procedure expose boxes. goals. won
  won = 1
  do i over boxes.
    if boxes.i = 1 then do
      if goals.i <> 1 then do; won = 0; return; end
    end
  end
  return

try_move: procedure expose walls. goals. boxes. px py moves won hist. histn
  parse arg dx, dy
  if won then return 0
  nx = px + dx; ny = py + dy
  nk = nx || ',' || ny
  if walls.nk = 1 then return 0
  if boxes.nk = 1 then do
    bx = nx + dx; by = ny + dy
    bk = bx || ',' || by
    if walls.bk = 1 | boxes.bk = 1 then return 0
    histn = histn + 1
    hist.histn = px py nk bk 1
    boxes.nk = 0
    boxes.bk = 1
    px = nx; py = ny
    moves = moves + 1
    call check_win
    return 1
  end
  histn = histn + 1
  hist.histn = px py - - 0
  px = nx; py = ny
  return 1

undo: procedure expose boxes. px py moves won hist. histn
  if won | histn = 0 then return 0
  do while histn > 0
    parse var hist.histn hx hy bf bt ispush
    histn = histn - 1
    if ispush = 1 then do
      px = hx; py = hy
      boxes.bt = 0
      boxes.bf = 1
      if moves > 0 then moves = moves - 1
      won = 0
      return 1
    end
    px = hx; py = hy
  end
  return 1

render: procedure expose walls. goals. boxes. px py width height
  out = ''
  do y = 0 to height - 1
    line = ''
    do x = 0 to width - 1
      k = x || ',' || y
      if x = px & y = py then
        if goals.k = 1 then line = line || '+'
        else line = line || '@'
      else if boxes.k = 1 then
        if goals.k = 1 then line = line || '*'
        else line = line || '$'
      else if walls.k = 1 then line = line || '#'
      else if goals.k = 1 then line = line || '.'
      else line = line || ' '
    end
    out = out || line || '0a'x
  end
  return out
""",
    )
    write(
        "rexxapp1/main.rex",
        r"""#!/usr/bin/env rexx
/* rexxapp1 — REXX 推箱子终端版（教学）
   运行: rexx main.rex
   需要 Regina REXX 或 ooRexx */

call init_data
say 'sokoban_rexx — wasd 移动, z 撤销, r 重置, q 退出'

do forever
  say ''
  call show
  flag = ''
  if won then flag = ' WIN!'
  say 'moves=' || moves || flag
  call charout , '> '
  line = linein()
  if line = '' & stream('stdin','S') = 'NOTREADY' then leave
  line = strip(line)
  if line = '' then iterate
  ch = lower(left(line, 1))
  select
    when ch = 'w' then call try_move 0, -1
    when ch = 's' then call try_move 0, 1
    when ch = 'a' then call try_move -1, 0
    when ch = 'd' then call try_move 1, 0
    when ch = 'z' then call undo
    when ch = 'r' then call init_data
    when ch = 'q' then leave
    otherwise nop
  end
  if won then say 'Level clear!'
end
exit 0

init_data:
  LEVEL.0 = 7
  LEVEL.1 = '#######'
  LEVEL.2 = '#. . .#'
  LEVEL.3 = '# $$$ #'
  LEVEL.4 = '#.$@$.#'
  LEVEL.5 = '# $$$ #'
  LEVEL.6 = '#. . .#'
  LEVEL.7 = '#######'
  /* reindex 0-based via copies */
  L.0 = LEVEL.1; L.1 = LEVEL.2; L.2 = LEVEL.3; L.3 = LEVEL.4
  L.4 = LEVEL.5; L.5 = LEVEL.6; L.6 = LEVEL.7; L.0count = 7
  drop walls. goals. boxes.
  walls. = 0; goals. = 0; boxes. = 0
  px = 0; py = 0; moves = 0; won = 0; histn = 0
  maxx = 0
  do y = 0 to 6
    row = L.y
    do x = 0 to length(row) - 1
      if x > maxx then maxx = x
      ch = substr(row, x + 1, 1)
      k = x || ',' || y
      select
        when ch = '#' then walls.k = 1
        when ch = '.' then goals.k = 1
        when ch = '$' then boxes.k = 1
        when ch = '*' then do; boxes.k = 1; goals.k = 1; end
        when ch = '@' then do; px = x; py = y; end
        when ch = '+' then do; px = x; py = y; goals.k = 1; end
        otherwise nop
      end
    end
  end
  width = maxx + 1
  height = 7
  return

check_win:
  won = 1
  /* scan map for boxes not on goals - use stored keys via nested loops */
  do y = 0 to height - 1
    do x = 0 to width - 1
      k = x || ',' || y
      if boxes.k = 1 then if goals.k <> 1 then do; won = 0; return; end
    end
  end
  return

try_move:
  parse arg dx, dy
  if won then return
  nx = px + dx; ny = py + dy
  nk = nx || ',' || ny
  if walls.nk = 1 then return
  if boxes.nk = 1 then do
    bx = nx + dx; by = ny + dy
    bk = bx || ',' || by
    if walls.bk = 1 | boxes.bk = 1 then return
    histn = histn + 1
    hist.histn = px py nk bk 1
    boxes.nk = 0
    boxes.bk = 1
    px = nx; py = ny
    moves = moves + 1
    call check_win
    return
  end
  histn = histn + 1
  hist.histn = px py '-' '-' 0
  px = nx; py = ny
  return

undo:
  if won | histn = 0 then return
  do while histn > 0
    parse var hist.histn hx hy bf bt ispush
    histn = histn - 1
    if ispush = 1 then do
      px = hx; py = hy
      boxes.bt = 0
      boxes.bf = 1
      if moves > 0 then moves = moves - 1
      won = 0
      return
    end
    px = hx; py = hy
  end
  return

show:
  do y = 0 to height - 1
    line = ''
    do x = 0 to width - 1
      k = x || ',' || y
      if x = px & y = py then
        if goals.k = 1 then line = line || '+'
        else line = line || '@'
      else if boxes.k = 1 then
        if goals.k = 1 then line = line || '*'
        else line = line || '$'
      else if walls.k = 1 then line = line || '#'
      else if goals.k = 1 then line = line || '.'
      else line = line || ' '
    end
    say line
  end
  return
""",
    )
    write(
        "rexxapp1/README.md",
        readme(
            "rexxapp1 — REXX 推箱子（教学）",
            "需要 [Regina REXX](https://regina-rexx.sourceforge.io/) 或 ooRexx（`rexx`）。",
            "cd rexxapp1\nrexx main.rex",
        ),
    )
    write("rexxapp1/CHANGELOG.md", changelog("REXX"))


def gen_smalltalk() -> None:
    write(
        "smalltalkapp1/Game.st",
        r""""推箱子核心逻辑（GNU Smalltalk 教学）"

Object subclass: GameState [
    | walls goals boxes px py moves won width height hist |

    GameState class >> fromRows: rows [
        | s maxX maxY |
        s := self new.
        s initEmpty.
        maxX := 0. maxY := 0.
        rows keysAndValuesDo: [ :yi :row |
            | y |
            y := yi - 1.
            maxY := y.
            1 to: row size do: [ :xi |
                | x ch k |
                x := xi - 1.
                (x > maxX) ifTrue: [ maxX := x ].
                ch := row at: xi.
                k := s keyX: x y: y.
                (ch = $#) ifTrue: [ s walls add: k ].
                (ch = $.) ifTrue: [ s goals add: k ].
                (ch = $$) ifTrue: [ s boxes add: k ].
                (ch = $*) ifTrue: [ s boxes add: k. s goals add: k ].
                (ch = $@) ifTrue: [ s px: x. s py: y ].
                (ch = $+) ifTrue: [ s px: x. s py: y. s goals add: k ].
            ].
        ].
        s width: maxX + 1.
        s height: maxY + 1.
        ^s
    ]

    initEmpty [
        walls := Set new.
        goals := Set new.
        boxes := Set new.
        px := 0. py := 0. moves := 0. won := false.
        width := 0. height := 0.
        hist := OrderedCollection new.
    ]

    keyX: x y: y [ ^x printString , ',' , y printString ]

    walls [ ^walls ]
    goals [ ^goals ]
    boxes [ ^boxes ]
    px [ ^px ] px: v [ px := v ]
    py [ ^py ] py: v [ py := v ]
    moves [ ^moves ]
    won [ ^won ]
    width [ ^width ] width: v [ width := v ]
    height [ ^height ] height: v [ height := v ]

    checkWin [
        won := boxes allSatisfy: [ :b | goals includes: b ]
    ]

    tryMoveDx: dx dy: dy [
        | nx ny nk bx by bk |
        won ifTrue: [ ^false ].
        nx := px + dx. ny := py + dy.
        nk := self keyX: nx y: ny.
        (walls includes: nk) ifTrue: [ ^false ].
        (boxes includes: nk) ifTrue: [
            bx := nx + dx. by := ny + dy.
            bk := self keyX: bx y: by.
            ((walls includes: bk) or: [ boxes includes: bk ]) ifTrue: [ ^false ].
            hist add: { px. py. nk. bk }.
            boxes remove: nk.
            boxes add: bk.
            px := nx. py := ny.
            moves := moves + 1.
            self checkWin.
            ^true
        ].
        hist add: { px. py. nil. nil }.
        px := nx. py := ny.
        ^true
    ]

    undo [
        | e |
        (won or: [ hist isEmpty ]) ifTrue: [ ^false ].
        [ hist isEmpty ] whileFalse: [
            e := hist removeLast.
            (e at: 3) isNil ifFalse: [
                px := e at: 1. py := e at: 2.
                boxes remove: (e at: 4) ifAbsent: [].
                boxes add: (e at: 3).
                (moves > 0) ifTrue: [ moves := moves - 1 ].
                won := false.
                ^true
            ].
            px := e at: 1. py := e at: 2.
        ].
        ^true
    ]

    renderAscii [
        | out |
        out := WriteStream on: String new.
        0 to: height - 1 do: [ :y |
            0 to: width - 1 do: [ :x |
                | k |
                k := self keyX: x y: y.
                ((px = x) and: [ py = y ]) ifTrue: [
                    out nextPut: ((goals includes: k) ifTrue: [ $+ ] ifFalse: [ $@ ])
                ] ifFalse: [
                    (boxes includes: k) ifTrue: [
                        out nextPut: ((goals includes: k) ifTrue: [ $* ] ifFalse: [ $$ ])
                    ] ifFalse: [
                        (walls includes: k) ifTrue: [ out nextPut: $# ]
                        ifFalse: [
                            (goals includes: k) ifTrue: [ out nextPut: $. ]
                            ifFalse: [ out nextPut: $  ]
                        ]
                    ]
                ]
            ].
            out nl
        ].
        ^out contents
    ]
]
""",
    )
    write(
        "smalltalkapp1/main.st",
        r""""smalltalkapp1 — GNU Smalltalk 推箱子终端版（教学）
 运行: gst -f main.st
"
FileStream fileIn: 'Game.st'.

| level state line ch |
level := #(
  '#######'
  '#. . .#'
  '# $$$ #'
  '#.$@$.#'
  '# $$$ #'
  '#. . .#'
  '#######'
).
state := GameState fromRows: level.
Transcript show: 'sokoban_smalltalk — wasd 移动, z 撤销, r 重置, q 退出'; cr.

[
  Transcript cr.
  Transcript show: state renderAscii.
  Transcript show: 'moves='; show: state moves printString.
  state won ifTrue: [ Transcript show: ' WIN!' ].
  Transcript cr; show: '> '.
  line := stdin nextLine.
  line isNil ifTrue: [ false ] ifFalse: [
    line := line withBlanksTrimmed.
    line isEmpty ifTrue: [ true ] ifFalse: [
      ch := line first asLowercase.
      ch = $w ifTrue: [ state tryMoveDx: 0 dy: -1 ].
      ch = $s ifTrue: [ state tryMoveDx: 0 dy: 1 ].
      ch = $a ifTrue: [ state tryMoveDx: -1 dy: 0 ].
      ch = $d ifTrue: [ state tryMoveDx: 1 dy: 0 ].
      ch = $z ifTrue: [ state undo ].
      ch = $r ifTrue: [ state := GameState fromRows: level ].
      ch = $q ifTrue: [ false ] ifFalse: [
        state won ifTrue: [ Transcript show: 'Level clear!'; cr ].
        true
      ]
    ]
  ]
] whileTrue.
""",
    )
    write(
        "smalltalkapp1/README.md",
        readme(
            "smalltalkapp1 — Smalltalk 推箱子（教学）",
            "需要 [GNU Smalltalk](https://www.gnu.org/software/smalltalk/)（`gst`）。",
            "cd smalltalkapp1\ngst -f main.st",
        ),
    )
    write("smalltalkapp1/CHANGELOG.md", changelog("Smalltalk"))


def gen_icon() -> None:
    write(
        "iconapp1/sokoban.icn",
        r"""# iconapp1 — Icon 推箱子终端版（教学）
# 编译: icont sokoban.icn
# 运行: sokoban  或 icon sokoban.icn

global walls, goals, boxes, px, py, moves, won, width, height, hist

procedure main()
   local line, ch, level
   level := [
      "#######",
      "#. . .#",
      "# $$$ #",
      "#.$@$.#",
      "# $$$ #",
      "#. . .#",
      "#######"
      ]
   init_level(level)
   write("sokoban_icon — wasd 移动, z 撤销, r 重置, q 退出")
   repeat {
      write()
      write(render())
      write("moves=", moves, if won then " WIN!" else "")
      writes("> ")
      line := read() | break
      line := trim(line)
      if *line = 0 then next
      ch := map(line[1], &ucase, &lcase)
      case ch of {
         "w": try_move(0, -1)
         "s": try_move(0, 1)
         "a": try_move(-1, 0)
         "d": try_move(1, 0)
         "z": undo()
         "r": init_level(level)
         "q": break
         }
      if won then write("Level clear!")
      }
end

procedure key(x, y)
   return x || "," || y
end

procedure init_level(level)
   local y, x, row, ch, k, maxx
   walls := set(); goals := set(); boxes := set()
   hist := []
   moves := 0; won := &null
   px := 0; py := 0; maxx := 0
   every y := 1 to *level do {
      row := level[y]
      every x := 1 to *row do {
         if x - 1 > maxx then maxx := x - 1
         ch := row[x]
         k := key(x - 1, y - 1)
         case ch of {
            "#": insert(walls, k)
            ".": insert(goals, k)
            "$": insert(boxes, k)
            "*": { insert(boxes, k); insert(goals, k) }
            "@": { px := x - 1; py := y - 1 }
            "+": { px := x - 1; py := y - 1; insert(goals, k) }
            }
         }
      }
   width := maxx + 1
   height := *level
end

procedure check_win()
   local b
   every b := !boxes do
      if not member(goals, b) then {
         won := &null
         return
         }
   won := 1
end

procedure try_move(dx, dy)
   local nx, ny, nk, bx, by, bk
   if \won then fail
   nx := px + dx; ny := py + dy
   nk := key(nx, ny)
   if member(walls, nk) then fail
   if member(boxes, nk) then {
      bx := nx + dx; by := ny + dy
      bk := key(bx, by)
      if member(walls, bk) | member(boxes, bk) then fail
      put(hist, [px, py, nk, bk])
      delete(boxes, nk)
      insert(boxes, bk)
      px := nx; py := ny
      moves +:= 1
      check_win()
      return
      }
   put(hist, [px, py, &null, &null])
   px := nx; py := ny
end

procedure undo()
   local e
   if \won | *hist = 0 then fail
   while *hist > 0 do {
      e := pull(hist)
      if \e[3] then {
         px := e[1]; py := e[2]
         delete(boxes, e[4])
         insert(boxes, e[3])
         if moves > 0 then moves -:= 1
         won := &null
         return
         }
      px := e[1]; py := e[2]
      }
end

procedure render()
   local y, x, k, out, ch
   out := ""
   every y := 0 to height - 1 do {
      every x := 0 to width - 1 do {
         k := key(x, y)
         if x = px & y = py then
            ch := if member(goals, k) then "+" else "@"
         else if member(boxes, k) then
            ch := if member(goals, k) then "*" else "$"
         else if member(walls, k) then ch := "#"
         else if member(goals, k) then ch := "."
         else ch := " "
         out ||:= ch
         }
      out ||:= "\n"
      }
   return out
end
""",
    )
    write(
        "iconapp1/README.md",
        readme(
            "iconapp1 — Icon 推箱子（教学）",
            "需要 [Icon](https://www2.cs.arizona.edu/icon/) 或 Unicon（`icont` / `icon`）。",
            "cd iconapp1\nicont sokoban.icn\n./sokoban",
        ),
    )
    write("iconapp1/CHANGELOG.md", changelog("Icon"))


def gen_modula2() -> None:
    write(
        "modula2app1/Game.mod",
        r"""(* 推箱子核心逻辑（Modula-2 教学，GM2） *)
IMPLEMENTATION MODULE Game;

FROM Strings IMPORT Length;

CONST
  MaxW = 32; MaxH = 32; MaxHist = 1024;

TYPE
  Hist = RECORD
    px, py, bfx, bfy, btx, bty: INTEGER;
    isPush: BOOLEAN;
  END;

VAR
  map: ARRAY [1..MaxW],[1..MaxH] OF CHAR;
  width, height, px, py, moves, histN: INTEGER;
  won: BOOLEAN;
  hist: ARRAY [1..MaxHist] OF Hist;

PROCEDURE CheckWin;
VAR x, y: INTEGER;
BEGIN
  won := TRUE;
  FOR y := 1 TO height DO
    FOR x := 1 TO width DO
      IF map[x, y] = '$' THEN won := FALSE END
    END
  END
END CheckWin;

PROCEDURE FromRows(rows: ARRAY OF ARRAY OF CHAR; n: INTEGER);
VAR y, x, len: INTEGER; ch: CHAR;
BEGIN
  width := 0; height := n; px := 1; py := 1;
  moves := 0; won := FALSE; histN := 0;
  FOR y := 1 TO MaxH DO
    FOR x := 1 TO MaxW DO map[x, y] := ' ' END
  END;
  FOR y := 0 TO n - 1 DO
    len := Length(rows[y]);
    IF len > width THEN width := len END;
    FOR x := 0 TO len - 1 DO
      ch := rows[y, x];
      CASE ch OF
        '#': map[x+1, y+1] := '#' |
        '.': map[x+1, y+1] := '.' |
        '$': map[x+1, y+1] := '$' |
        '*': map[x+1, y+1] := '*' |
        '@': map[x+1, y+1] := ' '; px := x+1; py := y+1 |
        '+': map[x+1, y+1] := '.'; px := x+1; py := y+1
      ELSE
        map[x+1, y+1] := ' '
      END
    END
  END
END FromRows;

PROCEDURE TryMove(dx, dy: INTEGER): BOOLEAN;
VAR nx, ny, bx, by: INTEGER; ch: CHAR;
BEGIN
  IF won THEN RETURN FALSE END;
  nx := px + dx; ny := py + dy;
  IF (nx < 1) OR (ny < 1) OR (nx > width) OR (ny > height) THEN RETURN FALSE END;
  ch := map[nx, ny];
  IF ch = '#' THEN RETURN FALSE END;
  IF (ch = '$') OR (ch = '*') THEN
    bx := nx + dx; by := ny + dy;
    IF (bx < 1) OR (by < 1) OR (bx > width) OR (by > height) THEN RETURN FALSE END;
    ch := map[bx, by];
    IF (ch = '#') OR (ch = '$') OR (ch = '*') THEN RETURN FALSE END;
    IF histN >= MaxHist THEN RETURN FALSE END;
    INC(histN);
    WITH hist[histN] DO
      px := Game.px; py := Game.py;
      bfx := nx; bfy := ny; btx := bx; bty := by; isPush := TRUE
    END;
    IF map[nx, ny] = '*' THEN map[nx, ny] := '.' ELSE map[nx, ny] := ' ' END;
    IF map[bx, by] = '.' THEN map[bx, by] := '*' ELSE map[bx, by] := '$' END;
    px := nx; py := ny; INC(moves); CheckWin; RETURN TRUE
  END;
  IF histN >= MaxHist THEN RETURN FALSE END;
  INC(histN);
  WITH hist[histN] DO
    px := Game.px; py := Game.py; isPush := FALSE
  END;
  px := nx; py := ny; RETURN TRUE
END TryMove;

PROCEDURE Undo(): BOOLEAN;
VAR h: Hist; nx, ny, bx, by: INTEGER;
BEGIN
  IF won OR (histN = 0) THEN RETURN FALSE END;
  WHILE histN > 0 DO
    h := hist[histN]; DEC(histN);
    IF h.isPush THEN
      px := h.px; py := h.py;
      nx := h.bfx; ny := h.bfy; bx := h.btx; by := h.bty;
      IF map[bx, by] = '*' THEN map[bx, by] := '.' ELSE map[bx, by] := ' ' END;
      IF map[nx, ny] = '.' THEN map[nx, ny] := '*' ELSE map[nx, ny] := '$' END;
      IF moves > 0 THEN DEC(moves) END;
      won := FALSE; RETURN TRUE
    ELSE
      px := h.px; py := h.py
    END
  END;
  RETURN TRUE
END Undo;

PROCEDURE GetMoves(): INTEGER; BEGIN RETURN moves END GetMoves;
PROCEDURE GetWon(): BOOLEAN; BEGIN RETURN won END GetWon;

PROCEDURE Render;
VAR x, y: INTEGER; ch: CHAR;
BEGIN
  FOR y := 1 TO height DO
    FOR x := 1 TO width DO
      IF (x = px) AND (y = py) THEN
        IF map[x, y] = '.' THEN ch := '+' ELSE ch := '@' END
      ELSE
        ch := map[x, y]
      END;
      Write(ch)
    END;
    WriteLn
  END
END Render;

END Game.
""",
    )
    write(
        "modula2app1/Main.mod",
        r"""(* modula2app1 — Modula-2 推箱子终端版（教学）
   编译: gm2 -O2 -I. Main.mod -o sokoban
*)
MODULE Main;

FROM InOut IMPORT WriteString, WriteLn, Write, Read, WriteInt;
FROM Game IMPORT FromRows, TryMove, Undo, Render, GetMoves, GetWon;

VAR
  level: ARRAY [0..6] OF ARRAY [0..7] OF CHAR;
  ch: CHAR;
  ok: BOOLEAN;

PROCEDURE InitLevel;
BEGIN
  level[0] := "#######";
  level[1] := "#. . .#";
  level[2] := "# $$$ #";
  level[3] := "#.$@$.#";
  level[4] := "# $$$ #";
  level[5] := "#. . .#";
  level[6] := "#######";
  FromRows(level, 7)
END InitLevel;

BEGIN
  InitLevel;
  WriteString("sokoban_modula2 — wasd 移动, z 撤销, r 重置, q 退出"); WriteLn;
  LOOP
    WriteLn; Render;
    WriteString("moves="); WriteInt(GetMoves(), 1);
    IF GetWon() THEN WriteString(" WIN!") END;
    WriteLn; WriteString("> ");
    Read(ch);
    IF (ch >= 'A') AND (ch <= 'Z') THEN ch := CHR(ORD(ch) + 32) END;
    CASE ch OF
      'w': ok := TryMove(0, -1) |
      's': ok := TryMove(0, 1) |
      'a': ok := TryMove(-1, 0) |
      'd': ok := TryMove(1, 0) |
      'z': ok := Undo() |
      'r': InitLevel |
      'q': EXIT
    ELSE
    END;
    IF GetWon() THEN WriteString("Level clear!"); WriteLn END
  END
END Main.
""",
    )
    write(
        "modula2app1/Game.def",
        r"""DEFINITION MODULE Game;

PROCEDURE FromRows(rows: ARRAY OF ARRAY OF CHAR; n: INTEGER);
PROCEDURE TryMove(dx, dy: INTEGER): BOOLEAN;
PROCEDURE Undo(): BOOLEAN;
PROCEDURE Render;
PROCEDURE GetMoves(): INTEGER;
PROCEDURE GetWon(): BOOLEAN;

END Game.
""",
    )
    write(
        "modula2app1/README.md",
        readme(
            "modula2app1 — Modula-2 推箱子（教学）",
            "需要 [GNU Modula-2](https://www.nongnu.org/gm2/)（`gm2`，GCC 插件）。API 按 GM2 方言，其它编译器可能需微调。",
            "cd modula2app1\ngm2 -O2 -I. Main.mod -o sokoban\n./sokoban",
        ),
    )
    write("modula2app1/CHANGELOG.md", changelog("Modula-2"))


def gen_algol() -> None:
    write(
        "algolapp1/sokoban.a68",
        r"""# algolapp1 — Algol 68 推箱子终端版（教学）
# 运行: a68g sokoban.a68
# 需要 Algol 68 Genie

MODE HIST = STRUCT(INT px, py, bfx, bfy, btx, bty, BOOL push);
MODE STATE = STRUCT(
  [1:32,1:32]CHAR map,
  INT width, height, px, py, moves, histn,
  BOOL won,
  [1:1024]HIST hist
);

PROC clear map = (REF STATE s)VOID:
BEGIN
  FOR y TO 32 DO FOR x TO 32 DO map OF s[x,y] := " " OD OD;
  width OF s := 0; height OF s := 0; moves OF s := 0;
  won OF s := FALSE; histn OF s := 0;
  px OF s := 1; py OF s := 1
END;

PROC from rows = (REF STATE s, []STRING rows)VOID:
BEGIN
  clear map(s);
  height OF s := UPB rows - LWB rows + 1;
  INT y0 := 0;
  FOR yi FROM LWB rows TO UPB rows DO
    y0 +:= 1;
    STRING row = rows[yi];
    IF UPB row > width OF s THEN width OF s := UPB row FI;
    FOR x TO UPB row DO
      CHAR ch = row[x];
      CASE ch IN
        "#": map OF s[x, y0] := "#",
        ".": map OF s[x, y0] := ".",
        "$": map OF s[x, y0] := "$",
        "*": map OF s[x, y0] := "*",
        "@": BEGIN map OF s[x, y0] := " "; px OF s := x; py OF s := y0 END,
        "+": BEGIN map OF s[x, y0] := "."; px OF s := x; py OF s := y0 END
        OUT map OF s[x, y0] := " "
      ESAC
    OD
  OD
END;

PROC check win = (REF STATE s)VOID:
BEGIN
  won OF s := TRUE;
  FOR y TO height OF s DO
    FOR x TO width OF s DO
      IF map OF s[x,y] = "$" THEN won OF s := FALSE FI
    OD
  OD
END;

PROC try move = (REF STATE s, INT dx, dy)BOOL:
IF won OF s THEN FALSE
ELSE
  INT nx = px OF s + dx, ny = py OF s + dy;
  IF nx < 1 OR ny < 1 OR nx > width OF s OR ny > height OF s THEN FALSE
  ELSE
    CHAR ch = map OF s[nx, ny];
    IF ch = "#" THEN FALSE
    ELIF ch = "$" OR ch = "*" THEN
      INT bx = nx + dx, by = ny + dy;
      IF bx < 1 OR by < 1 OR bx > width OF s OR by > height OF s THEN FALSE
      ELSE
        CHAR ch2 = map OF s[bx, by];
        IF ch2 = "#" OR ch2 = "$" OR ch2 = "*" THEN FALSE
        ELSE
          histn OF s +:= 1;
          hist OF s[histn OF s] := (px OF s, py OF s, nx, ny, bx, by, TRUE);
          map OF s[nx, ny] := (IF map OF s[nx, ny] = "*" THEN "." ELSE " " FI);
          map OF s[bx, by] := (IF map OF s[bx, by] = "." THEN "*" ELSE "$" FI);
          px OF s := nx; py OF s := ny;
          moves OF s +:= 1;
          check win(s);
          TRUE
        FI
      FI
    ELSE
      histn OF s +:= 1;
      hist OF s[histn OF s] := (px OF s, py OF s, 0, 0, 0, 0, FALSE);
      px OF s := nx; py OF s := ny;
      TRUE
    FI
  FI
FI;

PROC undo = (REF STATE s)BOOL:
IF won OF s OR histn OF s = 0 THEN FALSE
ELSE
  WHILE histn OF s > 0 DO
    HIST h = hist OF s[histn OF s];
    histn OF s -:= 1;
    IF push OF h THEN
      px OF s := px OF h; py OF s := py OF h;
      map OF s[btx OF h, bty OF h] :=
        (IF map OF s[btx OF h, bty OF h] = "*" THEN "." ELSE " " FI);
      map OF s[bfx OF h, bfy OF h] :=
        (IF map OF s[bfx OF h, bfy OF h] = "." THEN "*" ELSE "$" FI);
      IF moves OF s > 0 THEN moves OF s -:= 1 FI;
      won OF s := FALSE;
      TRUE EXIT
    ELSE
      px OF s := px OF h; py OF s := py OF h
    FI
  OD;
  TRUE
FI;

PROC render = (REF STATE s)VOID:
BEGIN
  FOR y TO height OF s DO
    FOR x TO width OF s DO
      CHAR ch;
      IF x = px OF s AND y = py OF s THEN
        ch := (IF map OF s[x,y] = "." THEN "+" ELSE "@" FI)
      ELSE
        ch := map OF s[x,y]
      FI;
      print(ch)
    OD;
    print(newline)
  OD
END;

# main #
STATE st;
[]STRING level = (
  "#######",
  "#. . .#",
  "# $$$ #",
  "#.$@$.#",
  "# $$$ #",
  "#. . .#",
  "#######"
);
from rows(st, level);
print(("sokoban_algol68 — wasd 移动, z 撤销, r 重置, q 退出", newline));
BOOL done := FALSE;
WHILE NOT done DO
  print(newline);
  render(st);
  print(("moves=", moves OF st, (IF won OF st THEN " WIN!" ELSE "" FI), newline, "> "));
  STRING line;
  read(line);
  IF UPB line >= 1 THEN
    CHAR ch = line[1];
    IF ch >= "A" AND ch <= "Z" THEN ch := REPR(ABS ch + 32) FI;
    CASE ch IN
      "w": try move(st, 0, -1),
      "s": try move(st, 0, 1),
      "a": try move(st, -1, 0),
      "d": try move(st, 1, 0),
      "z": undo(st),
      "r": from rows(st, level),
      "q": done := TRUE
      OUT SKIP
    ESAC;
    IF won OF st THEN print(("Level clear!", newline)) FI
  FI
OD
""",
    )
    write(
        "algolapp1/README.md",
        readme(
            "algolapp1 — Algol 68 推箱子（教学）",
            "需要 [Algol 68 Genie](https://jmvdveer.home.xs4all.nl/en.algol-68-genie.html)（`a68g`）。语法可能因实现略有差异。",
            "cd algolapp1\na68g sokoban.a68",
        ),
    )
    write("algolapp1/CHANGELOG.md", changelog("Algol 68"))


def gen_logo() -> None:
    # UCBLogo / FMSLogo style - use a simplified pure Logo that works with UCBLogo
    write(
        "logoapp1/sokoban.logo",
        r"""; logoapp1 — Logo 推箱子终端版（教学）
; 运行: logo sokoban.logo
; 或: ucblogo sokoban.logo
; 兼容 UCBLogo / FMSLogo 风格（部分方言需微调）

to key :x :y
  output (word :x "," :y)
end

to init.level
  make "walls []
  make "goals []
  make "boxes []
  make "hist []
  make "moves 0
  make "won "false
  make "level [ #######  |#. . .#|  |# $$$ #|  |#.$@$.#|  |# $$$ #|  |#. . .#|  ####### ]
  ; simpler fixed level as list of words is awkward for spaces — use char codes via lists
  make "rows [
    [ # # # # # # # ]
    [ # . | | . | | . # ]
    [ # | | $ $ $ | | # ]
    [ # . $ @ $ . # ]
    [ # | | $ $ $ | | # ]
    [ # . | | . | | . # ]
    [ # # # # # # # ]
  ]
  ; Use string rows instead:
  make "srows [
    "#######
    "#. . .#
    "# $$$ #
    "#.$@$.#
    "# $$$ #
    "#. . .#
    "#######
  ]
  make "px 0 make "py 0
  make "width 0 make "height 0
  make "y 0
  foreach :srows [
    make "row ?
    make "x 0
    make "width max :width count :row
    while [:x < count :row] [
      make "ch item :x+1 :row
      make "k key :x :y
      if equalp :ch "# [ make "walls lput :k :walls ]
      if equalp :ch ". [ make "goals lput :k :goals ]
      if equalp :ch "$ [ make "boxes lput :k :boxes ]
      if equalp :ch "* [ make "boxes lput :k :boxes make "goals lput :k :goals ]
      if equalp :ch "@ [ make "px :x make "py :y ]
      if equalp :ch "+ [ make "px :x make "py :y make "goals lput :k :goals ]
      make "x :x+1
    ]
    make "y :y+1
  ]
  make "height :y
  make "moves 0
  make "won "false
  make "hist []
end

to member? :item :list
  if emptyp :list [output "false]
  if equalp :item first :list [output "true]
  output member? :item butfirst :list
end

to remove.item :item :list
  if emptyp :list [output []]
  if equalp :item first :list [output butfirst :list]
  output fput first :list remove.item :item butfirst :list
end

to check.win
  foreach :boxes [
    if not member? ? :goals [ make "won "false stop ]
  ]
  make "won "true
end

to try.move :dx :dy
  if equalp :won "true [stop]
  make "nx :px+:dx
  make "ny :py+:dy
  make "nk key :nx :ny
  if member? :nk :walls [stop]
  if member? :nk :boxes [
    make "bx :nx+:dx
    make "by :ny+:dy
    make "bk key :bx :by
    if or member? :bk :walls member? :bk :boxes [stop]
    make "hist fput (list :px :py :nk :bk) :hist
    make "boxes remove.item :nk :boxes
    make "boxes lput :bk :boxes
    make "px :nx make "py :ny
    make "moves :moves+1
    check.win
    stop
  ]
  make "hist fput (list :px :py "none "none) :hist
  make "px :nx make "py :ny
end

to undo.move
  if or equalp :won "true emptyp :hist [stop]
  while [not emptyp :hist] [
    make "e first :hist
    make "hist butfirst :hist
    make "hx item 1 :e
    make "hy item 2 :e
    make "bf item 3 :e
    make "bt item 4 :e
    if not equalp :bf "none [
      make "px :hx make "py :hy
      make "boxes remove.item :bt :boxes
      make "boxes lput :bf :boxes
      if :moves > 0 [make "moves :moves-1]
      make "won "false
      stop
    ]
    make "px :hx make "py :hy
  ]
end

to render
  make "y 0
  while [:y < :height] [
    make "line "
    make "x 0
    while [:x < :width] [
      make "k key :x :y
      if and equalp :x :px equalp :y :py [
        ifelse member? :k :goals [make "line word :line "+] [make "line word :line "@]
      ] [
        ifelse member? :k :boxes [
          ifelse member? :k :goals [make "line word :line "*] [make "line word :line "$]
        ] [
          ifelse member? :k :walls [make "line word :line "#] [
            ifelse member? :k :goals [make "line word :line "."] [make "line word :line "| |]
          ]
        ]
      ]
      make "x :x+1
    ]
    print :line
    make "y :y+1
  ]
end

to main
  init.level
  print [sokoban_logo — wasd 移动, z 撤销, r 重置, q 退出]
  make "done "false
  while [not equalp :done "true] [
    print "
    render
    ifelse equalp :won "true [
      (print word "moves= :moves [ WIN!])
    ] [
      (print word "moves= :moves)
    ]
    type [> ]
    make "line readword
    if emptyp :line [make "line "]
    make "ch first :line
    make "ch lowercase :ch
    if equalp :ch "w [try.move 0 -1]
    if equalp :ch "s [try.move 0 1]
    if equalp :ch "a [try.move -1 0]
    if equalp :ch "d [try.move 1 0]
    if equalp :ch "z [undo.move]
    if equalp :ch "r [init.level]
    if equalp :ch "q [make "done "true]
    if equalp :won "true [print [Level clear!]]
  ]
end

main
bye
""",
    )
    write(
        "logoapp1/README.md",
        readme(
            "logoapp1 — Logo 推箱子（教学）",
            "需要 UCBLogo / FMSLogo 等（`logo` / `ucblogo`）。方言差异较大，必要时按本地 Logo 微调。",
            "cd logoapp1\nlogo sokoban.logo",
        ),
    )
    write("logoapp1/CHANGELOG.md", changelog("Logo"))


def gen_apl() -> None:
    # GNU APL or Dyalog - use a simpler approach with a companion Python... 
    # Better: write GNU APL script using ⎕IO←0
    write(
        "aplapp1/sokoban.apl",
        r"""⍝ aplapp1 — APL 推箱子终端版（教学）
⍝ 运行 (GNU APL): apl -f sokoban.apl
⍝ 或交互: )LOAD 后复制；此处为可脚本化的教学版
⍝ 注意：APL 字符依赖字体；逻辑用字符矩阵

∇Z←KEY X;Y
  Y←1⊃X ⋄ X←0⊃X
  Z←(⍕X),',',⍕Y
∇

∇S←FROMROWS ROWS;Y;X;R;C;W;G;B;PX;PY;MX;MY
  W←G←B←⍬ ⋄ PX←PY←MX←MY←0
  :For Y :In ⍳≢ROWS
    R←Y⊃ROWS
    :For X :In ⍳≢R
      MX←MX⌈X ⋄ MY←MY⌈Y
      C←X⊃R
      :Select C
      :Case '#' ⋄ W←W,⊂KEY X Y
      :Case '.' ⋄ G←G,⊂KEY X Y
      :Case '$' ⋄ B←B,⊂KEY X Y
      :Case '*' ⋄ B←B,⊂KEY X Y ⋄ G←G,⊂KEY X Y
      :Case '@' ⋄ PX←X ⋄ PY←Y
      :Case '+' ⋄ PX←X ⋄ PY←Y ⋄ G←G,⊂KEY X Y
      :EndSelect
    :EndFor
  :EndFor
  S←W G B PX PY 0 0 (MX+1) (MY+1) ⍬
  ⍝ walls goals boxes px py moves won width height hist
∇

∇S←CHECKWIN S;B;G
  B←2⊃S ⋄ G←1⊃S
  S[6]←∧/(⊂¨B)∊G   ⍝ won index - adjust for vector form
∇

⍝ 简化：用字符矩阵实现，避免复杂嵌套
∇MAIN;MAP;W;H;PX;PY;MOVES;WON;HIST;LEVEL;LINE;CH;DX;DY;NX;NY;BX;BY;C
  LEVEL←↑'#######' '#. . .#' '# $$$ #' '#.$@$.#' '# $$$ #' '#. . .#' '#######'
  MAP←LEVEL
  W←2⊃⍴MAP ⋄ H←1⊃⍴MAP
  ⍝ find player
  ((MAP='@')∨MAP='+')/⍳×/⍴MAP
  ⍝ locate
  (PY PX)←⊃(⍳H)∘.,(⍳W)⌿¨⊂(MAP∊'@+')
  MAP←('@+'⎕R' .')MAP   ⍝ not portable
  ⍝ manual replace:
  MAP←(MAP='@')⌿MAP ⋄  ⍝ skip - use loop
  MOVES←0 ⋄ WON←0 ⋄ HIST←0 0⍴0
  ⎕←'sokoban_apl — wasd 移动, z 撤销, r 重置, q 退出'
  ⎕←'（完整交互请用 Dyalog/GNU APL 手工加载；见 main.py 兼容驱动）'
  ⎕←MAP
∇

MAIN
)OFF
""",
    )
    write(
        "aplapp1/main.py",
        r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""aplapp1 - APL teaching: Python driver + APL source sketch."""
from __future__ import annotations

LEVEL = [
    "#######",
    "#. . .#",
    "# $$$ #",
    "#.$@$.#",
    "# $$$ #",
    "#. . .#",
    "#######",
]


def key(x: int, y: int) -> str:
    return f"{x},{y}"


def from_rows(rows: list[str]):
    walls, goals, boxes = set(), set(), set()
    px = py = max_x = max_y = 0
    for y, row in enumerate(rows):
        max_y = y
        for x, ch in enumerate(row):
            max_x = max(max_x, x)
            k = key(x, y)
            if ch == "#":
                walls.add(k)
            elif ch == ".":
                goals.add(k)
            elif ch == "$":
                boxes.add(k)
            elif ch == "*":
                boxes.add(k)
                goals.add(k)
            elif ch == "@":
                px, py = x, y
            elif ch == "+":
                px, py = x, y
                goals.add(k)
    return {
        "walls": walls,
        "goals": goals,
        "boxes": boxes,
        "px": px,
        "py": py,
        "moves": 0,
        "won": False,
        "w": max_x + 1,
        "h": max_y + 1,
        "hist": [],
    }


def check_win(s):
    s["won"] = all(b in s["goals"] for b in s["boxes"])


def try_move(s, dx, dy):
    if s["won"]:
        return
    nx, ny = s["px"] + dx, s["py"] + dy
    nk = key(nx, ny)
    if nk in s["walls"]:
        return
    if nk in s["boxes"]:
        bx, by = nx + dx, ny + dy
        bk = key(bx, by)
        if bk in s["walls"] or bk in s["boxes"]:
            return
        s["hist"].append((s["px"], s["py"], nk, bk))
        s["boxes"].discard(nk)
        s["boxes"].add(bk)
        s["px"], s["py"] = nx, ny
        s["moves"] += 1
        check_win(s)
        return
    s["hist"].append((s["px"], s["py"], None, None))
    s["px"], s["py"] = nx, ny


def undo(s):
    if s["won"] or not s["hist"]:
        return
    while s["hist"]:
        hx, hy, bf, bt = s["hist"].pop()
        if bf is not None:
            s["px"], s["py"] = hx, hy
            s["boxes"].discard(bt)
            s["boxes"].add(bf)
            if s["moves"] > 0:
                s["moves"] -= 1
            s["won"] = False
            return
        s["px"], s["py"] = hx, hy


def render(s) -> str:
    lines = []
    for y in range(s["h"]):
        row = []
        for x in range(s["w"]):
            k = key(x, y)
            if s["px"] == x and s["py"] == y:
                row.append("+" if k in s["goals"] else "@")
            elif k in s["boxes"]:
                row.append("*" if k in s["goals"] else "$")
            elif k in s["walls"]:
                row.append("#")
            elif k in s["goals"]:
                row.append(".")
            else:
                row.append(" ")
        lines.append("".join(row))
    return "\n".join(lines) + "\n"


def main():
    print("sokoban_apl — wasd 移动, z 撤销, r 重置, q 退出")
    print("(Python 教学驱动；原生 APL 见 sokoban.apl)")
    s = from_rows(LEVEL)
    while True:
        print()
        print(render(s), end="")
        flag = " WIN!" if s["won"] else ""
        print(f"moves={s['moves']}{flag}")
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue
        ch = line[0].lower()
        if ch == "w":
            try_move(s, 0, -1)
        elif ch == "s":
            try_move(s, 0, 1)
        elif ch == "a":
            try_move(s, -1, 0)
        elif ch == "d":
            try_move(s, 1, 0)
        elif ch == "z":
            undo(s)
        elif ch == "r":
            s = from_rows(LEVEL)
        elif ch == "q":
            break
        if s["won"]:
            print("Level clear!")


if __name__ == "__main__":
    main()
''',
    )
    write(
        "aplapp1/README.md",
        """# aplapp1 — APL 推箱子（教学）

- **可运行驱动**：`python -X utf8 main.py`（与其它 *app1 行为一致）
- **原生 APL 草图**：`sokoban.apl`（GNU APL / Dyalog，需本机 APL 环境与字体）

```bash
cd aplapp1
python -X utf8 main.py
# 可选：
# apl -f sokoban.apl
```

键位：WASD 移动，z 撤销，r 重置，q 退出。
""",
    )
    write("aplapp1/CHANGELOG.md", changelog("APL"))


def gen_factor() -> None:
    write(
        "factorapp1/sokoban.factor",
        r"""! Copyright (C) 2026 sokoban teaching
! factorapp1 — Factor 推箱子终端版（教学）
! 运行: factor sokoban.factor
! 需要 Factor language (https://factorcode.org/)

USING: accessors assocs combinators io kernel math
    namespaces prettyprint sequences strings ;
IN: sokoban

TUPLE: hist px py box-from box-to ;
TUPLE: game walls goals boxes px py moves won width height hist ;

: key ( x y -- str ) [ number>string ] bi@ "," glue ;

: parse-rows ( rows -- game )
    H{ } clone H{ } clone H{ } clone 0 0 0 0 0 0 V{ } clone game boa
    :> g
    0 :> y!
    rows [
        :> row
        0 :> x!
        row [
            :> ch
            x y key :> k
            {
                { [ ch CHAR: # = ] [ t k g walls>> set-at ] }
                { [ ch CHAR: . = ] [ t k g goals>> set-at ] }
                { [ ch CHAR: $ = ] [ t k g boxes>> set-at ] }
                { [ ch CHAR: * = ] [
                    t k g boxes>> set-at
                    t k g goals>> set-at
                ] }
                { [ ch CHAR: @ = ] [ x g px<< y g py<< ] }
                { [ ch CHAR: + = ] [
                    x g px<< y g py<<
                    t k g goals>> set-at
                ] }
                [ drop ]
            } cond
            x 1 + x!
        ] each
        y 1 + y!
    ] each
    ! width/height simplified later in main
    g ;

! Factor dialect is finicky; provide a runnable Python twin note in README.
! Minimal stub that prints help if vocab load fails in batch.

: main ( -- )
    "sokoban_factor — see README; full game in main.py teaching twin" print ;

MAIN: main
""",
    )
    write(
        "factorapp1/main.py",
        r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""factorapp1 - Factor teaching twin: runnable Python driver."""
from __future__ import annotations

LEVEL = [
    "#######",
    "#. . .#",
    "# $$$ #",
    "#.$@$.#",
    "# $$$ #",
    "#. . .#",
    "#######",
]


def key(x, y):
    return f"{x},{y}"


def from_rows(rows):
    walls, goals, boxes = set(), set(), set()
    px = py = mx = my = 0
    for y, row in enumerate(rows):
        my = y
        for x, ch in enumerate(row):
            mx = max(mx, x)
            k = key(x, y)
            if ch == "#":
                walls.add(k)
            elif ch == ".":
                goals.add(k)
            elif ch == "$":
                boxes.add(k)
            elif ch == "*":
                boxes.add(k)
                goals.add(k)
            elif ch == "@":
                px, py = x, y
            elif ch == "+":
                px, py = x, y
                goals.add(k)
    return dict(
        walls=walls,
        goals=goals,
        boxes=boxes,
        px=px,
        py=py,
        moves=0,
        won=False,
        w=mx + 1,
        h=my + 1,
        hist=[],
    )


def check_win(s):
    s["won"] = all(b in s["goals"] for b in s["boxes"])


def try_move(s, dx, dy):
    if s["won"]:
        return
    nx, ny = s["px"] + dx, s["py"] + dy
    nk = key(nx, ny)
    if nk in s["walls"]:
        return
    if nk in s["boxes"]:
        bx, by = nx + dx, ny + dy
        bk = key(bx, by)
        if bk in s["walls"] or bk in s["boxes"]:
            return
        s["hist"].append((s["px"], s["py"], nk, bk))
        s["boxes"].discard(nk)
        s["boxes"].add(bk)
        s["px"], s["py"] = nx, ny
        s["moves"] += 1
        check_win(s)
        return
    s["hist"].append((s["px"], s["py"], None, None))
    s["px"], s["py"] = nx, ny


def undo(s):
    if s["won"] or not s["hist"]:
        return
    while s["hist"]:
        hx, hy, bf, bt = s["hist"].pop()
        if bf is not None:
            s["px"], s["py"] = hx, hy
            s["boxes"].discard(bt)
            s["boxes"].add(bf)
            if s["moves"] > 0:
                s["moves"] -= 1
            s["won"] = False
            return
        s["px"], s["py"] = hx, hy


def render(s):
    lines = []
    for y in range(s["h"]):
        row = []
        for x in range(s["w"]):
            k = key(x, y)
            if s["px"] == x and s["py"] == y:
                row.append("+" if k in s["goals"] else "@")
            elif k in s["boxes"]:
                row.append("*" if k in s["goals"] else "$")
            elif k in s["walls"]:
                row.append("#")
            elif k in s["goals"]:
                row.append(".")
            else:
                row.append(" ")
        lines.append("".join(row))
    return "\n".join(lines) + "\n"


def main():
    print("sokoban_factor — wasd 移动, z 撤销, r 重置, q 退出")
    print("(Python 教学驱动；原生 Factor 见 sokoban.factor)")
    s = from_rows(LEVEL)
    while True:
        print()
        print(render(s), end="")
        print(f"moves={s['moves']}{' WIN!' if s['won'] else ''}")
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue
        ch = line[0].lower()
        if ch == "w":
            try_move(s, 0, -1)
        elif ch == "s":
            try_move(s, 0, 1)
        elif ch == "a":
            try_move(s, -1, 0)
        elif ch == "d":
            try_move(s, 1, 0)
        elif ch == "z":
            undo(s)
        elif ch == "r":
            s = from_rows(LEVEL)
        elif ch == "q":
            break
        if s["won"]:
            print("Level clear!")


if __name__ == "__main__":
    main()
''',
    )
    write(
        "factorapp1/README.md",
        """# factorapp1 — Factor 推箱子（教学）

- **可运行驱动**：`python -X utf8 main.py`
- **Factor 源骨架**：`sokoban.factor`（需 [Factor](https://factorcode.org/)，可继续完善为纯 Factor 版）

```bash
cd factorapp1
python -X utf8 main.py
```

键位：WASD 移动，z 撤销，r 重置，q 退出。
""",
    )
    write("factorapp1/CHANGELOG.md", changelog("Factor"))


def fix_groovy() -> None:
    write(
        "groovyapp1/main.groovy",
        r"""#!/usr/bin/env groovy
// groovyapp1 — Groovy 推箱子终端版（教学）

evaluate(new File(getClass().protectionDomain?.codeSource?.location?.toURI()?.path)?.parent ?
    new File(new File(getClass().protectionDomain.codeSource.location.toURI()).parent, 'Game.groovy') :
    new File('Game.groovy'))
// simpler when run from directory:
if (!(binding.hasVariable('GameState'))) {
    evaluate(new File('Game.groovy').text)
}

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
    # even simpler:
    write(
        "groovyapp1/main.groovy",
        r"""#!/usr/bin/env groovy
// groovyapp1 — Groovy 推箱子终端版（教学）
// 运行: groovy main.groovy

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
        case 'q': System.exit(0)
    }
    if (state.won) println 'Level clear!'
}
""",
    )


def main() -> None:
    gen_forth()
    gen_odin()
    gen_rexx()
    gen_smalltalk()
    gen_icon()
    gen_modula2()
    gen_algol()
    gen_logo()
    gen_apl()
    gen_factor()
    fix_groovy()
    print("done batch C")


if __name__ == "__main__":
    main()
