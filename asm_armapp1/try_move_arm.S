@ try_move_arm.S — full sk_try_move (AAPCS ARM)
@ int sk_try_move(SkGame *g, int dx, int dy)  r0=g r1=dx r2=dy → r0

        .text
        .global sk_try_move
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
        add     r7, r7, r5
        ldr     r8, [r4, #1036]
        add     r8, r8, r6

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
        mov     r1, #28
        mul     r1, r0, r1
        add     r1, r1, #1052
        add     r1, r4, r1
        ldr     r2, [r4, #1032]
        str     r2, [r1]
        ldr     r2, [r4, #1036]
        str     r2, [r1, #4]
        mov     r2, #0
        str     r2, [r1, #24]
        add     r0, r0, #1
        str     r0, [r4, #1048]
        str     r7, [r4, #1032]
        str     r8, [r4, #1036]
        mov     r0, #1
        b       .Lret

.Lpush:
        add     r9, r7, r5
        add     r10, r8, r6
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

        mov     r1, #28
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
        mov     r2, #1
        str     r2, [r1, #24]
        add     r0, r0, #1
        str     r0, [r4, #1048]

        mov     r0, r7
        mov     r1, r8
        bl      .Lat
        cmp     r0, #42
        moveq   r2, #46
        movne   r2, #32
        mov     r0, r7
        mov     r1, r8
        bl      .Lset

        mov     r0, r9
        mov     r1, r10
        bl      .Lat
        cmp     r0, #46
        moveq   r2, #42
        movne   r2, #36
        mov     r0, r9
        mov     r1, r10
        bl      .Lset

        str     r7, [r4, #1032]
        str     r8, [r4, #1036]
        ldr     r0, [r4, #1040]
        add     r0, r0, #1
        str     r0, [r4, #1040]
        bl      .Lcheck_win
        mov     r0, #1
        b       .Lret

.Lfail: mov     r0, #0
.Lret:  pop     {r4-r11, pc}

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
        mov     r2, r1, lsl #5
        add     r2, r2, r0
        ldrb    r0, [r4, r2]
        bx      lr
.Latw:  mov     r0, #35
        bx      lr

.Lset:  mov     r3, r1, lsl #5
        add     r3, r3, r0
        strb    r2, [r4, r3]
        bx      lr

.Lcheck_win:
        mov     r0, #1
        str     r0, [r4, #1044]
        mov     r1, #0
.Lcy:   ldr     r2, [r4, #1028]
        cmp     r1, r2
        bge     .Lcwd
        mov     r0, #0
.Lcx:   ldr     r2, [r4, #1024]
        cmp     r0, r2
        bge     .Lcxd
        mov     r3, r1, lsl #5
        add     r3, r3, r0
        ldrb    r2, [r4, r3]
        cmp     r2, #36
        moveq   r2, #0
        streq   r2, [r4, #1044]
        add     r0, r0, #1
        b       .Lcx
.Lcxd:  add     r1, r1, #1
        b       .Lcy
.Lcwd:  bx      lr
        .size   sk_try_move, .-sk_try_move
