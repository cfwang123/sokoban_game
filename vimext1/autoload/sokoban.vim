" autoload/sokoban.vim — 推箱子逻辑与缓冲 UI（Vimscript）

let s:levels = [
      \ ['###', '#@#', '#$#', '#.#', '###'],
      \ ['#####', '#.$@#', '#####'],
      \ ['###', '#.###', '#*$-#', '#--@#', '#####'],
      \ ]

let s:level = 0
let s:moves = 0
let s:won = 0
let s:px = 0
let s:py = 0
let s:w = 0
let s:h = 0
" maps as dicts string key 'x,y' -> 1
let s:walls = {}
let s:goals = {}
let s:boxes = {}
let s:hist = []

function! s:key(x, y) abort
  return a:x . ',' . a:y
endfunction

function! s:parse(rows) abort
  let s:walls = {}
  let s:goals = {}
  let s:boxes = {}
  let s:hist = []
  let s:moves = 0
  let s:won = 0
  let s:w = 0
  let s:h = len(a:rows)
  let y = 0
  while y < s:h
    let row = a:rows[y]
    let x = 0
    while x < len(row)
      if x + 1 > s:w | let s:w = x + 1 | endif
      let ch = row[x]
      let k = s:key(x, y)
      if ch ==# '#'
        let s:walls[k] = 1
      elseif ch ==# '.'
        let s:goals[k] = 1
      elseif ch ==# '$'
        let s:boxes[k] = 1
      elseif ch ==# '*'
        let s:boxes[k] = 1
        let s:goals[k] = 1
      elseif ch ==# '@'
        let s:px = x
        let s:py = y
      elseif ch ==# '+'
        let s:px = x
        let s:py = y
        let s:goals[k] = 1
      endif
      let x += 1
    endwhile
    let y += 1
  endwhile
endfunction

function! s:check_win() abort
  for k in keys(s:boxes)
    if !has_key(s:goals, k)
      let s:won = 0
      return
    endif
  endfor
  let s:won = 1
endfunction

function! s:try_move(dx, dy) abort
  if s:won | return | endif
  let nx = s:px + a:dx
  let ny = s:py + a:dy
  let nk = s:key(nx, ny)
  if has_key(s:walls, nk) | return | endif
  if has_key(s:boxes, nk)
    let bk = s:key(nx + a:dx, ny + a:dy)
    if has_key(s:walls, bk) || has_key(s:boxes, bk) | return | endif
    call add(s:hist, {'px': s:px, 'py': s:py, 'from': nk, 'to': bk, 'push': 1})
    call remove(s:boxes, nk)
    let s:boxes[bk] = 1
    let s:px = nx
    let s:py = ny
    let s:moves += 1
    call s:check_win()
    return
  endif
  call add(s:hist, {'px': s:px, 'py': s:py, 'push': 0})
  let s:px = nx
  let s:py = ny
endfunction

function! s:undo() abort
  if s:won || empty(s:hist) | return | endif
  let e = {}
  while !empty(s:hist)
    let e = remove(s:hist, -1)
    if get(e, 'push', 0)
      break
    endif
    let s:px = e.px
    let s:py = e.py
  endwhile
  if !get(e, 'push', 0) | return | endif
  let s:px = e.px
  let s:py = e.py
  call remove(s:boxes, e.to)
  let s:boxes[e.from] = 1
  if s:moves > 0 | let s:moves -= 1 | endif
  let s:won = 0
endfunction

function! s:render() abort
  let lines = []
  let y = 0
  while y < s:h
    let chars = []
    let x = 0
    while x < s:w
      let k = s:key(x, y)
      if s:px == x && s:py == y
        call add(chars, has_key(s:goals, k) ? '+' : '@')
      elseif has_key(s:boxes, k)
        call add(chars, has_key(s:goals, k) ? '*' : '$')
      elseif has_key(s:walls, k)
        call add(chars, '#')
      elseif has_key(s:goals, k)
        call add(chars, '.')
      else
        call add(chars, ' ')
      endif
      let x += 1
    endwhile
    call add(lines, join(chars, ''))
    let y += 1
  endwhile
  call add(lines, '')
  call add(lines, printf('LV%d/%d  moves:%d%s', s:level + 1, len(s:levels), s:moves, s:won ? '  WIN!' : ''))
  call add(lines, 'h/j/k/l or arrows move | u undo | r reset | n/p level | q quit')
  return lines
endfunction

function! s:redraw() abort
  setlocal modifiable
  call setline(1, s:render())
  if line('$') > len(s:render())
    silent! execute (len(s:render()) + 1) . ',$delete _'
  endif
  setlocal nomodifiable
  redraw
endfunction

function! s:load(i) abort
  let s:level = a:i
  if s:level < 0 | let s:level = 0 | endif
  if s:level >= len(s:levels) | let s:level = len(s:levels) - 1 | endif
  call s:parse(s:levels[s:level])
  call s:redraw()
endfunction

function! s:map_keys() abort
  nnoremap <silent><buffer> h :<C-u>call <SID>move(-1,0)<CR>
  nnoremap <silent><buffer> l :<C-u>call <SID>move(1,0)<CR>
  nnoremap <silent><buffer> k :<C-u>call <SID>move(0,-1)<CR>
  nnoremap <silent><buffer> j :<C-u>call <SID>move(0,1)<CR>
  nnoremap <silent><buffer> <Left> :<C-u>call <SID>move(-1,0)<CR>
  nnoremap <silent><buffer> <Right> :<C-u>call <SID>move(1,0)<CR>
  nnoremap <silent><buffer> <Up> :<C-u>call <SID>move(0,-1)<CR>
  nnoremap <silent><buffer> <Down> :<C-u>call <SID>move(0,1)<CR>
  nnoremap <silent><buffer> u :<C-u>call <SID>do_undo()<CR>
  nnoremap <silent><buffer> r :<C-u>call <SID>load(s:level)<CR>
  nnoremap <silent><buffer> n :<C-u>call <SID>load(s:level+1)<CR>
  nnoremap <silent><buffer> p :<C-u>call <SID>load(s:level-1)<CR>
  nnoremap <silent><buffer> q :<C-u>bd!<CR>
endfunction

function! s:move(dx, dy) abort
  call s:try_move(a:dx, a:dy)
  call s:redraw()
endfunction

function! s:do_undo() abort
  call s:undo()
  call s:redraw()
endfunction

function! sokoban#open() abort
  tabnew
  setlocal buftype=nofile bufhidden=wipe noswapfile nobuflisted
  setlocal nonumber norelativenumber nolist
  file [Sokoban]
  call s:map_keys()
  call s:load(0)
endfunction
