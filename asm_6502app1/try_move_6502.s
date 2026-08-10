; try_move_6502.s — full sk_try_move (ca65 / 65C02 teaching)
;
; Entry:  A = dx, X = dy (signed 8-bit)
;         zero-page game_ptr → SkGame (same layout as game.h)
; Return: A = 1 / 0
; Import: .importzp game_ptr

        .export sk_try_move
        .export sk_try_move_6502
        .importzp game_ptr

        .zeropage
tmp0:   .res 1
tmp1:   .res 1
tmp2:   .res 1
v_dx:   .res 1
v_dy:   .res 1
v_nx:   .res 1
v_ny:   .res 1
v_bx:   .res 1
v_by:   .res 1
v_ch:   .res 1
v_push: .res 1
ptr:    .res 2

        .code

sk_try_move_6502:
sk_try_move:
        sta     v_dx
        stx     v_dy

        lda     #<(1044)
        ldx     #>(1044)
        jsr     load_u8
        bne     fail

        lda     #<(1032)
        ldx     #>(1032)
        jsr     load_u8
        clc
        adc     v_dx
        sta     v_nx
        lda     #<(1036)
        ldx     #>(1036)
        jsr     load_u8
        clc
        adc     v_dy
        sta     v_ny

        lda     v_nx
        ldx     v_ny
        jsr     at_cell
        sta     v_ch
        cmp     #'#'
        beq     fail
        cmp     #'$'
        beq     do_push
        cmp     #'*'
        beq     do_push

        jsr     hist_full
        bcs     fail
        lda     #0
        sta     v_push
        jsr     hist_write
        lda     v_nx
        jsr     store_px
        lda     v_ny
        jsr     store_py
        lda     #1
        rts

do_push:
        lda     v_nx
        clc
        adc     v_dx
        sta     v_bx
        lda     v_ny
        clc
        adc     v_dy
        sta     v_by
        lda     v_bx
        ldx     v_by
        jsr     at_cell
        cmp     #'#'
        beq     fail
        cmp     #'$'
        beq     fail
        cmp     #'*'
        beq     fail
        jsr     hist_full
        bcs     fail
        lda     #1
        sta     v_push
        jsr     hist_write

        lda     v_nx
        ldx     v_ny
        jsr     at_cell
        cmp     #'*'
        lda     #'.'
        beq     :+
        lda     #' '
:       sta     v_ch
        lda     v_nx
        ldx     v_ny
        ldy     v_ch
        jsr     set_cell

        lda     v_bx
        ldx     v_by
        jsr     at_cell
        cmp     #'.'
        lda     #'*'
        beq     :+
        lda     #'$'
:       sta     v_ch
        lda     v_bx
        ldx     v_by
        ldy     v_ch
        jsr     set_cell

        lda     v_nx
        jsr     store_px
        lda     v_ny
        jsr     store_py
        lda     #<(1040)
        ldx     #>(1040)
        jsr     load_u8
        clc
        adc     #1
        jsr     store_moves
        jsr     check_win
        lda     #1
        rts

fail:   lda     #0
        rts

; ---- helpers ----
; A=lo X=hi offset → load byte to A
load_u8:
        clc
        adc     game_ptr
        sta     ptr
        txa
        adc     game_ptr+1
        sta     ptr+1
        ldy     #0
        lda     (ptr),y
        rts

store_px:
        sta     tmp0
        lda     #<(1032)
        clc
        adc     game_ptr
        sta     ptr
        lda     #>(1032)
        adc     game_ptr+1
        sta     ptr+1
        ldy     #0
        lda     tmp0
        sta     (ptr),y
        rts

store_py:
        sta     tmp0
        lda     #<(1036)
        clc
        adc     game_ptr
        sta     ptr
        lda     #>(1036)
        adc     game_ptr+1
        sta     ptr+1
        ldy     #0
        lda     tmp0
        sta     (ptr),y
        rts

store_moves:
        sta     tmp0
        lda     #<(1040)
        clc
        adc     game_ptr
        sta     ptr
        lda     #>(1040)
        adc     game_ptr+1
        sta     ptr+1
        ldy     #0
        lda     tmp0
        sta     (ptr),y
        rts

; A=x X=y → A
at_cell:
        sta     tmp0
        stx     tmp1
        lda     tmp0
        bmi     wall
        lda     tmp1
        bmi     wall
        lda     #<(1024)
        ldx     #>(1024)
        jsr     load_u8
        cmp     tmp0
        beq     wall
        bcc     wall
        lda     #<(1028)
        ldx     #>(1028)
        jsr     load_u8
        cmp     tmp1
        beq     wall
        bcc     wall
        lda     tmp1
        asl     a
        asl     a
        asl     a
        asl     a
        asl     a
        clc
        adc     tmp0
        clc
        adc     game_ptr
        sta     ptr
        lda     game_ptr+1
        adc     #0
        sta     ptr+1
        ldy     #0
        lda     (ptr),y
        rts
wall:   lda     #'#'
        rts

; A=x X=y Y=char
set_cell:
        sta     tmp0
        stx     tmp1
        sty     tmp2
        lda     tmp1
        asl     a
        asl     a
        asl     a
        asl     a
        asl     a
        clc
        adc     tmp0
        clc
        adc     game_ptr
        sta     ptr
        lda     game_ptr+1
        adc     #0
        sta     ptr+1
        ldy     #0
        lda     tmp2
        sta     (ptr),y
        rts

; C=1 if full
hist_full:
        lda     #<(1048)
        ldx     #>(1048)
        jsr     load_u8
        cmp     #255
        rts

hist_write:
        ; ptr = game + 1052 + n*28
        lda     #0
        sta     ptr
        sta     ptr+1
        lda     #<(1048)
        ldx     #>(1048)
        jsr     load_u8
        sta     tmp0
        beq     .hp0
:       clc
        lda     ptr
        adc     #28
        sta     ptr
        lda     ptr+1
        adc     #0
        sta     ptr+1
        dec     tmp0
        bne     :-
.hp0:   clc
        lda     ptr
        adc     game_ptr
        sta     ptr
        lda     ptr+1
        adc     game_ptr+1
        sta     ptr+1
        clc
        lda     ptr
        adc     #<(1052)
        sta     ptr
        lda     ptr+1
        adc     #>(1052)
        sta     ptr+1

        lda     #<(1032)
        ldx     #>(1032)
        jsr     load_u8
        ldy     #0
        sta     (ptr),y
        lda     #<(1036)
        ldx     #>(1036)
        jsr     load_u8
        ldy     #4
        sta     (ptr),y
        lda     v_nx
        ldy     #8
        sta     (ptr),y
        lda     v_ny
        ldy     #12
        sta     (ptr),y
        lda     v_bx
        ldy     #16
        sta     (ptr),y
        lda     v_by
        ldy     #20
        sta     (ptr),y
        lda     v_push
        ldy     #24
        sta     (ptr),y

        lda     #<(1048)
        clc
        adc     game_ptr
        sta     ptr
        lda     #>(1048)
        adc     game_ptr+1
        sta     ptr+1
        ldy     #0
        lda     (ptr),y
        clc
        adc     #1
        sta     (ptr),y
        rts

check_win:
        lda     #<(1044)
        clc
        adc     game_ptr
        sta     ptr
        lda     #>(1044)
        adc     game_ptr+1
        sta     ptr+1
        ldy     #0
        lda     #1
        sta     (ptr),y
        lda     #0
        sta     tmp1
.cy:    lda     #<(1028)
        ldx     #>(1028)
        jsr     load_u8
        cmp     tmp1
        beq     .cwd
        bcc     .cwd
        lda     #0
        sta     tmp0
.cx:    lda     #<(1024)
        ldx     #>(1024)
        jsr     load_u8
        cmp     tmp0
        beq     .cxd
        bcc     .cxd
        lda     tmp0
        ldx     tmp1
        jsr     at_cell
        cmp     #'$'
        bne     .n1
        lda     #<(1044)
        clc
        adc     game_ptr
        sta     ptr
        lda     #>(1044)
        adc     game_ptr+1
        sta     ptr+1
        ldy     #0
        tya
        sta     (ptr),y
.n1:    inc     tmp0
        jmp     .cx
.cxd:   inc     tmp1
        jmp     .cy
.cwd:   rts
