-- 推箱子核心逻辑（Lua 教学）

local M = {}

local function key(x, y)
  return x .. "," .. y
end

function M.from_rows(rows, index)
  local s = {
    walls = {},
    goals = {},
    boxes = {},
    player = { x = 0, y = 0 },
    moves = 0,
    won = false,
    width = 0,
    height = 0,
    level_index = index or 0,
    hist = {},
  }
  local max_x, max_y = 0, 0
  for y, row in ipairs(rows) do
    y = y - 1 -- 0-based
    max_y = y
    for x = 1, #row do
      local ch = row:sub(x, x)
      local xi = x - 1
      if xi > max_x then max_x = xi end
      local k = key(xi, y)
      if ch == "#" then
        s.walls[k] = true
      elseif ch == "." then
        s.goals[k] = true
      elseif ch == "$" then
        s.boxes[k] = true
      elseif ch == "*" then
        s.boxes[k] = true
        s.goals[k] = true
      elseif ch == "@" then
        s.player = { x = xi, y = y }
      elseif ch == "+" then
        s.player = { x = xi, y = y }
        s.goals[k] = true
      end
    end
  end
  s.width = max_x + 1
  s.height = max_y + 1
  return s
end

local function check_win(s)
  for b, _ in pairs(s.boxes) do
    if not s.goals[b] then
      s.won = false
      return
    end
  end
  s.won = true
end

function M.try_move(s, dx, dy)
  if s.won then return false end
  local nx = s.player.x + dx
  local ny = s.player.y + dy
  local nk = key(nx, ny)
  if s.walls[nk] then return false end
  if s.boxes[nk] then
    local bx = nx + dx
    local by = ny + dy
    local bk = key(bx, by)
    if s.walls[bk] or s.boxes[bk] then return false end
    s.hist[#s.hist + 1] = {
      player = { x = s.player.x, y = s.player.y },
      box_from = nk,
      box_to = bk,
    }
    s.boxes[nk] = nil
    s.boxes[bk] = true
    s.player.x, s.player.y = nx, ny
    s.moves = s.moves + 1
    check_win(s)
    return true
  end
  s.hist[#s.hist + 1] = {
    player = { x = s.player.x, y = s.player.y },
  }
  s.player.x, s.player.y = nx, ny
  return true
end

function M.undo(s)
  if s.won or #s.hist == 0 then return false end
  local entry
  while #s.hist > 0 do
    entry = table.remove(s.hist)
    if entry.box_from then break end
    s.player = entry.player
  end
  if not entry or not entry.box_from then return true end
  s.player = entry.player
  s.boxes[entry.box_to] = nil
  s.boxes[entry.box_from] = true
  if s.moves > 0 then s.moves = s.moves - 1 end
  s.won = false
  return true
end

function M.render_ascii(s)
  local lines = {}
  for y = 0, s.height - 1 do
    local row = {}
    for x = 0, s.width - 1 do
      local k = key(x, y)
      local ch
      if s.player.x == x and s.player.y == y then
        ch = s.goals[k] and "+" or "@"
      elseif s.boxes[k] then
        ch = s.goals[k] and "*" or "$"
      elseif s.walls[k] then
        ch = "#"
      elseif s.goals[k] then
        ch = "."
      else
        ch = " "
      end
      row[#row + 1] = ch
    end
    lines[#lines + 1] = table.concat(row)
  end
  return table.concat(lines, "\n") .. "\n"
end

return M
