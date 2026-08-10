# asm_common — 汇编教学共用 C 参考实现

各 `asm_*app1` 目录中的 **`.s` / `.S` / `.asm` / `.wat`** 对照本目录算法。

| 文件 | 说明 |
|------|------|
| `game.h` / `game.c` | 完整玩法（reset / try_move / undo / render） |
| `host_main.c` | 终端循环 |

```bash
cd asm_common
cc -O2 -o sokoban host_main.c game.c
./sokoban
```

键位：WASD / z / r / q。
