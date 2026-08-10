# try_move_riscv.S — RISC-V 教学骨架（RV64I / ILP32 类似）
# int sk_try_move(SkGame *g, int dx, int dy)
#   a0=g, a1=dx, a2=dy, 返回 a0
# 完整玩法: ../asm_common/game.c

        .text
        .globl sk_try_move_riscv_demo
sk_try_move_riscv_demo:
        li      a0, 0
        ret

# 教学: 固定 32 寄存器、load-store、无条件码（用分支）
