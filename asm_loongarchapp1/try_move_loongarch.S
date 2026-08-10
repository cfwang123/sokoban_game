# try_move_loongarch.S — full sk_try_move (LoongArch64)
# int sk_try_move(SkGame *g, int dx, int dy)  a0=g a1=dx a2=dy → a0

        .text
        .globl  sk_try_move
        .type   sk_try_move, @function
sk_try_move:
        addi.d  $sp, $sp, -64
        st.d    $ra, $sp, 56
        st.d    $fp, $sp, 48
        st.d    $s0, $sp, 40
        st.d    $s1, $sp, 32
        st.d    $s2, $sp, 24
        st.d    $s3, $sp, 16
        st.d    $s4, $sp, 8
        st.d    $s5, $sp, 0

        move    $fp, $a0
        move    $s0, $a1
        move    $s1, $a2

        ld.w    $t0, $fp, 1044
        bnez    $t0, .Lfail

        ld.w    $s2, $fp, 1032
        add.w   $s2, $s2, $s0
        ld.w    $s3, $fp, 1036
        add.w   $s3, $s3, $s1

        move    $a0, $s2
        move    $a1, $s3
        bl      .Lat
        li.w    $t0, 35
        beq     $a0, $t0, .Lfail
        li.w    $t0, 36
        beq     $a0, $t0, .Lpush
        li.w    $t0, 42
        beq     $a0, $t0, .Lpush

        ld.w    $t0, $fp, 1048
        li.w    $t1, 256
        bge     $t0, $t1, .Lfail
        li.w    $t1, 28
        mul.w   $t1, $t0, $t1
        add.d   $t1, $fp, $t1
        addi.d  $t1, $t1, 1052
        ld.w    $t2, $fp, 1032
        st.w    $t2, $t1, 0
        ld.w    $t2, $fp, 1036
        st.w    $t2, $t1, 4
        st.w    $zero, $t1, 24
        addi.w  $t0, $t0, 1
        st.w    $t0, $fp, 1048
        st.w    $s2, $fp, 1032
        st.w    $s3, $fp, 1036
        li.w    $a0, 1
        b       .Lret

.Lpush:
        add.w   $s4, $s2, $s0
        add.w   $s5, $s3, $s1
        move    $a0, $s4
        move    $a1, $s5
        bl      .Lat
        li.w    $t0, 35
        beq     $a0, $t0, .Lfail
        li.w    $t0, 36
        beq     $a0, $t0, .Lfail
        li.w    $t0, 42
        beq     $a0, $t0, .Lfail
        ld.w    $t0, $fp, 1048
        li.w    $t1, 256
        bge     $t0, $t1, .Lfail

        li.w    $t1, 28
        mul.w   $t1, $t0, $t1
        add.d   $t1, $fp, $t1
        addi.d  $t1, $t1, 1052
        ld.w    $t2, $fp, 1032
        st.w    $t2, $t1, 0
        ld.w    $t2, $fp, 1036
        st.w    $t2, $t1, 4
        st.w    $s2, $t1, 8
        st.w    $s3, $t1, 12
        st.w    $s4, $t1, 16
        st.w    $s5, $t1, 20
        li.w    $t2, 1
        st.w    $t2, $t1, 24
        addi.w  $t0, $t0, 1
        st.w    $t0, $fp, 1048

        move    $a0, $s2
        move    $a1, $s3
        bl      .Lat
        li.w    $t0, 42
        li.w    $a2, 32
        bne     $a0, $t0, 1f
        li.w    $a2, 46
1:      move    $a0, $s2
        move    $a1, $s3
        bl      .Lset

        move    $a0, $s4
        move    $a1, $s5
        bl      .Lat
        li.w    $t0, 46
        li.w    $a2, 36
        bne     $a0, $t0, 2f
        li.w    $a2, 42
2:      move    $a0, $s4
        move    $a1, $s5
        bl      .Lset

        st.w    $s2, $fp, 1032
        st.w    $s3, $fp, 1036
        ld.w    $t0, $fp, 1040
        addi.w  $t0, $t0, 1
        st.w    $t0, $fp, 1040
        bl      .Lcheck_win
        li.w    $a0, 1
        b       .Lret

.Lfail: li.w    $a0, 0
.Lret:  ld.d    $ra, $sp, 56
        ld.d    $fp, $sp, 48
        ld.d    $s0, $sp, 40
        ld.d    $s1, $sp, 32
        ld.d    $s2, $sp, 24
        ld.d    $s3, $sp, 16
        ld.d    $s4, $sp, 8
        ld.d    $s5, $sp, 0
        addi.d  $sp, $sp, 64
        jr      $ra

.Lat:   blt     $a0, $zero, .Latw
        blt     $a1, $zero, .Latw
        ld.w    $t0, $fp, 1024
        bge     $a0, $t0, .Latw
        ld.w    $t0, $fp, 1028
        bge     $a1, $t0, .Latw
        slli.d  $t0, $a1, 5
        add.d   $t0, $t0, $a0
        add.d   $t0, $t0, $fp
        ld.bu   $a0, $t0, 0
        jr      $ra
.Latw:  li.w    $a0, 35
        jr      $ra

.Lset:  slli.d  $t0, $a1, 5
        add.d   $t0, $t0, $a0
        add.d   $t0, $t0, $fp
        st.b    $a2, $t0, 0
        jr      $ra

.Lcheck_win:
        li.w    $t0, 1
        st.w    $t0, $fp, 1044
        move    $a1, $zero
.Lcy:   ld.w    $t0, $fp, 1028
        bge     $a1, $t0, .Lcwd
        move    $a0, $zero
.Lcx:   ld.w    $t0, $fp, 1024
        bge     $a0, $t0, .Lcxd
        slli.d  $t0, $a1, 5
        add.d   $t0, $t0, $a0
        add.d   $t0, $t0, $fp
        ld.bu   $t1, $t0, 0
        li.w    $t2, 36
        bne     $t1, $t2, 1f
        st.w    $zero, $fp, 1044
1:      addi.w  $a0, $a0, 1
        b       .Lcx
.Lcxd:  addi.w  $a1, $a1, 1
        b       .Lcy
.Lcwd:  jr      $ra
        .size   sk_try_move, .-sk_try_move
