; try_move_z80.asm — full sk_try_move (Z80 teaching)
;
; Convention (sjasmplus / similar):
;   HL = SkGame*
;   B  = dx, C = dy   (signed 8-bit)
;   A  = 1 success / 0 fail
; Field layout matches game.h; uses low bytes of int32 coords.

        PUBLIC  sk_try_move

        SECTION code

sk_try_move:
        ld      (game_ptr), hl
        ld      a, b
        ld      (v_dx), a
        ld      a, c
        ld      (v_dy), a

        ld      hl, (game_ptr)
        ld      de, 1044
        add     hl, de
        ld      a, (hl)
        or      a
        jp      nz, fail

        ld      hl, (game_ptr)
        ld      de, 1032
        add     hl, de
        ld      a, (hl)
        ld      b, a
        ld      a, (v_dx)
        add     a, b
        ld      (v_nx), a

        ld      hl, (game_ptr)
        ld      de, 1036
        add     hl, de
        ld      a, (hl)
        ld      b, a
        ld      a, (v_dy)
        add     a, b
        ld      (v_ny), a

        ld      a, (v_nx)
        ld      b, a
        ld      a, (v_ny)
        ld      c, a
        call    at_cell
        cp      '#'
        jp      z, fail
        cp      '$'
        jr      z, do_push
        cp      '*'
        jr      z, do_push

        call    hist_is_full
        jp      c, fail
        xor     a
        call    hist_write
        ld      a, (v_nx)
        call    set_px
        ld      a, (v_ny)
        call    set_py
        ld      a, 1
        ret

do_push:
        ld      a, (v_nx)
        ld      b, a
        ld      a, (v_dx)
        add     a, b
        ld      (v_bx), a
        ld      a, (v_ny)
        ld      b, a
        ld      a, (v_dy)
        add     a, b
        ld      (v_by), a

        ld      a, (v_bx)
        ld      b, a
        ld      a, (v_by)
        ld      c, a
        call    at_cell
        cp      '#'
        jp      z, fail
        cp      '$'
        jp      z, fail
        cp      '*'
        jp      z, fail
        call    hist_is_full
        jp      c, fail

        ld      a, 1
        call    hist_write

        ld      a, (v_nx)
        ld      b, a
        ld      a, (v_ny)
        ld      c, a
        call    at_cell
        cp      '*'
        ld      a, '.'
        jr      z, .c1
        ld      a, ' '
.c1:    ld      e, a
        ld      a, (v_nx)
        ld      b, a
        ld      a, (v_ny)
        ld      c, a
        ld      a, e
        call    set_cell

        ld      a, (v_bx)
        ld      b, a
        ld      a, (v_by)
        ld      c, a
        call    at_cell
        cp      '.'
        ld      a, '*'
        jr      z, .c2
        ld      a, '$'
.c2:    ld      e, a
        ld      a, (v_bx)
        ld      b, a
        ld      a, (v_by)
        ld      c, a
        ld      a, e
        call    set_cell

        ld      a, (v_nx)
        call    set_px
        ld      a, (v_ny)
        call    set_py
        ld      hl, (game_ptr)
        ld      de, 1040
        add     hl, de
        inc     (hl)
        call    check_win
        ld      a, 1
        ret

fail:   xor     a
        ret

; B=x C=y → A
at_cell:
        bit     7, b
        jr      nz, wall
        bit     7, c
        jr      nz, wall
        ld      hl, (game_ptr)
        ld      de, 1024
        add     hl, de
        ld      a, b
        cp      (hl)
        jr      nc, wall
        ld      hl, (game_ptr)
        ld      de, 1028
        add     hl, de
        ld      a, c
        cp      (hl)
        jr      nc, wall
        ld      h, 0
        ld      l, c
        add     hl, hl
        add     hl, hl
        add     hl, hl
        add     hl, hl
        add     hl, hl
        ld      e, b
        ld      d, 0
        add     hl, de
        ld      de, (game_ptr)
        add     hl, de
        ld      a, (hl)
        ret
wall:   ld      a, '#'
        ret

; B=x C=y A=char
set_cell:
        push    af
        ld      h, 0
        ld      l, c
        add     hl, hl
        add     hl, hl
        add     hl, hl
        add     hl, hl
        add     hl, hl
        ld      e, b
        ld      d, 0
        add     hl, de
        ld      de, (game_ptr)
        add     hl, de
        pop     af
        ld      (hl), a
        ret

set_px: ld      hl, (game_ptr)
        ld      de, 1032
        add     hl, de
        ld      (hl), a
        ret

set_py: ld      hl, (game_ptr)
        ld      de, 1036
        add     hl, de
        ld      (hl), a
        ret

; CF=1 if hist full (n >= 255)
hist_is_full:
        ld      hl, (game_ptr)
        ld      de, 1048
        add     hl, de
        ld      a, (hl)
        cp      255
        ccf                             ; if A<255 C=1 → CCF → C=0 ok; if A>=255 C=0 → C=1 full
        ret

; A = is_push
hist_write:
        ld      (v_push), a
        ld      hl, (game_ptr)
        ld      de, 1052
        add     hl, de
        push    hl
        ld      hl, (game_ptr)
        ld      de, 1048
        add     hl, de
        ld      a, (hl)
        ld      e, a
        ld      d, 0
        ld      l, e
        ld      h, d
        add     hl, hl
        add     hl, hl
        add     hl, hl
        add     hl, hl
        add     hl, hl                  ; *32
        push    hl
        ld      l, e
        ld      h, d
        add     hl, hl
        add     hl, hl                  ; *4
        pop     de
        ex      de, hl
        or      a
        sbc     hl, de                  ; *28
        pop     de
        add     hl, de                  ; entry

        push    hl
        ld      hl, (game_ptr)
        ld      de, 1032
        add     hl, de
        ld      a, (hl)
        pop     hl
        call    st_i32
        push    hl
        ld      hl, (game_ptr)
        ld      de, 1036
        add     hl, de
        ld      a, (hl)
        pop     hl
        call    st_i32
        ld      a, (v_nx)
        call    st_i32
        ld      a, (v_ny)
        call    st_i32
        ld      a, (v_bx)
        call    st_i32
        ld      a, (v_by)
        call    st_i32
        ld      a, (v_push)
        ld      (hl), a

        ld      hl, (game_ptr)
        ld      de, 1048
        add     hl, de
        inc     (hl)
        ret

st_i32: ld      (hl), a
        inc     hl
        ld      (hl), 0
        inc     hl
        ld      (hl), 0
        inc     hl
        ld      (hl), 0
        inc     hl
        ret

check_win:
        ld      hl, (game_ptr)
        ld      de, 1044
        add     hl, de
        ld      (hl), 1
        ld      c, 0
.cy:    ld      hl, (game_ptr)
        ld      de, 1028
        add     hl, de
        ld      a, c
        cp      (hl)
        ret     nc
        ld      b, 0
.cx:    ld      hl, (game_ptr)
        ld      de, 1024
        add     hl, de
        ld      a, b
        cp      (hl)
        jr      nc, .nx
        push    bc
        call    at_cell
        pop     bc
        cp      '$'
        jr      nz, .n1
        ld      hl, (game_ptr)
        ld      de, 1044
        add     hl, de
        ld      (hl), 0
.n1:    inc     b
        jr      .cx
.nx:    inc     c
        jr      .cy

        SECTION bss
game_ptr:   dw 0
v_dx:       db 0
v_dy:       db 0
v_nx:       db 0
v_ny:       db 0
v_bx:       db 0
v_by:       db 0
v_push:     db 0
