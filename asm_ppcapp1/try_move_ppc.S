# try_move_ppc.S — full sk_try_move (PowerPC 32-bit)
# int sk_try_move(SkGame *g, int dx, int dy)  r3=g r4=dx r5=dy → r3

        .text
        .globl  sk_try_move
        .type   sk_try_move, @function
sk_try_move:
        mflr    0
        stwu    1, -80(1)
        stw     0, 84(1)
        stw     14, 8(1)
        stw     15, 12(1)
        stw     16, 16(1)
        stw     17, 20(1)
        stw     18, 24(1)
        stw     19, 28(1)
        stw     20, 32(1)

        mr      14, 3
        mr      15, 4
        mr      16, 5

        lwz     3, 1044(14)
        cmpwi   3, 0
        bne     .Lfail

        lwz     17, 1032(14)
        add     17, 17, 15
        lwz     18, 1036(14)
        add     18, 18, 16

        mr      3, 17
        mr      4, 18
        bl      .Lat
        cmpwi   3, 35
        beq     .Lfail
        cmpwi   3, 36
        beq     .Lpush
        cmpwi   3, 42
        beq     .Lpush

        lwz     3, 1048(14)
        cmpwi   3, 256
        bge     .Lfail
        mulli   4, 3, 28
        add     4, 4, 14
        addi    4, 4, 1052
        lwz     5, 1032(14)
        stw     5, 0(4)
        lwz     5, 1036(14)
        stw     5, 4(4)
        li      5, 0
        stw     5, 24(4)
        addi    3, 3, 1
        stw     3, 1048(14)
        stw     17, 1032(14)
        stw     18, 1036(14)
        li      3, 1
        b       .Lret

.Lpush:
        add     19, 17, 15
        add     20, 18, 16
        mr      3, 19
        mr      4, 20
        bl      .Lat
        cmpwi   3, 35
        beq     .Lfail
        cmpwi   3, 36
        beq     .Lfail
        cmpwi   3, 42
        beq     .Lfail
        lwz     3, 1048(14)
        cmpwi   3, 256
        bge     .Lfail

        mulli   4, 3, 28
        add     4, 4, 14
        addi    4, 4, 1052
        lwz     5, 1032(14)
        stw     5, 0(4)
        lwz     5, 1036(14)
        stw     5, 4(4)
        stw     17, 8(4)
        stw     18, 12(4)
        stw     19, 16(4)
        stw     20, 20(4)
        li      5, 1
        stw     5, 24(4)
        addi    3, 3, 1
        stw     3, 1048(14)

        mr      3, 17
        mr      4, 18
        bl      .Lat
        cmpwi   3, 42
        li      5, 46
        beq     1f
        li      5, 32
1:      mr      3, 17
        mr      4, 18
        bl      .Lset

        mr      3, 19
        mr      4, 20
        bl      .Lat
        cmpwi   3, 46
        li      5, 42
        beq     2f
        li      5, 36
2:      mr      3, 19
        mr      4, 20
        bl      .Lset

        stw     17, 1032(14)
        stw     18, 1036(14)
        lwz     3, 1040(14)
        addi    3, 3, 1
        stw     3, 1040(14)
        bl      .Lcheck_win
        li      3, 1
        b       .Lret

.Lfail: li      3, 0
.Lret:  lwz     14, 8(1)
        lwz     15, 12(1)
        lwz     16, 16(1)
        lwz     17, 20(1)
        lwz     18, 24(1)
        lwz     19, 28(1)
        lwz     20, 32(1)
        lwz     0, 84(1)
        mtlr    0
        addi    1, 1, 80
        blr

.Lat:   cmpwi   3, 0
        blt     .Latw
        cmpwi   4, 0
        blt     .Latw
        lwz     5, 1024(14)
        cmpw    3, 5
        bge     .Latw
        lwz     5, 1028(14)
        cmpw    4, 5
        bge     .Latw
        slwi    5, 4, 5
        add     5, 5, 3
        lbzx    3, 14, 5
        blr
.Latw:  li      3, 35
        blr

.Lset:  slwi    6, 4, 5
        add     6, 6, 3
        stbx    5, 14, 6
        blr

.Lcheck_win:
        li      3, 1
        stw     3, 1044(14)
        li      4, 0
.Lcy:   lwz     5, 1028(14)
        cmpw    4, 5
        bge     .Lcwd
        li      3, 0
.Lcx:   lwz     5, 1024(14)
        cmpw    3, 5
        bge     .Lcxd
        slwi    5, 4, 5
        add     5, 5, 3
        lbzx    6, 14, 5
        cmpwi   6, 36
        bne     1f
        li      6, 0
        stw     6, 1044(14)
1:      addi    3, 3, 1
        b       .Lcx
.Lcxd:  addi    4, 4, 1
        b       .Lcy
.Lcwd:  blr
        .size   sk_try_move, .-sk_try_move
