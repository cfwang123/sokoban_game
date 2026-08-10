#!/usr/bin/env rexx
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
