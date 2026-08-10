# try_move_ppc.S — PowerPC 教学骨架
# int sk_try_move(SkGame *g, int dx, int dy)
#   r3=g, r4=dx, r5=dy, 返回 r3
# 完整玩法: ../asm_common/game.c

        .text
        .globl sk_try_move_ppc_demo
sk_try_move_ppc_demo:
        li      3, 0
        blr

# 教学: 条件寄存器 CR、链接寄存器 LR、r0 特殊
