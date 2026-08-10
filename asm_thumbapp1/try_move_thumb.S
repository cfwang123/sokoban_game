@ try_move_thumb.S — full sk_try_move (Thumb-2 unified syntax)
@ int sk_try_move(SkGame *g, int dx, int dy)  r0=g r1=dx r2=dy → r0

        .syntax unified
        .thumb
        .text
        .global sk_try_move
        .thumb_func
        .type   sk_try_move, %function
sk_try_move:
        push    {r4-r11, lr}
        mov     r4, r0
        mov     r5, r1
        mov     r6, r2

        ldr     r0, [r4, #1044]
        cmp     r0, #0
        bne     .Lfail

        ldr     r7, [r4, #1032]
        adds    r7, r7, r5
        ldr     r8, [r4, #1036]
        adds    r8, r8, r6

        mov     r0, r7
        mov     r1, r8
        bl      .Lat
        cmp     r0, #35
        beq     .Lfail
        cmp     r0, #36
        beq     .Lpush
        cmp     r0, #42
        beq     .Lpush

        ldr     r0, [r4, #1048]
        cmp     r0, #256
        bge     .Lfail
        movs    r1, #28
        mul     r1, r0, r1
        add     r1, r1, #1052
        add     r1, r4, r1
        ldr     r2, [r4, #1032]
        str     r2, [r1]
        ldr     r2, [r4, #1036]
        str     r2, [r1, #4]
        movs    r2, #0
        str     r2, [r1, #24]
        adds    r0, #1
        str     r0, [r4, #1048]
        str     r7, [r4, #1032]
        str     r8, [r4, #1036]
        movs    r0, #1
        b       .Lret

.Lpush:
        adds    r9, r7, r5
        adds    r10, r8, r6
        mov     r0, r9
        mov     r1, r10
        bl      .Lat
        cmp     r0, #35
        beq     .Lfail
        cmp     r0, #36
        beq     .Lfail
        cmp     r0, #42
        beq     .Lfail
        ldr     r0, [r4, #1048]
        cmp     r0, #256
        bge     .Lfail

        movs    r1, #28
        mul     r1, r0, r1
        add     r1, r1, #1052
        add     r1, r4, r1
        ldr     r2, [r4, #1032]
        str     r2, [r1]
        ldr     r2, [r4, #1036]
        str     r2, [r1, #4]
        str     r7, [r1, #8]
        str     r8, [r1, #12]
        str     r9, [r1, #16]
        str     r10, [r1, #20]
        movs    r2, #1
        str     r2, [r1, #24]
        adds    r0, #1
        str     r0, [r4, #1048]

        mov     r0, r7
        mov     r1, r8
        bl      .Lat
        cmp     r0, #42
        ite     eq
        moveq   r2, #46
        movne   r2, #32
        mov     r0, r7
        mov     r1, r8
        bl      .Lset

        mov     r0, r9
        mov     r1, r10
        bl      .Lat
        cmp     r0, #46
        ite     eq
        moveq   r2, #42
        movne   r2, #36
        mov     r0, r9
        mov     r1, r10
        bl      .Lset

        str     r7, [r4, #1032]
        str     r8, [r4, #1036]
        ldr     r0, [r4, #1040]
        adds    r0, #1
        str     r0, [r4, #1040]
        bl      .Lcheck_win
        movs    r0, #1
        b       .Lret

.Lfail: movs    r0, #0
.Lret:  pop     {r4-r11, pc}

        .thumb_func
.Lat:   cmp     r0, #0
        blt     .Latw
        cmp     r1, #0
        blt     .Latw
        ldr     r2, [r4, #1024]
        cmp     r0, r2
        bge     .Latw
        ldr     r2, [r4, #1028]
        cmp     r1, r2
        bge     .Latw
        lsls    r2, r1, #5
        adds    r2, r2, r0
        ldrb    r0, [r4, r2]
        bx      lr
.Latw:  movs    r0, #35
        bx      lr

        .thumb_func
.Lset:  lsls    r3, r1, #5
        adds    r3, r3, r0
        strb    r2, [r4, r3]
        bx      lr

        .thumb_func
.Lcheck_win:
        movs    r0, #1
        str     r0, [r4, #1044]
        movs    r1, #0
.Lcy:   ldr     r2, [r4, #1028]
        cmp     r1, r2
        bge     .Lcwd
        movs    r0, #0
.Lcx:   ldr     r2, [r4, #1024]
        cmp     r0, r2
        bge     .Lcxd
        lsls    r3, r1, #5
        adds    r3, r3, r0
        ldrb    r2, [r4, r3]
        cmp     r2, #36
        bne     1f
        movs    r2, #0
        str     r2, [r4, #1044]
1:      adds    r0, #1
        b       .Lcx
.Lcxd:  adds    r1, #1
        b       .Lcy
.Lcwd:  bx      lr
        .size   sk_try_move, .-sk_try_move
