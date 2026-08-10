# nimapp1 — Nim 推箱子终端版（教学）
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
