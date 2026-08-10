// try_move_aarch64.S — full sk_try_move (AAPCS64)
// int sk_try_move(SkGame *g, int dx, int dy)  x0=g w1=dx w2=dy → w0
// Matches ../asm_common/game.c

        .text
        .global sk_try_move
#ifndef _WIN32
        .type   sk_try_move, %function
#endif
sk_try_move:
        stp     x29, x30, [sp, #-80]!
        mov     x29, sp
        stp     x19, x20, [sp, #16]
        stp     x21, x22, [sp, #32]
        stp     x23, x24, [sp, #48]
        str     x25, [sp, #64]

        mov     x19, x0                 // g
        mov     w20, w1                 // dx
        mov     w21, w2                 // dy

        ldr     w0, [x19, #1044]
        cbnz    w0, .Lfail

        ldr     w22, [x19, #1032]
        add     w22, w22, w20           // nx
        ldr     w23, [x19, #1036]
        add     w23, w23, w21           // ny

        mov     w0, w22
        mov     w1, w23
        bl      .Lat
        cmp     w0, #35
        b.eq    .Lfail
        cmp     w0, #36
        b.eq    .Lpush
        cmp     w0, #42
        b.eq    .Lpush

        ldr     w0, [x19, #1048]
        cmp     w0, #256
        b.ge    .Lfail
        mov     w1, #28
        mul     w1, w0, w1
        add     x2, x19, #1052
        add     x2, x2, w1, uxtw
        ldr     w3, [x19, #1032]
        str     w3, [x2]
        ldr     w3, [x19, #1036]
        str     w3, [x2, #4]
        str     wzr, [x2, #24]
        add     w0, w0, #1
        str     w0, [x19, #1048]
        str     w22, [x19, #1032]
        str     w23, [x19, #1036]
        mov     w0, #1
        b       .Lret

.Lpush:
        add     w24, w22, w20           // bx
        add     w25, w23, w21           // by
        mov     w0, w24
        mov     w1, w25
        bl      .Lat
        cmp     w0, #35
        b.eq    .Lfail
        cmp     w0, #36
        b.eq    .Lfail
        cmp     w0, #42
        b.eq    .Lfail
        ldr     w0, [x19, #1048]
        cmp     w0, #256
        b.ge    .Lfail

        mov     w1, #28
        mul     w1, w0, w1
        add     x2, x19, #1052
        add     x2, x2, w1, uxtw
        ldr     w3, [x19, #1032]
        str     w3, [x2]
        ldr     w3, [x19, #1036]
        str     w3, [x2, #4]
        str     w22, [x2, #8]
        str     w23, [x2, #12]
        str     w24, [x2, #16]
        str     w25, [x2, #20]
        mov     w3, #1
        str     w3, [x2, #24]
        add     w0, w0, #1
        str     w0, [x19, #1048]

        mov     w0, w22
        mov     w1, w23
        bl      .Lat
        cmp     w0, #42
        mov     w2, #46
        mov     w3, #32
        csel    w2, w2, w3, eq
        mov     w0, w22
        mov     w1, w23
        bl      .Lset

        mov     w0, w24
        mov     w1, w25
        bl      .Lat
        cmp     w0, #46
        mov     w2, #42
        mov     w3, #36
        csel    w2, w2, w3, eq
        mov     w0, w24
        mov     w1, w25
        bl      .Lset

        str     w22, [x19, #1032]
        str     w23, [x19, #1036]
        ldr     w0, [x19, #1040]
        add     w0, w0, #1
        str     w0, [x19, #1040]
        bl      .Lcheck_win
        mov     w0, #1
        b       .Lret

.Lfail:
        mov     w0, #0
.Lret:
        ldr     x25, [sp, #64]
        ldp     x19, x20, [sp, #16]
        ldp     x21, x22, [sp, #32]
        ldp     x23, x24, [sp, #48]
        ldp     x29, x30, [sp], #80
        ret

.Lat:   // w0=x w1=y  x19=g → w0
        tbnz    w0, #31, .Latw
        tbnz    w1, #31, .Latw
        ldr     w2, [x19, #1024]
        cmp     w0, w2
        b.ge    .Latw
        ldr     w2, [x19, #1028]
        cmp     w1, w2
        b.ge    .Latw
        add     x2, x19, w0, uxtw
        add     x2, x2, w1, uxtw #5
        ldrb    w0, [x2]
        ret
.Latw:  mov     w0, #35
        ret

.Lset:  // w0=x w1=y w2=c
        add     x3, x19, w0, uxtw
        add     x3, x3, w1, uxtw #5
        strb    w2, [x3]
        ret

.Lcheck_win:
        mov     w0, #1
        str     w0, [x19, #1044]
        mov     w1, wzr
.Lcy:   ldr     w2, [x19, #1028]
        cmp     w1, w2
        b.ge    .Lcwd
        mov     w0, wzr
.Lcx:   ldr     w2, [x19, #1024]
        cmp     w0, w2
        b.ge    .Lcxd
        add     x3, x19, w0, uxtw
        add     x3, x3, w1, uxtw #5
        ldrb    w2, [x3]
        cmp     w2, #36
        b.ne    1f
        str     wzr, [x19, #1044]
1:      add     w0, w0, #1
        b       .Lcx
.Lcxd:  add     w1, w1, #1
        b       .Lcy
.Lcwd:  ret
