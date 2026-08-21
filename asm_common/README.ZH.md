# asm_common — 汇编教学共用 C 参考实现

> [English](README.md)


各 `asm_*app1` 目录中的 **`.s` / `.S` / `.asm` / `.wat`** 实现同一套 `sk_try_move` 语义，对照本目录算法。

| 文件 | 说明 |
|------|------|
| `game.h` / `game.c` | 完整玩法（reset / try_move / undo / render） |
| `host_main.c` | 终端循环 |
| `test_try_move.c` | `sk_try_move` 自测（C 或汇编） |

```bash
cd asm_common
cc -O2 -o sokoban host_main.c game.c
./sokoban
cc -O2 -o test_try_move test_try_move.c game.c && ./test_try_move
```

### 用汇编替换 `sk_try_move`

定义 `SK_USE_ASM_TRY_MOVE` 时**不编译** C 版 `sk_try_move`，改为链接各 ISA 导出的同名符号：

```bash
cc -O2 -DSK_USE_ASM_TRY_MOVE -o sokoban_asm \
  host_main.c game.c ../asm_x64app1/try_move.o -I.
```

键位：WASD / z / r / q。
