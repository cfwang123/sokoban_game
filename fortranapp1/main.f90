! fortranapp1 — Fortran 推箱子终端版（教学）
! 编译: gfortran -O2 game.f90 main.f90 -o sokoban
program main
  use game
  implicit none
  type(game_state) :: state
  character(len=64) :: level(7)
  character(len=80) :: line
  character(len=1) :: ch
  character(len=8) :: flag
  integer :: ios
  logical :: ok

  level = [ character(len=64) :: &
    '#######', &
    '#. . .#', &
    '# $$$ #', &
    '#.$@$.#', &
    '# $$$ #', &
    '#. . .#', &
    '#######' ]

  call from_rows(level, 7, state)
  write(*, '(A)') 'sokoban_fortran — wasd 移动, z 撤销, r 重置, q 退出'

  do
    write(*, '(A)') ''
    call render_ascii(state)
    if (state%won) then
      flag = ' WIN!'
    else
      flag = ''
    end if
    write(*, '(A,I0,A)') 'moves=', state%moves, trim(flag)
    write(*, '(A)', advance='no') '> '
    read(*, '(A)', iostat=ios) line
    if (ios /= 0) exit
    line = adjustl(line)
    if (len_trim(line) == 0) cycle
    ch = line(1:1)
    if (ch >= 'A' .and. ch <= 'Z') ch = achar(iachar(ch) + 32)
    select case (ch)
    case ('w')
      ok = try_move(state, 0, -1)
    case ('s')
      ok = try_move(state, 0, 1)
    case ('a')
      ok = try_move(state, -1, 0)
    case ('d')
      ok = try_move(state, 1, 0)
    case ('z')
      ok = undo(state)
    case ('r')
      call from_rows(level, 7, state)
    case ('q')
      exit
    end select
    if (state%won) write(*, '(A)') 'Level clear!'
  end do
end program main
