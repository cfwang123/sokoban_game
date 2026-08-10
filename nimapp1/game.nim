# 推箱子核心逻辑（Nim 教学）

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
