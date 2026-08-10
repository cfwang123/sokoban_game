// try_move_aarch64.S — AArch64 教学骨架
// int sk_try_move(SkGame *g, int dx, int dy)
//   x0=g, w1=dx, w2=dy, 返回 w0
// 完整玩法: ../asm_common/game.c

        .text
        .global sk_try_move_aarch64_demo
sk_try_move_aarch64_demo:
        mov     w0, #0
        ret

// 教学: 31 个 64 位通用寄存器、W 寄存器 32 位视图、SP/XZR
