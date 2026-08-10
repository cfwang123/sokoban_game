# try_move_riscv.S — full sk_try_move (RISC-V integer calling convention)
# int sk_try_move(SkGame *g, int dx, int dy)  a0=g a1=dx a2=dy → a0
# Written for RV64I (ld/sd of callees); ints are still 32-bit lw/sw.

        .text
        .globl  sk_try_move
        .type   sk_try_move, @function
sk_try_move:
        addi    sp, sp, -64
        sd      ra, 56(sp)
        sd      s0, 48(sp)
        sd      s1, 40(sp)
        sd      s2, 32(sp)
        sd      s3, 24(sp)
        sd      s4, 16(sp)
        sd      s5, 8(sp)
        sd      s6, 0(sp)

        mv      s0, a0
        mv      s1, a1
        mv      s2, a2

        lw      t0, 1044(s0)
        bnez    t0, .Lfail

        lw      s3, 1032(s0)
        addw    s3, s3, s1
        lw      s4, 1036(s0)
        addw    s4, s4, s2

        mv      a0, s3
        mv      a1, s4
        call    .Lat
        li      t0, 35
        beq     a0, t0, .Lfail
        li      t0, 36
        beq     a0, t0, .Lpush
        li      t0, 42
        beq     a0, t0, .Lpush

        lw      t0, 1048(s0)
        li      t1, 256
        bge     t0, t1, .Lfail
        li      t1, 28
        mul     t1, t0, t1
        add     t1, t1, s0
        addi    t1, t1, 1052
        lw      t2, 1032(s0)
        sw      t2, 0(t1)
        lw      t2, 1036(s0)
        sw      t2, 4(t1)
        sw      zero, 24(t1)
        addiw   t0, t0, 1
        sw      t0, 1048(s0)
        sw      s3, 1032(s0)
        sw      s4, 1036(s0)
        li      a0, 1
        j       .Lret

.Lpush:
        addw    s5, s3, s1
        addw    s6, s4, s2
        mv      a0, s5
        mv      a1, s6
        call    .Lat
        li      t0, 35
        beq     a0, t0, .Lfail
        li      t0, 36
        beq     a0, t0, .Lfail
        li      t0, 42
        beq     a0, t0, .Lfail
        lw      t0, 1048(s0)
        li      t1, 256
        bge     t0, t1, .Lfail

        li      t1, 28
        mul     t1, t0, t1
        add     t1, t1, s0
        addi    t1, t1, 1052
        lw      t2, 1032(s0)
        sw      t2, 0(t1)
        lw      t2, 1036(s0)
        sw      t2, 4(t1)
        sw      s3, 8(t1)
        sw      s4, 12(t1)
        sw      s5, 16(t1)
        sw      s6, 20(t1)
        li      t2, 1
        sw      t2, 24(t1)
        addiw   t0, t0, 1
        sw      t0, 1048(s0)

        mv      a0, s3
        mv      a1, s4
        call    .Lat
        li      t0, 42
        li      a2, 32
        bne     a0, t0, 1f
        li      a2, 46
1:      mv      a0, s3
        mv      a1, s4
        call    .Lset

        mv      a0, s5
        mv      a1, s6
        call    .Lat
        li      t0, 46
        li      a2, 36
        bne     a0, t0, 2f
        li      a2, 42
2:      mv      a0, s5
        mv      a1, s6
        call    .Lset

        sw      s3, 1032(s0)
        sw      s4, 1036(s0)
        lw      t0, 1040(s0)
        addiw   t0, t0, 1
        sw      t0, 1040(s0)
        call    .Lcheck_win
        li      a0, 1
        j       .Lret

.Lfail: li      a0, 0
.Lret:  ld      ra, 56(sp)
        ld      s0, 48(sp)
        ld      s1, 40(sp)
        ld      s2, 32(sp)
        ld      s3, 24(sp)
        ld      s4, 16(sp)
        ld      s5, 8(sp)
        ld      s6, 0(sp)
        addi    sp, sp, 64
        ret

.Lat:   bltz    a0, .Latw
        bltz    a1, .Latw
        lw      t0, 1024(s0)
        bge     a0, t0, .Latw
        lw      t0, 1028(s0)
        bge     a1, t0, .Latw
        slli    t0, a1, 5
        add     t0, t0, a0
        add     t0, t0, s0
        lbu     a0, 0(t0)
        ret
.Latw:  li      a0, 35
        ret

.Lset:  slli    t0, a1, 5
        add     t0, t0, a0
        add     t0, t0, s0
        sb      a2, 0(t0)
        ret

.Lcheck_win:
        li      t0, 1
        sw      t0, 1044(s0)
        li      a1, 0
.Lcy:   lw      t0, 1028(s0)
        bge     a1, t0, .Lcwd
        li      a0, 0
.Lcx:   lw      t0, 1024(s0)
        bge     a0, t0, .Lcxd
        slli    t0, a1, 5
        add     t0, t0, a0
        add     t0, t0, s0
        lbu     t1, 0(t0)
        li      t2, 36
        bne     t1, t2, 1f
        sw      zero, 1044(s0)
1:      addi    a0, a0, 1
        j       .Lcx
.Lcxd:  addi    a1, a1, 1
        j       .Lcy
.Lcwd:  ret
        .size   sk_try_move, .-sk_try_move
