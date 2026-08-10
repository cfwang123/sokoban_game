# try_move_mips.S — full sk_try_move (MIPS o32)
# int sk_try_move(SkGame *g, int dx, int dy)  a0=g a1=dx a2=dy → v0
# Branch delay slots filled with nop (or useful insn where noted).

        .text
        .globl  sk_try_move
        .ent    sk_try_move
sk_try_move:
        addiu   $sp, $sp, -48
        sw      $ra, 44($sp)
        sw      $s0, 40($sp)
        sw      $s1, 36($sp)
        sw      $s2, 32($sp)
        sw      $s3, 28($sp)
        sw      $s4, 24($sp)
        sw      $s5, 20($sp)
        sw      $s6, 16($sp)

        move    $s0, $a0
        move    $s1, $a1
        move    $s2, $a2

        lw      $t0, 1044($s0)
        bne     $t0, $zero, .Lfail
        nop

        lw      $s3, 1032($s0)
        addu    $s3, $s3, $s1
        lw      $s4, 1036($s0)
        addu    $s4, $s4, $s2

        move    $a0, $s3
        jal     .Lat
        move    $a1, $s4

        li      $t0, 35
        beq     $v0, $t0, .Lfail
        nop
        li      $t0, 36
        beq     $v0, $t0, .Lpush
        nop
        li      $t0, 42
        beq     $v0, $t0, .Lpush
        nop

        lw      $t0, 1048($s0)
        li      $t1, 256
        slt     $t2, $t0, $t1
        beq     $t2, $zero, .Lfail
        nop
        li      $t1, 28
        mul     $t1, $t0, $t1
        addu    $t1, $t1, $s0
        addiu   $t1, $t1, 1052
        lw      $t2, 1032($s0)
        sw      $t2, 0($t1)
        lw      $t2, 1036($s0)
        sw      $t2, 4($t1)
        sw      $zero, 24($t1)
        addiu   $t0, $t0, 1
        sw      $t0, 1048($s0)
        sw      $s3, 1032($s0)
        sw      $s4, 1036($s0)
        b       .Lret
        li      $v0, 1

.Lpush:
        addu    $s5, $s3, $s1
        addu    $s6, $s4, $s2
        move    $a0, $s5
        jal     .Lat
        move    $a1, $s6

        li      $t0, 35
        beq     $v0, $t0, .Lfail
        nop
        li      $t0, 36
        beq     $v0, $t0, .Lfail
        nop
        li      $t0, 42
        beq     $v0, $t0, .Lfail
        nop
        lw      $t0, 1048($s0)
        li      $t1, 256
        slt     $t2, $t0, $t1
        beq     $t2, $zero, .Lfail
        nop

        li      $t1, 28
        mul     $t1, $t0, $t1
        addu    $t1, $t1, $s0
        addiu   $t1, $t1, 1052
        lw      $t2, 1032($s0)
        sw      $t2, 0($t1)
        lw      $t2, 1036($s0)
        sw      $t2, 4($t1)
        sw      $s3, 8($t1)
        sw      $s4, 12($t1)
        sw      $s5, 16($t1)
        sw      $s6, 20($t1)
        li      $t2, 1
        sw      $t2, 24($t1)
        addiu   $t0, $t0, 1
        sw      $t0, 1048($s0)

        move    $a0, $s3
        jal     .Lat
        move    $a1, $s4
        li      $a2, 32
        li      $t0, 42
        bne     $v0, $t0, 1f
        nop
        li      $a2, 46
1:      move    $a0, $s3
        jal     .Lset
        move    $a1, $s4

        move    $a0, $s5
        jal     .Lat
        move    $a1, $s6
        li      $a2, 36
        li      $t0, 46
        bne     $v0, $t0, 2f
        nop
        li      $a2, 42
2:      move    $a0, $s5
        jal     .Lset
        move    $a1, $s6

        sw      $s3, 1032($s0)
        sw      $s4, 1036($s0)
        lw      $t0, 1040($s0)
        addiu   $t0, $t0, 1
        sw      $t0, 1040($s0)
        jal     .Lcheck_win
        nop
        b       .Lret
        li      $v0, 1

.Lfail: move    $v0, $zero
.Lret:  lw      $ra, 44($sp)
        lw      $s0, 40($sp)
        lw      $s1, 36($sp)
        lw      $s2, 32($sp)
        lw      $s3, 28($sp)
        lw      $s4, 24($sp)
        lw      $s5, 20($sp)
        lw      $s6, 16($sp)
        addiu   $sp, $sp, 48
        jr      $ra
        nop

.Lat:   bltz    $a0, .Latw
        nop
        bltz    $a1, .Latw
        nop
        lw      $t0, 1024($s0)
        slt     $t1, $a0, $t0
        beq     $t1, $zero, .Latw
        nop
        lw      $t0, 1028($s0)
        slt     $t1, $a1, $t0
        beq     $t1, $zero, .Latw
        nop
        sll     $t0, $a1, 5
        addu    $t0, $t0, $a0
        addu    $t0, $t0, $s0
        jr      $ra
        lbu     $v0, 0($t0)
.Latw:  jr      $ra
        li      $v0, 35

.Lset:  sll     $t0, $a1, 5
        addu    $t0, $t0, $a0
        addu    $t0, $t0, $s0
        jr      $ra
        sb      $a2, 0($t0)

.Lcheck_win:
        li      $t0, 1
        sw      $t0, 1044($s0)
        move    $t1, $zero
.Lcy:   lw      $t0, 1028($s0)
        slt     $t2, $t1, $t0
        beq     $t2, $zero, .Lcwd
        nop
        move    $t3, $zero
.Lcx:   lw      $t0, 1024($s0)
        slt     $t2, $t3, $t0
        beq     $t2, $zero, .Lcxd
        nop
        sll     $t0, $t1, 5
        addu    $t0, $t0, $t3
        addu    $t0, $t0, $s0
        lbu     $t4, 0($t0)
        li      $t5, 36
        bne     $t4, $t5, 1f
        nop
        sw      $zero, 1044($s0)
1:      b       .Lcx
        addiu   $t3, $t3, 1
.Lcxd:  b       .Lcy
        addiu   $t1, $t1, 1
.Lcwd:  jr      $ra
        nop
        .end    sk_try_move
