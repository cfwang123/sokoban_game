-- Neovim Lua 推箱子（教学）
-- 用法: :Sokoban 或 require('sokoban').open()

local M = {}

local levels = {
  { "###", "#@#", "#$#", "#.#", "###" },
  { "#####", "#.$@#", "#####" },
  { "###", "#.###", "#*$-#", "#--@#", "#####" },
}

local state = {
  level = 1,
  moves = 0,
  won = false,
  px = 0,
  py = 0,
  w = 0,
  h = 0,
  walls = {},
  goals = {},
  boxes = {},
  hist = {},
  buf = nil,
  win = nil,
}

local function key(x, y)
  return x .. "," .. y
end

local function parse(rows)
  state.walls, state.goals, state.boxes, state.hist = {}, {}, {}, {}
  state.moves, state.won = 0, false
  state.h = #rows
  state.w = 0
  for y, row in ipairs(rows) do
    if #row > state.w then
      state.w = #row
    end
    for x = 1, #row do
      local ch = row:sub(x, x)
      local k = key(x - 1, y - 1)
      if ch == "#" then
        state.walls[k] = true
      elseif ch == "." then
        state.goals[k] = true
      elseif ch == "$" then
        state.boxes[k] = true
      elseif ch == "*" then
        state.boxes[k] = true
        state.goals[k] = true
      elseif ch == "@" then
        state.px, state.py = x - 1, y - 1
      elseif ch == "+" then
        state.px, state.py = x - 1, y - 1
        state.goals[k] = true
      end
    end
  end
end

local function check_win()
  for k, _ in pairs(state.boxes) do
    if not state.goals[k] then
      state.won = false
      return
    end
  end
  state.won = true
end

local function try_move(dx, dy)
  if state.won then
    return
  end
  local nx, ny = state.px + dx, state.py + dy
  local nk = key(nx, ny)
  if state.walls[nk] then
    return
  end
  if state.boxes[nk] then
    local bk = key(nx + dx, ny + dy)
    if state.walls[bk] or state.boxes[bk] then
      return
    end
    table.insert(state.hist, { px = state.px, py = state.py, from = nk, to = bk, push = true })
    state.boxes[nk] = nil
    state.boxes[bk] = true
    state.px, state.py = nx, ny
    state.moves = state.moves + 1
    check_win()
    return
  end
  table.insert(state.hist, { px = state.px, py = state.py, push = false })
  state.px, state.py = nx, ny
end

local function undo()
  if state.won or #state.hist == 0 then
    return
  end
  local e
  while #state.hist > 0 do
    e = table.remove(state.hist)
    if e.push then
      break
    end
    state.px, state.py = e.px, e.py
  end
  if not e or not e.push then
    return
  end
  state.px, state.py = e.px, e.py
  state.boxes[e.to] = nil
  state.boxes[e.from] = true
  if state.moves > 0 then
    state.moves = state.moves - 1
  end
  state.won = false
end

local function render()
  local lines = {}
  for y = 0, state.h - 1 do
    local chars = {}
    for x = 0, state.w - 1 do
      local k = key(x, y)
      if state.px == x and state.py == y then
        chars[#chars + 1] = state.goals[k] and "+" or "@"
      elseif state.boxes[k] then
        chars[#chars + 1] = state.goals[k] and "*" or "$"
      elseif state.walls[k] then
        chars[#chars + 1] = "#"
      elseif state.goals[k] then
        chars[#chars + 1] = "."
      else
        chars[#chars + 1] = " "
      end
    end
    lines[#lines + 1] = table.concat(chars)
  end
  lines[#lines + 1] = ""
  lines[#lines + 1] = string.format(
    "LV%d/%d  moves:%d%s",
    state.level,
    #levels,
    state.moves,
    state.won and "  WIN!" or ""
  )
  lines[#lines + 1] = "h/j/k/l move | u undo | r reset | n/p level | q quit"
  return lines
end

local function redraw()
  if not state.buf or not vim.api.nvim_buf_is_valid(state.buf) then
    return
  end
  local lines = render()
  vim.bo[state.buf].modifiable = true
  vim.api.nvim_buf_set_lines(state.buf, 0, -1, false, lines)
  vim.bo[state.buf].modifiable = false
end

local function load(i)
  state.level = math.max(1, math.min(#levels, i))
  parse(levels[state.level])
  redraw()
end

local function map(lhs, rhs)
  vim.keymap.set("n", lhs, rhs, { buffer = state.buf, silent = true, nowait = true })
end

function M.open()
  state.buf = vim.api.nvim_create_buf(false, true)
  vim.bo[state.buf].buftype = "nofile"
  vim.bo[state.buf].bufhidden = "wipe"
  vim.bo[state.buf].swapfile = false
  vim.api.nvim_buf_set_name(state.buf, "[Sokoban]")
  vim.cmd("tabnew")
  state.win = vim.api.nvim_get_current_win()
  vim.api.nvim_win_set_buf(state.win, state.buf)

  map("h", function()
    try_move(-1, 0)
    redraw()
  end)
  map("l", function()
    try_move(1, 0)
    redraw()
  end)
  map("k", function()
    try_move(0, -1)
    redraw()
  end)
  map("j", function()
    try_move(0, 1)
    redraw()
  end)
  map("<Left>", function()
    try_move(-1, 0)
    redraw()
  end)
  map("<Right>", function()
    try_move(1, 0)
    redraw()
  end)
  map("<Up>", function()
    try_move(0, -1)
    redraw()
  end)
  map("<Down>", function()
    try_move(0, 1)
    redraw()
  end)
  map("u", function()
    undo()
    redraw()
  end)
  map("r", function()
    load(state.level)
  end)
  map("n", function()
    load(state.level + 1)
  end)
  map("p", function()
    load(state.level - 1)
  end)
  map("q", function()
    vim.cmd("bd!")
  end)

  load(1)
end

return M
