# asm_6502app1 — 6502 / 65C02 推箱子汇编教学

**不强制在本仓库交叉编译**。完整可玩逻辑见 [`../asm_common`](../asm_common)（C 参考）。

## 工具

ca65 / nesasm / VICE 等

## 本目录

| 文件 | 说明 |
|------|------|
| `try_move_6502.s` | 该 ISA 下 `try_move` **教学骨架 / 寄存器约定** |
| 可玩主机 | `../asm_common/host_main.c` + `game.c` |

## 6502 要点

- NES、Apple II、C64 等
- 本仓库已有可运行 NES 版：[`../fcapp1`](../fcapp1)
- 本目录强调**纯汇编教学片段**与寻址方式

```bash
cc -O2 -o sokoban ../asm_common/host_main.c ../asm_common/game.c
```


## 算法对照

推箱 `try_move` 核心步骤（各 ISA 汇编应实现同一语义）：

1. 若已胜利则失败  
2. 计算 `nx,ny`；越界或墙则失败  
3. 若是箱子：检查前方；推箱并记 hist；`moves++`；判胜  
4. 否则走路并记 hist  

键位（C 主机）：WASD / z / r / q。
