# try_move_x64.s — 教学：x86-64 System V ABI 版 sk_try_move 骨架
# 完整可玩逻辑见 ../asm_common/game.c；本文件演示寄存器约定与控制流。
#
# ABI: int sk_try_move(SkGame *g, int dx, int dy)
#   rdi = g, esi = dx, edx = dy, 返回 eax
#
# SkGame 布局（与 game.h 一致，教学用偏移）:
#   0: map[32*32]
#   1024: width, height, px, py, moves, won, hist_n ...
#
# 汇编（Linux）:
#   as --64 -o try_move_x64.o try_move_x64.s
# 链接参考（需自行导出完整符号时）:
#   默认请用: cc ../asm_common/host_main.c ../asm_common/game.c

        .text
        .globl  sk_try_move_x64_demo
        .type   sk_try_move_x64_demo, @function
# 演示：仅返回 0（未修改状态）。真正玩法用 C 实现。
sk_try_move_x64_demo:
        xorl    %eax, %eax
        ret
        .size   sk_try_move_x64_demo, .-sk_try_move_x64_demo

# --- 教学伪代码对应 C sk_try_move ---
# if (g->won) return 0;
# nx = g->px + dx; ny = g->py + dy;
# ch = map[ny][nx];
# if (ch == '#') return 0;
# if (ch == '$' || ch == '*') { /* 推箱 */ ... }
# /* 走路 */ g->px = nx; g->py = ny; return 1;
