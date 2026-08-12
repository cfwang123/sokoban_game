# asm_mipsapp1 — MIPS32 推箱子汇编教学

> [English](readme.md)


**完整 `sk_try_move` 已实现**，语义对齐 [../asm_common/game.c](../asm_common/game.c)。
不强制在本仓库交叉编译；无对应工具链时用 C 参考主机可玩。

## 工具

o32 ABI; mips-linux-gnu-gcc -c

## 本目录

| 文件 | 说明 |
|------|------|
| `try_move_mips.S` | **完整** `sk_try_move`（与 game.h 布局一致） |
| 可玩主机 | `../asm_common/host_main.c` + `game.c` |
| 自测 | `../asm_common/test_try_move.c` |

## 算法对照

1. 若已胜利则失败
2. 计算 `nx,ny`；越界或墙则失败
3. 若是箱子：检查前方；推箱并记 hist；`moves++`；判胜
4. 否则走路并记 hist

## 可选：链接汇编 `sk_try_move`

`ash
# 汇编 try_move_mips.S → try_move.o 后：
cc -O2 -DSK_USE_ASM_TRY_MOVE -o sokoban_asm \
  ../asm_common/host_main.c ../asm_common/game.c try_move.o -I../asm_common
`

x86-64 本机可直接：`cd ../asm_x64app1 && make asm`

默认 C 参考：

`ash
cc -O2 -o sokoban ../asm_common/host_main.c ../asm_common/game.c -I../asm_common
./sokoban
`

键位：WASD / z / r / q。
