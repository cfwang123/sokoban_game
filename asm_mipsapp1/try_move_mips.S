# try_move_mips.S — MIPS 教学骨架（o32）
# int sk_try_move(SkGame *g, int dx, int dy)
#   a0=g, a1=dx, a2=dy, 返回 v0
# 完整玩法: ../asm_common/game.c

        .text
        .globl sk_try_move_mips_demo
sk_try_move_mips_demo:
        move    $v0, $zero
        jr      $ra
        nop                 # 延迟槽

# 教学: 分支延迟槽、$t/$s 寄存器、HI/LO 乘除
