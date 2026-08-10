; try_move_avr.S — full sk_try_move (AVR / avr-gcc ABI)
;
; int sk_try_move(SkGame *g, int dx, int dy)
;   r25:r24 = g, r23:r22 = dx, r21:r20 = dy → r25:r24 (0/1)
; Mini-level coordinates fit in 8 bits; field offsets match game.h (LE int32).
; avr-gcc -mmcu=atmega328p -c try_move_avr.S

        .global sk_try_move
        .type   sk_try_move, @function

sk_try_move:
        push    r2
        push    r3
        push    r4
        push    r6
        push    r8
        push    r9
        push    r10
        push    r11
        push    r12
        push    r16
        push    r17
        push    r28
        push    r29

        movw    r28, r24                ; Y = g
        mov     r2, r22                 ; dx
        mov     r3, r20                 ; dy

        ldd     r16, Y+1044
        tst     r16
        brne    .Lfail

        ldd     r4, Y+1032
        add     r4, r2                  ; nx
        ldd     r6, Y+1036
        add     r6, r3                  ; ny

        mov     r24, r4
        mov     r22, r6
        rcall   at_cell
        cpi     r24, '#'
        breq    .Lfail
        cpi     r24, '$'
        breq    .Lpush
        cpi     r24, '*'
        breq    .Lpush

        ldd     r16, Y+1048
        cpi     r16, 255
        brsh    .Lfail
        ldi     r24, 0
        rcall   hist_write
        std     Y+1032, r4
        std     Y+1036, r6
        ldi     r24, 1
        clr     r25
        rjmp    .Lret

.Lpush:
        mov     r8, r4
        add     r8, r2                  ; bx
        mov     r9, r6
        add     r9, r3                  ; by
        mov     r24, r8
        mov     r22, r9
        rcall   at_cell
        cpi     r24, '#'
        breq    .Lfail
        cpi     r24, '$'
        breq    .Lfail
        cpi     r24, '*'
        breq    .Lfail
        ldd     r16, Y+1048
        cpi     r16, 255
        brsh    .Lfail

        ldi     r24, 1
        rcall   hist_write
        mov     r24, r4
        mov     r22, r6
        rcall   at_cell
        cpi     r24, '*'
        ldi     r20, '.'
        breq    1f
        ldi     r20, ' '
1:      mov     r24, r4
        mov     r22, r6
        rcall   set_cell
        mov     r24, r8
        mov     r22, r9
        rcall   at_cell
        cpi     r24, '.'
        ldi     r20, '*'
        breq    2f
        ldi     r20, '$'
2:      mov     r24, r8
        mov     r22, r9
        rcall   set_cell
        std     Y+1032, r4
        std     Y+1036, r6
        ldd     r16, Y+1040
        inc     r16
        std     Y+1040, r16
        rcall   check_win
        ldi     r24, 1
        clr     r25
        rjmp    .Lret

.Lfail: clr     r24
        clr     r25
.Lret:  pop     r29
        pop     r28
        pop     r17
        pop     r16
        pop     r12
        pop     r11
        pop     r10
        pop     r9
        pop     r8
        pop     r6
        pop     r4
        pop     r3
        pop     r2
        ret

at_cell:
        tst     r24
        brmi    .wall
        tst     r22
        brmi    .wall
        ldd     r16, Y+1024
        cp      r24, r16
        brsh    .wall
        ldd     r16, Y+1028
        cp      r22, r16
        brsh    .wall
        mov     r30, r22
        clr     r31
        ldi     r16, 5
.m:     lsl     r30
        rol     r31
        dec     r16
        brne    .m
        add     r30, r24
        adc     r31, r1
        add     r30, r28
        adc     r31, r29
        ld      r24, Z
        ret
.wall:  ldi     r24, '#'
        ret

set_cell:
        mov     r30, r22
        clr     r31
        ldi     r16, 5
.ms:    lsl     r30
        rol     r31
        dec     r16
        brne    .ms
        add     r30, r24
        adc     r31, r1
        add     r30, r28
        adc     r31, r29
        st      Z, r20
        ret

; r24 = is_push; uses r4=nx r6=ny r8=bx r9=by when push
hist_write:
        mov     r12, r24
        ldd     r16, Y+1048
        movw    r30, r28
        ldi     r18, lo8(1052)
        ldi     r19, hi8(1052)
        add     r30, r18
        adc     r31, r19
        ldi     r18, 28
        mul     r16, r18
        add     r30, r0
        adc     r31, r1
        clr     r1
        ldd     r18, Y+1032
        st      Z+, r18
        st      Z+, r1
        st      Z+, r1
        st      Z+, r1
        ldd     r18, Y+1036
        st      Z+, r18
        st      Z+, r1
        st      Z+, r1
        st      Z+, r1
        st      Z+, r4
        st      Z+, r1
        st      Z+, r1
        st      Z+, r1
        st      Z+, r6
        st      Z+, r1
        st      Z+, r1
        st      Z+, r1
        st      Z+, r8
        st      Z+, r1
        st      Z+, r1
        st      Z+, r1
        st      Z+, r9
        st      Z+, r1
        st      Z+, r1
        st      Z+, r1
        st      Z+, r12
        st      Z+, r1
        st      Z+, r1
        st      Z+, r1
        inc     r16
        std     Y+1048, r16
        ret

check_win:
        ldi     r16, 1
        std     Y+1044, r16
        clr     r10
.cy:    ldd     r16, Y+1028
        cp      r10, r16
        brsh    .cwd
        clr     r11
.cx:    ldd     r16, Y+1024
        cp      r11, r16
        brsh    .cxd
        mov     r24, r11
        mov     r22, r10
        rcall   at_cell
        cpi     r24, '$'
        brne    1f
        std     Y+1044, r1
1:      inc     r11
        rjmp    .cx
.cxd:   inc     r10
        rjmp    .cy
.cwd:   ret
        .size   sk_try_move, .-sk_try_move
