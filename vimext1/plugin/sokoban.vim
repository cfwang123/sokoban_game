" sokoban.vim — 教学用 Vim 推箱子
" 用法: :Sokoban
if exists('g:loaded_sokoban')
  finish
endif
let g:loaded_sokoban = 1

command! -nargs=0 Sokoban call sokoban#open()
