! 推箱子核心逻辑（Fortran 教学）
module game
  implicit none
  private
  public :: game_state, from_rows, try_move, undo, render_ascii, check_win

  integer, parameter :: MAX_W = 32, MAX_H = 32, MAX_HIST = 1024

  type :: hist_entry
    integer :: px, py
    integer :: bfx, bfy, btx, bty
    logical :: is_push
  end type

  type :: game_state
    character(len=1) :: map(MAX_W, MAX_H)
    integer :: width, height
    integer :: px, py
    integer :: moves
    logical :: won
    integer :: hist_n
    type(hist_entry) :: hist(MAX_HIST)
  end type

contains

  subroutine from_rows(rows, n, s)
    character(len=*), intent(in) :: rows(:)
    integer, intent(in) :: n
    type(game_state), intent(out) :: s
    integer :: y, x, lenr
    character(len=1) :: ch

    s%map = ' '
    s%width = 0
    s%height = n
    s%px = 1
    s%py = 1
    s%moves = 0
    s%won = .false.
    s%hist_n = 0

    do y = 1, n
      lenr = len_trim(rows(y))
      if (lenr > s%width) s%width = lenr
      do x = 1, lenr
        ch = rows(y)(x:x)
        select case (ch)
        case ('#')
          s%map(x, y) = '#'
        case ('.')
          s%map(x, y) = '.'
        case ('$')
          s%map(x, y) = '$'
        case ('*')
          s%map(x, y) = '*'
        case ('@')
          s%map(x, y) = ' '
          s%px = x
          s%py = y
        case ('+')
          s%map(x, y) = '.'
          s%px = x
          s%py = y
        case default
          s%map(x, y) = ' '
        end select
      end do
    end do
  end subroutine from_rows

  subroutine check_win(s)
    type(game_state), intent(inout) :: s
    integer :: x, y
    s%won = .true.
    do y = 1, s%height
      do x = 1, s%width
        if (s%map(x, y) == '$') then
          s%won = .false.
          return
        end if
      end do
    end do
  end subroutine check_win

  logical function try_move(s, dx, dy)
    type(game_state), intent(inout) :: s
    integer, intent(in) :: dx, dy
    integer :: nx, ny, bx, by
    character(len=1) :: ch

    try_move = .false.
    if (s%won) return
    nx = s%px + dx
    ny = s%py + dy
    if (nx < 1 .or. ny < 1 .or. nx > s%width .or. ny > s%height) return
    ch = s%map(nx, ny)
    if (ch == '#') return

    if (ch == '$' .or. ch == '*') then
      bx = nx + dx
      by = ny + dy
      if (bx < 1 .or. by < 1 .or. bx > s%width .or. by > s%height) return
      ch = s%map(bx, by)
      if (ch == '#' .or. ch == '$' .or. ch == '*') return
      if (s%hist_n >= MAX_HIST) return
      s%hist_n = s%hist_n + 1
      s%hist(s%hist_n) = hist_entry(s%px, s%py, nx, ny, bx, by, .true.)
      if (s%map(nx, ny) == '*') then
        s%map(nx, ny) = '.'
      else
        s%map(nx, ny) = ' '
      end if
      if (s%map(bx, by) == '.') then
        s%map(bx, by) = '*'
      else
        s%map(bx, by) = '$'
      end if
      s%px = nx
      s%py = ny
      s%moves = s%moves + 1
      call check_win(s)
      try_move = .true.
      return
    end if

    if (s%hist_n >= MAX_HIST) return
    s%hist_n = s%hist_n + 1
    s%hist(s%hist_n) = hist_entry(s%px, s%py, 0, 0, 0, 0, .false.)
    s%px = nx
    s%py = ny
    try_move = .true.
  end function try_move

  logical function undo(s)
    type(game_state), intent(inout) :: s
    type(hist_entry) :: h
    integer :: nx, ny, bx, by

    undo = .false.
    if (s%won .or. s%hist_n == 0) return
    do while (s%hist_n > 0)
      h = s%hist(s%hist_n)
      s%hist_n = s%hist_n - 1
      if (h%is_push) then
        s%px = h%px
        s%py = h%py
        nx = h%bfx; ny = h%bfy
        bx = h%btx; by = h%bty
        if (s%map(bx, by) == '*') then
          s%map(bx, by) = '.'
        else
          s%map(bx, by) = ' '
        end if
        if (s%map(nx, ny) == '.') then
          s%map(nx, ny) = '*'
        else
          s%map(nx, ny) = '$'
        end if
        if (s%moves > 0) s%moves = s%moves - 1
        s%won = .false.
        undo = .true.
        return
      else
        s%px = h%px
        s%py = h%py
      end if
    end do
    undo = .true.
  end function undo

  subroutine render_ascii(s)
    type(game_state), intent(in) :: s
    integer :: x, y
    character(len=MAX_W) :: line
    character(len=1) :: ch

    do y = 1, s%height
      line = ' '
      do x = 1, s%width
        if (x == s%px .and. y == s%py) then
          if (s%map(x, y) == '.') then
            ch = '+'
          else
            ch = '@'
          end if
        else
          ch = s%map(x, y)
          if (ch == ' ') ch = ' '
        end if
        line(x:x) = ch
      end do
      write(*, '(A)') line(1:s%width)
    end do
  end subroutine render_ascii

end module game
