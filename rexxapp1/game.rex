/* 推箱子核心逻辑（REXX 教学） */

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
