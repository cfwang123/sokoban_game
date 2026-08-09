#!/usr/bin/env lua
-- luaapp1 — 推箱子终端版（教学）

local game = require("game")

local LEVEL = {
  "#######",
  "#. . .#",
  "# $$$ #",
  "#.$@$.#",
  "# $$$ #",
  "#. . .#",
  "#######",
}

local state = game.from_rows(LEVEL, 0)
io.write("sokoban_lua — wasd 移动, z 撤销, r 重置, q 退出\n")

while true do
  io.write("\n")
  io.write(game.render_ascii(state))
  local flag = state.won and " WIN!" or ""
  io.write(string.format("moves=%d%s\n> ", state.moves, flag))
  local line = io.read("*l")
  if not line then break end
  line = line:match("^%s*(.-)%s*$") or ""
  if line ~= "" then
    local ch = line:sub(1, 1):lower()
    if ch == "w" then
      game.try_move(state, 0, -1)
    elseif ch == "s" then
      game.try_move(state, 0, 1)
    elseif ch == "a" then
      game.try_move(state, -1, 0)
    elseif ch == "d" then
      game.try_move(state, 1, 0)
    elseif ch == "z" then
      game.undo(state)
    elseif ch == "r" then
      state = game.from_rows(LEVEL, 0)
    elseif ch == "q" then
      break
    end
    if state.won then
      io.write("Level clear!\n")
    end
  end
end
